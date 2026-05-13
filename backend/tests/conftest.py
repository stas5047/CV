from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://aerovision:db-secret@postgres:5432/aerovision",
    )
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-secret-value")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.local")
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-secret-value")
    monkeypatch.setenv("ALLOW_PUBLIC_REGISTRATION", "true")
    monkeypatch.setenv("STORAGE_ROOT", "/app/storage")
    monkeypatch.setenv("MODELS_ROOT", "/app/storage/models")
    monkeypatch.setenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "20")
    monkeypatch.setenv("MAX_VIDEO_SIZE_MB", "500")


@pytest.fixture
def client(required_env: None) -> TestClient:
    return TestClient(create_app())
