from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.queue import claim_next_job

DEFAULT_POSTGRES_URL = (
    "postgresql+psycopg://aerovision:change-me-postgres-password@localhost:5432/aerovision"
)
pytestmark = pytest.mark.postgres


@pytest.fixture()
def postgres_queue_factory() -> sessionmaker[Session]:
    base_url = os.getenv("POSTGRES_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if base_url is None:
        base_url = DEFAULT_POSTGRES_URL
    base_url = base_url.replace("@postgres:", "@localhost:")
    admin_engine = create_engine(
        base_url,
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 2},
    )
    try:
        with admin_engine.connect() as connection:
            connection.execute(text("select 1"))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL unavailable for queue integration tests: {exc}")

    schema = f"queue_test_{uuid4().hex}"
    with admin_engine.begin() as connection:
        connection.execute(text(f'create schema "{schema}"'))

    test_url = _url_with_search_path(base_url, schema)
    test_engine = create_engine(test_url, pool_pre_ping=True, connect_args={"connect_timeout": 2})
    try:
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    create table processing_jobs (
                        id uuid primary key,
                        status varchar(20) not null,
                        progress_percent integer not null default 0,
                        last_heartbeat_at timestamptz null,
                        locked_by varchar(255) null,
                        locked_at timestamptz null,
                        retry_count integer not null default 0,
                        started_at timestamptz null,
                        completed_at timestamptz null,
                        deleted_at timestamptz null,
                        created_at timestamptz not null,
                        updated_at timestamptz not null,
                        error_message text null
                    )
                    """
                )
            )
        yield sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    finally:
        test_engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'drop schema if exists "{schema}" cascade'))
        admin_engine.dispose()


def test_two_postgres_workers_do_not_claim_same_job(
    postgres_queue_factory: sessionmaker[Session],
) -> None:
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    job_id = _insert_job(postgres_queue_factory, created_at=now)
    barrier = Barrier(2)

    def claim(worker_id: str):
        barrier.wait(timeout=5)
        return claim_next_job(postgres_queue_factory, worker_id=worker_id, now=now)

    with ThreadPoolExecutor(max_workers=2) as executor:
        claims = list(executor.map(claim, ["worker-a", "worker-b"]))

    claimed_ids = [claimed.id for claimed in claims if claimed is not None]
    assert claimed_ids == [job_id]
    assert claims.count(None) == 1


def test_postgres_workers_claim_distinct_queued_jobs(
    postgres_queue_factory: sessionmaker[Session],
) -> None:
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    first_id = _insert_job(postgres_queue_factory, created_at=now - timedelta(minutes=2))
    second_id = _insert_job(postgres_queue_factory, created_at=now - timedelta(minutes=1))

    first_claim = claim_next_job(postgres_queue_factory, worker_id="worker-a", now=now)
    second_claim = claim_next_job(
        postgres_queue_factory,
        worker_id="worker-b",
        now=now + timedelta(seconds=1),
    )

    assert first_claim is not None
    assert second_claim is not None
    assert {first_claim.id, second_claim.id} == {first_id, second_id}


def test_postgres_claim_transaction_commits_before_processing(
    postgres_queue_factory: sessionmaker[Session],
) -> None:
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    job_id = _insert_job(postgres_queue_factory, created_at=now)

    claimed = claim_next_job(postgres_queue_factory, worker_id="worker-a", now=now)

    assert claimed is not None
    with postgres_queue_factory.begin() as session:
        locked_id = session.execute(
            text("select id from processing_jobs where id = :job_id for update nowait"),
            {"job_id": job_id},
        ).scalar_one()
    assert locked_id == job_id


def _insert_job(factory: sessionmaker[Session], *, created_at: datetime):
    job_id = uuid4()
    with factory.begin() as session:
        session.execute(
            text(
                """
                insert into processing_jobs (
                    id, status, progress_percent, retry_count, created_at, updated_at
                )
                values (:id, 'queued', 0, 0, :created_at, :created_at)
                """
            ),
            {"id": job_id, "created_at": created_at},
        )
    return job_id


def _url_with_search_path(base_url: str, schema: str) -> str:
    parts = urlsplit(base_url)
    separator = "&" if parts.query else ""
    query = f"{parts.query}{separator}options={quote(f'-csearch_path={schema}')}"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))
