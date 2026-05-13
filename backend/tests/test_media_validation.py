from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import UUID

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.passwords import hash_password
from app.db.models import Base, MediaFile, User
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture
def media_validation_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'media-validation.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(tmp_path / "storage"))
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


def _create_user(email: str, password: str) -> UUID:
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role="user",
            is_active=True,
        )
        session.add(user)
        session.commit()
        return user.id


def _token(client: TestClient) -> str:
    _create_user("owner@example.local", "user-secret-value")
    response = client.post(
        "/api/auth/login",
        json={"email": "owner@example.local", "password": "user-secret-value"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _image_bytes(format_name: str) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 3), (255, 255, 255)).save(buffer, format=format_name)
    return buffer.getvalue()


def _video_bytes(tmp_path: Path, extension: str, fourcc_name: str) -> bytes:
    path = tmp_path / f"clip{extension}"
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*fourcc_name),
        5.0,
        (2, 2),
    )
    assert writer.isOpened()
    writer.write(np.zeros((2, 2, 3), dtype=np.uint8))
    writer.release()
    return path.read_bytes()


@pytest.mark.parametrize(
    ("extension", "mime_type", "format_name"),
    [
        (".jpg", "image/jpeg", "JPEG"),
        (".jpeg", "image/jpeg", "JPEG"),
        (".png", "image/png", "PNG"),
        (".webp", "image/webp", "WEBP"),
    ],
)
def test_accepts_required_image_formats(
    media_validation_client: TestClient,
    extension: str,
    mime_type: str,
    format_name: str,
) -> None:
    token = _token(media_validation_client)

    response = media_validation_client.post(
        "/api/media",
        headers=_headers(token),
        files={"file": (f"drone{extension}", _image_bytes(format_name), mime_type)},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["media_type"] == "image"
    assert body["width"] == 2
    assert body["height"] == 3


@pytest.mark.parametrize(
    ("extension", "mime_type", "fourcc_name"),
    [
        (".mp4", "video/mp4", "mp4v"),
        (".avi", "video/x-msvideo", "MJPG"),
        (".mov", "video/quicktime", "mp4v"),
        (".mkv", "video/x-matroska", "mp4v"),
    ],
)
def test_accepts_required_video_formats(
    media_validation_client: TestClient,
    tmp_path: Path,
    extension: str,
    mime_type: str,
    fourcc_name: str,
) -> None:
    token = _token(media_validation_client)

    response = media_validation_client.post(
        "/api/media",
        headers=_headers(token),
        files={
            "file": (
                f"drone{extension}",
                _video_bytes(tmp_path, extension, fourcc_name),
                mime_type,
            )
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["media_type"] == "video"
    assert body["frame_count"] == 1
    assert body["fps"] == 5.0
    assert body["duration_seconds"] == 0.2


def test_rejects_mismatched_extension_mime_and_content(
    media_validation_client: TestClient,
) -> None:
    token = _token(media_validation_client)

    response = media_validation_client.post(
        "/api/media",
        headers=_headers(token),
        files={"file": ("drone.jpg", _image_bytes("PNG"), "image/jpeg")},
    )

    assert response.status_code == 400


def test_rejects_mismatched_video_extension_mime_and_content(
    media_validation_client: TestClient,
    tmp_path: Path,
) -> None:
    token = _token(media_validation_client)

    response = media_validation_client.post(
        "/api/media",
        headers=_headers(token),
        files={
            "file": (
                "drone.mp4",
                _video_bytes(tmp_path, ".avi", "MJPG"),
                "video/mp4",
            )
        },
    )

    assert response.status_code == 400


def test_oversized_upload_leaves_no_media_record(
    media_validation_client: TestClient,
) -> None:
    token = _token(media_validation_client)
    response = media_validation_client.post(
        "/api/media",
        headers=_headers(token),
        files={"file": ("drone.png", _image_bytes("PNG") + b"0" * 1_100_000, "image/png")},
    )

    assert response.status_code == 413
    with sessionmaker(bind=get_engine())() as session:
        assert session.query(MediaFile).count() == 0
