from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.queue import (
    PLACEHOLDER_PROCESSING_ERROR,
    claim_next_job,
    fail_processing_job,
    recover_stale_jobs,
    update_job_heartbeat,
)


def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                create table processing_jobs (
                    id char(32) primary key,
                    status varchar(20) not null,
                    progress_percent integer not null default 0,
                    last_heartbeat_at timestamp null,
                    locked_by varchar(255) null,
                    locked_at timestamp null,
                    retry_count integer not null default 0,
                    started_at timestamp null,
                    completed_at timestamp null,
                    deleted_at timestamp null,
                    created_at timestamp not null,
                    updated_at timestamp not null,
                    error_message text null
                )
                """
            )
        )
    return factory


def insert_job(
    factory: sessionmaker[Session],
    *,
    job_id: str | None = None,
    status: str = "queued",
    created_at: datetime,
    retry_count: int = 0,
    last_heartbeat_at: datetime | None = None,
    locked_by: str | None = None,
    locked_at: datetime | None = None,
    started_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> str:
    job_id = job_id or uuid4().hex
    with factory.begin() as session:
        session.execute(
            text(
                """
                insert into processing_jobs (
                    id, status, progress_percent, last_heartbeat_at, locked_by,
                    locked_at, retry_count, started_at, completed_at, deleted_at,
                    created_at, updated_at, error_message
                )
                values (
                    :id, :status, 0, :last_heartbeat_at, :locked_by,
                    :locked_at, :retry_count, :started_at, null, :deleted_at,
                    :created_at, :created_at, :error_message
                )
                """
            ),
            {
                "id": job_id,
                "status": status,
                "last_heartbeat_at": last_heartbeat_at,
                "locked_by": locked_by,
                "locked_at": locked_at,
                "retry_count": retry_count,
                "started_at": started_at,
                "deleted_at": deleted_at,
                "created_at": created_at,
                "error_message": "previous safe error",
            },
        )
    return job_id


def fetch_job(factory: sessionmaker[Session], job_id: str) -> dict[str, object]:
    with factory() as session:
        row = (
            session.execute(
                text("select * from processing_jobs where id = :id"),
                {"id": job_id},
            )
            .mappings()
            .one()
        )
    job = dict(row)
    for key in (
        "last_heartbeat_at",
        "locked_at",
        "started_at",
        "completed_at",
        "deleted_at",
        "created_at",
        "updated_at",
    ):
        value = job.get(key)
        if isinstance(value, str):
            job[key] = datetime.fromisoformat(value)
    return job


def test_claim_next_job_claims_oldest_queued_job_and_sets_required_fields() -> None:
    factory = session_factory()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    older_id = insert_job(factory, created_at=now - timedelta(minutes=2))
    newer_id = insert_job(factory, created_at=now - timedelta(minutes=1))

    claimed = claim_next_job(factory, worker_id="worker-a", now=now)

    assert claimed is not None
    assert claimed.id == older_id
    older = fetch_job(factory, older_id)
    newer = fetch_job(factory, newer_id)
    assert older["status"] == "processing"
    assert older["locked_by"] == "worker-a"
    assert older["locked_at"] == now
    assert older["started_at"] == now
    assert older["last_heartbeat_at"] == now
    assert newer["status"] == "queued"


def test_claim_next_job_returns_none_when_queue_empty() -> None:
    factory = session_factory()

    claimed = claim_next_job(factory, worker_id="worker-a")

    assert claimed is None


def test_update_job_heartbeat_updates_only_matching_processing_owner() -> None:
    factory = session_factory()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    job_id = insert_job(
        factory,
        status="processing",
        created_at=now,
        locked_by="worker-a",
        locked_at=now,
        started_at=now,
    )

    owner_updated = update_job_heartbeat(
        factory,
        job_id=job_id,
        worker_id="worker-a",
        progress_percent=50,
        now=now + timedelta(seconds=5),
    )
    wrong_owner_updated = update_job_heartbeat(
        factory,
        job_id=job_id,
        worker_id="worker-b",
        progress_percent=75,
        now=now + timedelta(seconds=10),
    )

    job = fetch_job(factory, job_id)
    assert owner_updated is True
    assert wrong_owner_updated is False
    assert job["progress_percent"] == 50
    assert job["last_heartbeat_at"] == now + timedelta(seconds=5)


def test_update_job_heartbeat_rejects_progress_outside_range() -> None:
    factory = session_factory()

    try:
        update_job_heartbeat(
            factory,
            job_id=uuid4().hex,
            worker_id="worker-a",
            progress_percent=101,
        )
    except ValueError as exc:
        assert "progress_percent must be between 0 and 100" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("invalid progress should fail")


def test_recover_stale_jobs_requeues_below_retry_limit_and_ignores_soft_deleted() -> None:
    factory = session_factory()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    stale_id = insert_job(
        factory,
        status="processing",
        created_at=now - timedelta(hours=1),
        retry_count=1,
        last_heartbeat_at=now - timedelta(minutes=20),
        locked_by="worker-a",
        locked_at=now - timedelta(minutes=20),
        started_at=now - timedelta(minutes=20),
    )
    deleted_id = insert_job(
        factory,
        status="processing",
        created_at=now - timedelta(hours=1),
        retry_count=1,
        last_heartbeat_at=now - timedelta(minutes=20),
        locked_by="worker-a",
        locked_at=now - timedelta(minutes=20),
        started_at=now - timedelta(minutes=20),
        deleted_at=now - timedelta(minutes=5),
    )

    summary = recover_stale_jobs(
        factory,
        stale_before=now - timedelta(minutes=10),
        max_retries=2,
        now=now,
    )

    stale = fetch_job(factory, stale_id)
    deleted = fetch_job(factory, deleted_id)
    assert summary.requeued == 1
    assert summary.failed == 0
    assert stale["status"] == "queued"
    assert stale["retry_count"] == 2
    assert stale["locked_by"] is None
    assert stale["locked_at"] is None
    assert stale["started_at"] is None
    assert stale["last_heartbeat_at"] is None
    assert stale["error_message"] is None
    assert deleted["status"] == "processing"
    assert deleted["retry_count"] == 1


def test_recover_stale_jobs_fails_at_retry_limit_and_handles_missing_heartbeat() -> None:
    factory = session_factory()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    stale_id = insert_job(
        factory,
        status="processing",
        created_at=now - timedelta(hours=1),
        retry_count=2,
        last_heartbeat_at=None,
        locked_by="worker-a",
        locked_at=now - timedelta(minutes=20),
        started_at=now - timedelta(minutes=20),
    )

    summary = recover_stale_jobs(
        factory,
        stale_before=now - timedelta(minutes=10),
        max_retries=2,
        now=now,
    )

    stale = fetch_job(factory, stale_id)
    assert summary.requeued == 0
    assert summary.failed == 1
    assert stale["status"] == "failed"
    assert stale["error_message"] == "Worker heartbeat timed out"
    assert stale["completed_at"] == now
    assert stale["locked_by"] is None
    assert stale["locked_at"] is None


def test_fail_processing_job_only_updates_matching_owner() -> None:
    factory = session_factory()
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    job_id = insert_job(
        factory,
        status="processing",
        created_at=now,
        locked_by="worker-a",
        locked_at=now,
        started_at=now,
    )

    wrong_owner_failed = fail_processing_job(
        factory,
        job_id=job_id,
        worker_id="worker-b",
        error_message=PLACEHOLDER_PROCESSING_ERROR,
        now=now + timedelta(seconds=1),
    )
    owner_failed = fail_processing_job(
        factory,
        job_id=job_id,
        worker_id="worker-a",
        error_message=PLACEHOLDER_PROCESSING_ERROR,
        now=now + timedelta(seconds=2),
    )

    job = fetch_job(factory, job_id)
    assert wrong_owner_failed is False
    assert owner_failed is True
    assert job["status"] == "failed"
    assert job["error_message"] == PLACEHOLDER_PROCESSING_ERROR
    assert job["completed_at"] == now + timedelta(seconds=2)
    assert job["locked_by"] is None
