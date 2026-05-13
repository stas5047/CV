from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import hash_password, verify_password
from app.db.models import Base, User
from app.db.session import get_engine
from app.main import create_app
from app.setup import run_setup


@pytest.fixture
def auth_client(required_env: None, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'auth.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    get_engine.cache_clear()
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    with TestClient(create_app()) as client:
        yield client

    Base.metadata.drop_all(get_engine())
    get_engine.cache_clear()


def _create_user(
    email: str,
    password: str,
    *,
    role: str = "user",
    is_active: bool = True,
) -> None:
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        session.add(
            User(
                email=email.strip().lower(),
                password_hash=hash_password(password),
                role=role,
                is_active=is_active,
            )
        )
        session.commit()


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_register_creates_active_user_with_hashed_password(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/register",
        json={"email": " New.User@Example.Local ", "password": "user-secret-value"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@example.local"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "password_hash" not in body
    assert "access_token" not in body

    with sessionmaker(bind=get_engine())() as session:
        user = session.scalar(select(User).where(User.email == "new.user@example.local"))

    assert user is not None
    assert user.role == "user"
    assert user.password_hash != "user-secret-value"
    assert verify_password("user-secret-value", user.password_hash)


def test_register_rejects_disabled_registration(
    auth_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_PUBLIC_REGISTRATION", "false")
    from app.core.config import get_settings

    get_settings.cache_clear()

    response = auth_client.post(
        "/api/auth/register",
        json={"email": "blocked@example.local", "password": "user-secret-value"},
    )

    assert response.status_code == 403


def test_register_rejects_short_password(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/register",
        json={"email": "short@example.local", "password": "short"},
    )

    assert response.status_code == 422


def test_register_rejects_duplicate_email_safely(auth_client: TestClient) -> None:
    payload = {"email": "duplicate@example.local", "password": "user-secret-value"}
    assert auth_client.post("/api/auth/register", json=payload).status_code == 201

    response = auth_client.post("/api/auth/register", json=payload)

    assert response.status_code == 409
    assert "password_hash" not in response.text


def test_register_cannot_smuggle_admin_role(auth_client: TestClient) -> None:
    response = auth_client.post(
        "/api/auth/register",
        json={
            "email": "smuggle@example.local",
            "password": "user-secret-value",
            "role": "admin",
            "is_active": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"
    assert response.json()["is_active"] is True

    with sessionmaker(bind=get_engine())() as session:
        user = session.scalar(select(User).where(User.email == "smuggle@example.local"))

    assert user is not None
    assert user.role == "user"
    assert user.is_active is True


def test_authenticated_clients_cannot_register_or_login(auth_client: TestClient) -> None:
    token = _login_after_registration(auth_client)

    register_response = auth_client.post(
        "/api/auth/register",
        json={"email": "other@example.local", "password": "user-secret-value"},
        headers={"Authorization": f"Bearer {token}"},
    )
    login_response = auth_client.post(
        "/api/auth/login",
        json={"email": "phase5@example.local", "password": "user-secret-value"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert register_response.status_code == 403
    assert login_response.status_code == 403


def test_login_returns_access_token_for_active_user(auth_client: TestClient) -> None:
    _create_user("active@example.local", "user-secret-value")

    response = auth_client.post(
        "/api/auth/login",
        json={"email": " ACTIVE@example.local ", "password": "user-secret-value"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert "password_hash" not in body


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.local", "user-secret-value"),
        ("known@example.local", "wrong-password"),
    ],
)
def test_login_rejects_bad_credentials(
    auth_client: TestClient,
    email: str,
    password: str,
) -> None:
    _create_user("known@example.local", "user-secret-value")

    response = auth_client.post("/api/auth/login", json={"email": email, "password": password})

    assert response.status_code == 401
    assert "password_hash" not in response.text


def test_login_rejects_inactive_user(auth_client: TestClient) -> None:
    _create_user("inactive@example.local", "user-secret-value", is_active=False)

    response = auth_client.post(
        "/api/auth/login",
        json={"email": "inactive@example.local", "password": "user-secret-value"},
    )

    assert response.status_code == 401
    assert "password_hash" not in response.text


def test_me_returns_safe_current_user_profile(auth_client: TestClient) -> None:
    token = _login_after_registration(auth_client)

    response = auth_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "phase5@example.local"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "password_hash" not in body
    assert "access_token" not in body


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-token"},
    ],
)
def test_me_rejects_missing_or_invalid_token(
    auth_client: TestClient,
    headers: dict[str, str],
) -> None:
    response = auth_client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401


def test_me_rejects_expired_token(auth_client: TestClient, required_env: None) -> None:
    settings = Settings()
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = auth_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_rejects_inactive_user_token(auth_client: TestClient) -> None:
    _create_user("inactive-token@example.local", "user-secret-value", is_active=False)
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        user = session.scalar(select(User).where(User.email == "inactive-token@example.local"))
        assert user is not None
        user_id = user.id

    settings = Settings()
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(UTC) + timedelta(minutes=30),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = auth_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_seeded_admin_can_login(auth_client: TestClient) -> None:
    run_setup(Settings(), sessionmaker(bind=get_engine()))

    response = auth_client.post(
        "/api/auth/login",
        json={"email": "admin@example.local", "password": "admin-secret-value"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    me_response = auth_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "admin"


def _login_after_registration(client: TestClient) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": "phase5@example.local", "password": "user-secret-value"},
    )
    assert response.status_code == 201
    return _login(client, "phase5@example.local", "user-secret-value")
