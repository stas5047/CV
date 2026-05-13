from fastapi.testclient import TestClient

from app.db.health import DatabaseHealthError


def test_health_returns_safe_status(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_health_payload_excludes_sensitive_values(client: TestClient) -> None:
    response_text = client.get("/api/health").text

    assert "jwt-secret-value" not in response_text
    assert "admin-secret-value" not in response_text
    assert "db-secret" not in response_text
    assert "postgresql+psycopg://" not in response_text


def test_db_health_returns_safe_available_status(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr("app.api.health.check_database", lambda: None)

    response = client.get("/api/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "available"}


def test_db_health_failure_hides_exception_and_secrets(
    client: TestClient,
    monkeypatch,
) -> None:
    raw_error = (
        "could not connect with DATABASE_URL "
        "postgresql+psycopg://aerovision:db-secret@postgres:5432/aerovision"
    )

    def fail() -> None:
        raise DatabaseHealthError(raw_error)

    monkeypatch.setattr("app.api.health.check_database", fail)

    response = client.get("/api/health/db")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unavailable"}
    assert raw_error not in response.text
    assert "db-secret" not in response.text
    assert "postgresql+psycopg://" not in response.text
