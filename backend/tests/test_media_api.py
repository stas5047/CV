from __future__ import annotations

import base64
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.passwords import hash_password
from app.db.models import Base, MediaFile, User
from app.db.session import get_engine
from app.main import create_app

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC"
)


@pytest.fixture
def media_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'media.db'}"
    storage_root = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))
    monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "1")
    monkeypatch.setenv("MAX_VIDEO_SIZE_MB", "1")
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
) -> UUID:
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        user = User(
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.commit()
        return user.id


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _upload_image(
    client: TestClient,
    token: str,
    *,
    filename: str = "drone.png",
    content: bytes = PNG_1X1,
    content_type: str = "image/png",
) -> dict[str, object]:
    response = client.post(
        "/api/media",
        headers=_auth(token),
        files={"file": (filename, content, content_type)},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_upload_image_creates_safe_media_record(media_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(media_client, "owner@example.local", "user-secret-value")

    body = _upload_image(media_client, token, filename="../drone.png")

    assert body["original_filename"] == "drone.png"
    assert body["media_type"] == "image"
    assert body["mime_type"] == "image/png"
    assert body["file_size_bytes"] == len(PNG_1X1)
    assert body["width"] == 1
    assert body["height"] == 1
    assert body["frame_count"] == 1
    assert body["fps"] is None
    assert body["duration_seconds"] is None
    assert "stored_path" not in body
    assert str(user_id) not in body["original_filename"]
    assert "/app/storage" not in str(body)

    with sessionmaker(bind=get_engine())() as session:
        media = session.get(MediaFile, UUID(body["id"]))

    assert media is not None
    assert media.user_id == user_id
    assert media.stored_path.startswith(f"uploads/{user_id}/{media.id}/")
    assert Path(media.stored_path).is_absolute() is False
    assert media.deleted_at is None


def test_media_endpoints_require_active_token(media_client: TestClient) -> None:
    _create_user("inactive@example.local", "user-secret-value", is_active=False)
    response = media_client.post(
        "/api/media",
        files={"file": ("drone.png", PNG_1X1, "image/png")},
    )

    assert response.status_code == 401


def test_users_list_only_own_media_and_admin_lists_all(media_client: TestClient) -> None:
    _create_user("owner@example.local", "user-secret-value")
    _create_user("other@example.local", "user-secret-value")
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    owner_token = _login(media_client, "owner@example.local", "user-secret-value")
    other_token = _login(media_client, "other@example.local", "user-secret-value")
    admin_token = _login(media_client, "admin@example.local", "admin-secret-value")

    owner_media = _upload_image(media_client, owner_token, filename="owner.png")
    _upload_image(media_client, other_token, filename="other.png")

    owner_list = media_client.get("/api/media", headers=_auth(owner_token))
    admin_list = media_client.get("/api/media", headers=_auth(admin_token))

    assert owner_list.status_code == 200
    assert [item["id"] for item in owner_list.json()["items"]] == [owner_media["id"]]
    assert admin_list.status_code == 200
    assert admin_list.json()["total"] == 2


def test_cross_owner_detail_and_delete_are_hidden(media_client: TestClient) -> None:
    _create_user("owner@example.local", "user-secret-value")
    _create_user("other@example.local", "user-secret-value")
    owner_token = _login(media_client, "owner@example.local", "user-secret-value")
    other_token = _login(media_client, "other@example.local", "user-secret-value")
    owner_media = _upload_image(media_client, owner_token)

    detail = media_client.get(f"/api/media/{owner_media['id']}", headers=_auth(other_token))
    delete = media_client.delete(f"/api/media/{owner_media['id']}", headers=_auth(other_token))

    assert detail.status_code == 404
    assert delete.status_code == 404


def test_delete_soft_deletes_and_hides_media(media_client: TestClient) -> None:
    _create_user("owner@example.local", "user-secret-value")
    token = _login(media_client, "owner@example.local", "user-secret-value")
    media = _upload_image(media_client, token)

    delete = media_client.delete(f"/api/media/{media['id']}", headers=_auth(token))
    list_response = media_client.get("/api/media", headers=_auth(token))
    detail_response = media_client.get(f"/api/media/{media['id']}", headers=_auth(token))

    assert delete.status_code == 204
    assert list_response.json()["items"] == []
    assert detail_response.status_code == 404
    with sessionmaker(bind=get_engine())() as session:
        deleted_media = session.get(MediaFile, UUID(media["id"]))
    assert deleted_media is not None
    assert deleted_media.deleted_at is not None


@pytest.mark.parametrize(
    ("filename", "content_type", "content"),
    [
        ("drone.txt", "text/plain", b"not media"),
        ("drone.png", "application/octet-stream", PNG_1X1),
        ("drone.png", "image/png", b"not an image"),
        ("../", "image/png", PNG_1X1),
    ],
)
def test_upload_rejects_invalid_inputs(
    media_client: TestClient,
    filename: str,
    content_type: str,
    content: bytes,
) -> None:
    _create_user("owner@example.local", "user-secret-value")
    token = _login(media_client, "owner@example.local", "user-secret-value")

    response = media_client.post(
        "/api/media",
        headers=_auth(token),
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code in {400, 413, 422}
    assert "password" not in response.text.lower()
    assert "token" not in response.text.lower()
    assert "/app/storage" not in response.text


def test_upload_rejects_oversized_file(media_client: TestClient) -> None:
    _create_user("owner@example.local", "user-secret-value")
    token = _login(media_client, "owner@example.local", "user-secret-value")
    oversized = PNG_1X1 + (b"0" * 1_100_000)

    response = media_client.post(
        "/api/media",
        headers=_auth(token),
        files={"file": ("drone.png", oversized, "image/png")},
    )

    assert response.status_code == 413
