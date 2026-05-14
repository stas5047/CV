from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

PLACEHOLDER_PROCESSING_ERROR = "Processing not implemented in this phase"
STALE_TIMEOUT_ERROR = "Worker heartbeat timed out"


@dataclass(frozen=True)
class ClaimedJob:
    id: Any
    media_type: str


@dataclass(frozen=True)
class RecoverySummary:
    requeued: int = 0
    failed: int = 0


def utc_now() -> datetime:
    return datetime.now(UTC)


def claim_next_job(
    session_factory: sessionmaker[Session],
    *,
    worker_id: str,
    now: datetime | None = None,
) -> ClaimedJob | None:
    claimed_at = now or utc_now()
    with session_factory.begin() as session:
        queued_job = _select_next_queued_job(session)
        if queued_job is None:
            return None
        job_id = queued_job["id"]
        result = session.execute(
            text(
                """
                update processing_jobs
                set status = 'processing',
                    locked_by = :worker_id,
                    locked_at = :claimed_at,
                    started_at = :claimed_at,
                    last_heartbeat_at = :claimed_at,
                    updated_at = :claimed_at,
                    error_message = null
                where id = :job_id
                  and status = 'queued'
                  and deleted_at is null
                """
            ),
            {
                "worker_id": worker_id,
                "claimed_at": claimed_at,
                "job_id": job_id,
            },
        )
        if result.rowcount != 1:
            return None
        return ClaimedJob(id=job_id, media_type=str(queued_job["media_type"]))


def update_job_heartbeat(
    session_factory: sessionmaker[Session],
    *,
    job_id: Any,
    worker_id: str,
    progress_percent: int,
    now: datetime | None = None,
) -> bool:
    if progress_percent < 0 or progress_percent > 100:
        raise ValueError("progress_percent must be between 0 and 100")

    heartbeat_at = now or utc_now()
    with session_factory.begin() as session:
        result = session.execute(
            text(
                """
                update processing_jobs
                set progress_percent = :progress_percent,
                    last_heartbeat_at = :heartbeat_at,
                    updated_at = :heartbeat_at
                where id = :job_id
                  and locked_by = :worker_id
                  and status = 'processing'
                  and deleted_at is null
                """
            ),
            {
                "job_id": job_id,
                "worker_id": worker_id,
                "progress_percent": progress_percent,
                "heartbeat_at": heartbeat_at,
            },
        )
    return result.rowcount == 1


def recover_stale_jobs(
    session_factory: sessionmaker[Session],
    *,
    stale_before: datetime,
    max_retries: int,
    now: datetime | None = None,
) -> RecoverySummary:
    recovered_at = now or utc_now()
    requeued = 0
    failed = 0
    with session_factory.begin() as session:
        rows = (
            session.execute(
                text(
                    """
                    select id, retry_count
                    from processing_jobs
                    where status = 'processing'
                      and deleted_at is null
                      and (
                        last_heartbeat_at is null
                        or last_heartbeat_at < :stale_before
                      )
                    order by created_at asc
                    """
                ),
                {"stale_before": stale_before},
            )
            .mappings()
            .all()
        )
        for row in rows:
            if row["retry_count"] < max_retries:
                requeued += _requeue_stale_job(
                    session,
                    job_id=row["id"],
                    recovered_at=recovered_at,
                )
            else:
                failed += _fail_stale_job(
                    session,
                    job_id=row["id"],
                    recovered_at=recovered_at,
                )
    return RecoverySummary(requeued=requeued, failed=failed)


def fail_processing_job(
    session_factory: sessionmaker[Session],
    *,
    job_id: Any,
    worker_id: str,
    error_message: str,
    now: datetime | None = None,
) -> bool:
    failed_at = now or utc_now()
    with session_factory.begin() as session:
        result = session.execute(
            text(
                """
                update processing_jobs
                set status = 'failed',
                    error_message = :error_message,
                    completed_at = :failed_at,
                    locked_by = null,
                    locked_at = null,
                    last_heartbeat_at = :failed_at,
                    updated_at = :failed_at
                where id = :job_id
                  and locked_by = :worker_id
                  and status = 'processing'
                  and deleted_at is null
                """
            ),
            {
                "job_id": job_id,
                "worker_id": worker_id,
                "error_message": error_message,
                "failed_at": failed_at,
            },
        )
    return result.rowcount == 1


def _select_next_queued_job(session: Session) -> dict[str, Any] | None:
    statement = """
        select pj.id, mf.media_type
        from processing_jobs pj
        join media_files mf on mf.id = pj.media_file_id
        where pj.status = 'queued'
          and pj.deleted_at is null
          and mf.deleted_at is null
          and mf.media_type in ('image', 'video')
        order by pj.created_at asc
        limit 1
    """
    if session.get_bind().dialect.name == "postgresql":
        statement = f"{statement} for update skip locked"
    row = session.execute(text(statement)).mappings().one_or_none()
    return None if row is None else dict(row)


def _requeue_stale_job(session: Session, *, job_id: Any, recovered_at: datetime) -> int:
    result = session.execute(
        text(
            """
            update processing_jobs
            set status = 'queued',
                retry_count = retry_count + 1,
                locked_by = null,
                locked_at = null,
                started_at = null,
                last_heartbeat_at = null,
                error_message = null,
                updated_at = :recovered_at
            where id = :job_id
              and status = 'processing'
              and deleted_at is null
            """
        ),
        {"job_id": job_id, "recovered_at": recovered_at},
    )
    return int(result.rowcount or 0)


def _fail_stale_job(session: Session, *, job_id: Any, recovered_at: datetime) -> int:
    result = session.execute(
        text(
            """
            update processing_jobs
            set status = 'failed',
                error_message = :error_message,
                completed_at = :recovered_at,
                locked_by = null,
                locked_at = null,
                updated_at = :recovered_at
            where id = :job_id
              and status = 'processing'
              and deleted_at is null
            """
        ),
        {
            "job_id": job_id,
            "error_message": STALE_TIMEOUT_ERROR,
            "recovered_at": recovered_at,
        },
    )
    return int(result.rowcount or 0)
