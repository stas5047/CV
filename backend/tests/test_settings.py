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
    assert settings.max_image_size_mb == 20
    assert settings.max_video_size_mb == 500


def test_settings_reject_wildcard_cors_origin(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,*")

    with pytest.raises(ValidationError):
        Settings()


def test_settings_repr_masks_sensitive_values(required_env: None) -> None:
    settings = Settings()

    rendered = repr(settings)

    assert "jwt-secret-value" not in rendered
    assert "admin-secret-value" not in rendered
    assert "db-secret" not in rendered
    assert "postgresql+psycopg://" not in rendered
    assert "********" in rendered
