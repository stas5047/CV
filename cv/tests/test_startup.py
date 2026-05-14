import logging

from aerovision_worker import main as worker_main
from aerovision_worker.device import DeviceUnavailableError
from aerovision_worker.main import run_startup_checks
from aerovision_worker.settings import WorkerSettings


def test_run_startup_checks_logs_selected_device_and_checks_database(caplog) -> None:
    caplog.set_level(logging.INFO, logger="aerovision_worker")
    checked = {"database": False}
    settings = WorkerSettings(
        database_url="postgresql+psycopg://user:secret@postgres:5432/db",
        cv_device="auto",
    )

    def check_database() -> None:
        checked["database"] = True

    run_startup_checks(settings, check_database=check_database, cuda_available=lambda: False)

    log_text = caplog.text
    assert checked["database"] is True
    assert "selected_device=cpu" in log_text
    assert "secret" not in log_text
    assert "/app/storage" not in log_text


def test_forced_cuda_unavailable_fails_before_database_check() -> None:
    checked = {"database": False}
    settings = WorkerSettings(
        database_url="postgresql+psycopg://user:secret@postgres:5432/db",
        cv_device="cuda",
    )

    def check_database() -> None:
        checked["database"] = True

    try:
        run_startup_checks(settings, check_database=check_database, cuda_available=lambda: False)
    except DeviceUnavailableError as exc:
        assert "CUDA requested but unavailable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("forced CUDA should fail before database check")

    assert checked["database"] is False


def test_run_worker_reports_forced_cuda_failure_without_database_retry(monkeypatch) -> None:
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        cv_device="cuda",
    )

    monkeypatch.setattr(worker_main, "get_settings", lambda: settings)
    monkeypatch.setattr(worker_main, "create_session_factory", lambda _database_url: object())
    monkeypatch.setattr("aerovision_worker.device.torch_cuda_available", lambda: False)
    monkeypatch.setattr("aerovision_worker.database.time.sleep", lambda _seconds: None)

    try:
        worker_main.run_worker(check_once=True)
    except DeviceUnavailableError as exc:
        assert "CUDA requested but unavailable" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("forced CUDA should fail with device-specific error")
