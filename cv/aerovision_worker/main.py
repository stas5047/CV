from __future__ import annotations

import argparse
import logging
import os
import socket
import time
from collections.abc import Callable
from datetime import timedelta
from uuid import uuid4

from aerovision_worker.database import check_database, create_session_factory, wait_for_database
from aerovision_worker.device import DeviceSelection, select_device
from aerovision_worker.image_processing import process_image_job
from aerovision_worker.logging import configure_logging
from aerovision_worker.model_runtime import ModelLoadingError, ModelRuntime
from aerovision_worker.queue import (
    claim_next_job,
    fail_processing_job,
    recover_stale_jobs,
    utc_now,
)
from aerovision_worker.settings import WorkerSettings, get_settings
from aerovision_worker.video_processing import process_video_job

LOGGER = logging.getLogger("aerovision_worker")


def run_startup_checks(
    settings: WorkerSettings,
    *,
    check_database: Callable[[], None],
    cuda_available: Callable[[], bool] | None = None,
) -> DeviceSelection:
    LOGGER.info("worker_start settings=%s", settings.safe_log_payload())
    device = select_device(settings.cv_device, cuda_available=cuda_available)
    LOGGER.info(
        "device_selected requested_device=%s selected_device=%s",
        device.requested,
        device.selected,
    )
    check_database()
    LOGGER.info("database_ready")
    return device


def build_worker_id() -> str:
    return f"{socket.gethostname()}-{os.getpid()}-{uuid4().hex[:12]}"


def run_poll_iteration(
    settings: WorkerSettings,
    session_factory,
    *,
    worker_id: str,
    model_runtime: ModelRuntime | None = None,
) -> bool:
    now = utc_now()
    summary = recover_stale_jobs(
        session_factory,
        stale_before=now - timedelta(minutes=settings.stale_job_minutes),
        max_retries=settings.max_retries,
        now=now,
    )
    if summary.requeued or summary.failed:
        LOGGER.info(
            "stale_jobs_recovered requeued=%s failed=%s",
            summary.requeued,
            summary.failed,
        )

    claimed = claim_next_job(session_factory, worker_id=worker_id, now=utc_now())
    if claimed is None:
        return False

    LOGGER.info(
        "job_claimed job_id=%s media_type=%s worker_id=%s",
        claimed.id,
        claimed.media_type,
        worker_id,
    )
    if model_runtime is not None:
        try:
            loaded_model = model_runtime.load_for_job(session_factory, job_id=claimed.id)
        except ModelLoadingError as exc:
            failed = fail_processing_job(
                session_factory,
                job_id=claimed.id,
                worker_id=worker_id,
                error_message=str(exc),
                now=utc_now(),
            )
            if failed:
                LOGGER.info("job_failed_model_load job_id=%s worker_id=%s", claimed.id, worker_id)
            return True
        if claimed.media_type == "image":
            process_image_job(
                settings,
                session_factory,
                job_id=claimed.id,
                worker_id=worker_id,
                loaded_model=loaded_model,
            )
        elif claimed.media_type == "video":
            process_video_job(
                settings,
                session_factory,
                job_id=claimed.id,
                worker_id=worker_id,
                loaded_model=loaded_model,
            )
        else:
            fail_processing_job(
                session_factory,
                job_id=claimed.id,
                worker_id=worker_id,
                error_message="Claimed job media type is unsupported",
                now=utc_now(),
            )
    return True


def run_worker(*, check_once: bool = False) -> None:
    configure_logging()
    settings = get_settings()
    session_factory = create_session_factory(settings.database_url)
    worker_id = build_worker_id()
    device = run_startup_checks(
        settings,
        check_database=lambda: wait_for_database(
            lambda: check_database(session_factory),
            attempts=30,
            delay_seconds=1,
        ),
    )
    if check_once:
        return

    LOGGER.info("worker_polling_started worker_id=%s", worker_id)
    model_runtime = ModelRuntime(settings=settings, selected_device=device.selected)
    try:
        while True:
            claimed = run_poll_iteration(
                settings,
                session_factory,
                worker_id=worker_id,
                model_runtime=model_runtime,
            )
            if not claimed:
                time.sleep(settings.poll_interval_seconds)
    except KeyboardInterrupt:
        LOGGER.info("worker_shutdown_requested worker_id=%s", worker_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="AeroVision CV worker")
    parser.add_argument(
        "--check-once",
        action="store_true",
        help="Run startup smoke checks and exit",
    )
    args = parser.parse_args()
    run_worker(check_once=args.check_once)


if __name__ == "__main__":
    main()
