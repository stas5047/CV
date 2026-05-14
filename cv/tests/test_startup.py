import logging
from datetime import UTC, datetime
from types import SimpleNamespace

from aerovision_worker import main as worker_main
from aerovision_worker.device import DeviceUnavailableError
from aerovision_worker.main import run_poll_iteration, run_startup_checks
from aerovision_worker.model_runtime import ModelLoadingError
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


def test_run_poll_iteration_loads_model_then_processes_claimed_image_job(
    monkeypatch,
    caplog,
) -> None:
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        stale_job_minutes=10,
        max_retries=2,
    )
    calls: list[tuple[str, object]] = []
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)

    monkeypatch.setattr(worker_main, "utc_now", lambda: now)
    monkeypatch.setattr(
        worker_main,
        "recover_stale_jobs",
        lambda *args, **kwargs: calls.append(("recover", kwargs))
        or SimpleNamespace(requeued=1, failed=0),
    )
    monkeypatch.setattr(
        worker_main,
        "claim_next_job",
        lambda *args, **kwargs: calls.append(("claim", kwargs))
        or SimpleNamespace(id="job-1", media_type="image"),
    )
    monkeypatch.setattr(
        worker_main,
        "fail_processing_job",
        lambda *args, **kwargs: calls.append(("fail", kwargs)) or True,
    )
    monkeypatch.setattr(
        worker_main,
        "process_image_job",
        lambda *args, **kwargs: calls.append(("process_image", kwargs)) or None,
        raising=False,
    )
    model_runtime = SimpleNamespace(
        load_for_job=lambda *args, **kwargs: calls.append(("load_model", kwargs))
        or SimpleNamespace(model=object(), metadata=SimpleNamespace(id="model-1", name="Model 1"))
    )
    caplog.set_level(logging.INFO, logger="aerovision_worker")

    claimed = run_poll_iteration(
        settings,
        object(),
        worker_id="worker-a",
        model_runtime=model_runtime,
    )

    assert claimed is True
    assert [name for name, _payload in calls] == ["recover", "claim", "load_model", "process_image"]
    assert calls[2][1]["job_id"] == "job-1"
    assert calls[3][1]["job_id"] == "job-1"
    assert calls[3][1]["worker_id"] == "worker-a"
    assert "stale_jobs_recovered requeued=1 failed=0" in caplog.text
    assert "job_claimed job_id=job-1 media_type=image worker_id=worker-a" in caplog.text


def test_run_poll_iteration_marks_missing_model_failed_with_safe_error(monkeypatch) -> None:
    settings = WorkerSettings(database_url="sqlite+pysqlite:///:memory:")
    calls: list[tuple[str, object]] = []
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)

    monkeypatch.setattr(worker_main, "utc_now", lambda: now)
    monkeypatch.setattr(
        worker_main,
        "recover_stale_jobs",
        lambda *args, **kwargs: SimpleNamespace(requeued=0, failed=0),
    )
    monkeypatch.setattr(
        worker_main,
        "claim_next_job",
        lambda *args, **kwargs: SimpleNamespace(id="job-1", media_type="image"),
    )
    monkeypatch.setattr(
        worker_main,
        "fail_processing_job",
        lambda *args, **kwargs: calls.append(("fail", kwargs)) or True,
    )
    model_runtime = SimpleNamespace(
        load_for_job=lambda *args, **kwargs: (_ for _ in ()).throw(
            ModelLoadingError("Model weights file is missing")
        )
    )

    claimed = run_poll_iteration(
        settings,
        object(),
        worker_id="worker-a",
        model_runtime=model_runtime,
    )

    assert claimed is True
    assert calls == [
        (
            "fail",
            {
                "job_id": "job-1",
                "worker_id": "worker-a",
                "error_message": "Model weights file is missing",
                "now": now,
            },
        )
    ]


def test_run_poll_iteration_returns_false_when_no_job_claimed(monkeypatch) -> None:
    settings = WorkerSettings(database_url="sqlite+pysqlite:///:memory:")

    monkeypatch.setattr(
        worker_main,
        "recover_stale_jobs",
        lambda *args, **kwargs: SimpleNamespace(requeued=0, failed=0),
    )
    monkeypatch.setattr(worker_main, "claim_next_job", lambda *args, **kwargs: None)

    claimed = run_poll_iteration(settings, object(), worker_id="worker-a")

    assert claimed is False


def test_run_poll_iteration_dispatches_claimed_video_job(monkeypatch) -> None:
    settings = WorkerSettings(database_url="sqlite+pysqlite:///:memory:")
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        worker_main,
        "recover_stale_jobs",
        lambda *args, **kwargs: SimpleNamespace(requeued=0, failed=0),
    )
    monkeypatch.setattr(
        worker_main,
        "claim_next_job",
        lambda *args, **kwargs: SimpleNamespace(id="job-1", media_type="video"),
    )
    monkeypatch.setattr(
        worker_main,
        "process_video_job",
        lambda *args, **kwargs: calls.append(("process_video", kwargs)) or None,
    )
    model_runtime = SimpleNamespace(
        load_for_job=lambda *args, **kwargs: SimpleNamespace(
            model=object(),
            metadata=SimpleNamespace(id="model-1", name="Model 1"),
        )
    )

    claimed = run_poll_iteration(
        settings,
        object(),
        worker_id="worker-a",
        model_runtime=model_runtime,
    )

    assert claimed is True
    assert calls[0][0] == "process_video"
    assert calls[0][1]["job_id"] == "job-1"
    assert calls[0][1]["worker_id"] == "worker-a"


def test_run_poll_iteration_fails_unknown_claimed_media_type(monkeypatch) -> None:
    settings = WorkerSettings(database_url="sqlite+pysqlite:///:memory:")
    calls: list[tuple[str, object]] = []
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)

    monkeypatch.setattr(worker_main, "utc_now", lambda: now)
    monkeypatch.setattr(
        worker_main,
        "recover_stale_jobs",
        lambda *args, **kwargs: SimpleNamespace(requeued=0, failed=0),
    )
    monkeypatch.setattr(
        worker_main,
        "claim_next_job",
        lambda *args, **kwargs: SimpleNamespace(id="job-1", media_type="audio"),
    )
    monkeypatch.setattr(
        worker_main,
        "fail_processing_job",
        lambda *args, **kwargs: calls.append(("fail", kwargs)) or True,
    )
    model_runtime = SimpleNamespace(
        load_for_job=lambda *args, **kwargs: SimpleNamespace(
            model=object(),
            metadata=SimpleNamespace(id="model-1", name="Model 1"),
        )
    )

    claimed = run_poll_iteration(
        settings,
        object(),
        worker_id="worker-a",
        model_runtime=model_runtime,
    )

    assert claimed is True
    assert calls == [
        (
            "fail",
            {
                "job_id": "job-1",
                "worker_id": "worker-a",
                "error_message": "Claimed job media type is unsupported",
                "now": now,
            },
        )
    ]
