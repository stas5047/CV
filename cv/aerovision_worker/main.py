from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable

from aerovision_worker.database import check_database, create_session_factory, wait_for_database
from aerovision_worker.device import select_device
from aerovision_worker.logging import configure_logging
from aerovision_worker.settings import WorkerSettings, get_settings

LOGGER = logging.getLogger("aerovision_worker")


def run_startup_checks(
    settings: WorkerSettings,
    *,
    check_database: Callable[[], None],
    cuda_available: Callable[[], bool] | None = None,
) -> None:
    LOGGER.info("worker_start settings=%s", settings.safe_log_payload())
    device = select_device(settings.cv_device, cuda_available=cuda_available)
    LOGGER.info(
        "device_selected requested_device=%s selected_device=%s",
        device.requested,
        device.selected,
    )
    check_database()
    LOGGER.info("database_ready")


def run_worker(*, check_once: bool = False) -> None:
    configure_logging()
    settings = get_settings()
    session_factory = create_session_factory(settings.database_url)
    run_startup_checks(
        settings,
        check_database=lambda: wait_for_database(
            lambda: check_database(session_factory),
            attempts=30,
            delay_seconds=1,
        ),
    )
    if check_once:
        return

    LOGGER.info("worker_idle processing_not_implemented_in_phase_14")
    while True:
        time.sleep(settings.poll_interval_seconds)


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
