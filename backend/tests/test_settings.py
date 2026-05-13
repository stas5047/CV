import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_load_required_environment(required_env: None) -> None:
    settings = Settings()

    assert settings.database_url.startswith("postgresql+psycopg://")
    assert settings.backend_cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert settings.allow_public_registration is True
    assert settings.active_model_id is None
    assert settings.max_image_size_mb == 20
    assert settings.max_video_size_mb == 500
    assert settings.run_migrations_on_start is True
    assert settings.run_seed_on_start is True


def test_settings_parse_startup_switches(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RUN_MIGRATIONS_ON_START", "false")
    monkeypatch.setenv("RUN_SEED_ON_START", "false")

    settings = Settings()

    assert settings.run_migrations_on_start is False
    assert settings.run_seed_on_start is False


def test_settings_loads_active_model_id(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ACTIVE_MODEL_ID", "11111111-1111-1111-1111-111111111111")

    settings = Settings()

    assert settings.active_model_id == "11111111-1111-1111-1111-111111111111"


def test_settings_reject_short_admin_password(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ADMIN_PASSWORD", "short")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_reject_wildcard_cors_origin(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,*")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_reject_empty_cors_origins(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", " , ")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_repr_masks_sensitive_values(required_env: None) -> None:
    settings = Settings()

    rendered = repr(settings)

    assert "jwt-secret-value" not in rendered
    assert "admin-secret-value" not in rendered
    assert "db-secret" not in rendered
    assert "postgresql+psycopg://" not in rendered
    assert "active_model_id=None" in rendered
    assert "********" in rendered
