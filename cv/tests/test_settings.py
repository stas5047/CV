import pytest
from pydantic import ValidationError

from aerovision_worker.settings import WorkerSettings


def test_settings_parse_worker_environment_defaults() -> None:
    settings = WorkerSettings(database_url="postgresql+psycopg://user:pass@postgres:5432/db")

    assert settings.storage_root == "/app/storage"
    assert settings.models_root == "/app/storage/models"
    assert settings.cv_device == "cpu"
    assert settings.poll_interval_seconds == 2
    assert settings.heartbeat_frames == 30
    assert settings.heartbeat_seconds == 2
    assert settings.stale_job_minutes == 10
    assert settings.max_retries == 2


def test_settings_reject_invalid_device() -> None:
    with pytest.raises(ValidationError):
        WorkerSettings(
            database_url="postgresql+psycopg://user:pass@postgres:5432/db",
            cv_device="gpu",
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("poll_interval_seconds", 0),
        ("heartbeat_frames", 0),
        ("heartbeat_seconds", 0),
        ("stale_job_minutes", 0),
        ("max_retries", -1),
    ],
)
def test_settings_reject_invalid_numeric_values(field: str, value: int) -> None:
    with pytest.raises(ValidationError):
        WorkerSettings(
            database_url="postgresql+psycopg://user:pass@postgres:5432/db",
            **{field: value},
        )


def test_settings_log_payload_redacts_sensitive_values() -> None:
    settings = WorkerSettings(
        database_url="postgresql+psycopg://user:secret@postgres:5432/db",
        storage_root="/app/storage",
        models_root="/app/storage/models",
    )

    payload = settings.safe_log_payload()
    rendered = repr(payload)

    assert payload["database_url"] == "<redacted>"
    assert payload["storage_root"] == "<path>"
    assert payload["models_root"] == "<path>"
    assert "secret" not in rendered
    assert "/app/storage" not in rendered
