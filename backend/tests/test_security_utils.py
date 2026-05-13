from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.authorization import (
    ensure_owner_or_admin,
    get_current_admin_user,
    owner_id_from_job,
    owner_id_from_media,
    owner_id_from_user_field,
)
from app.core.storage_paths import (
    safe_download_filename,
    safe_join_storage_path,
    sanitize_upload_filename,
    validate_relative_storage_path,
)
from app.db.models import User

CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]


def _user(*, role: str = "user", is_active: bool = True) -> User:
    return User(
        id=uuid4(),
        email=f"{uuid4()}@example.local",
        password_hash="hash",
        role=role,
        is_active=is_active,
    )


def test_admin_dependency_accepts_admin_user() -> None:
    admin = _user(role="admin")

    assert get_current_admin_user(admin) is admin


def test_admin_dependency_response_is_safe_for_regular_user() -> None:
    regular_user = _user()
    app = FastAPI()
    app.dependency_overrides[get_current_admin_user] = lambda: get_current_admin_user(
        regular_user
    )

    @app.get("/admin-only")
    def admin_only(current_user: CurrentAdminUser) -> dict[str, str]:
        return {"role": current_user.role}

    response = TestClient(app).get("/admin-only")

    assert response.status_code == 403
    response_text = response.text.lower()
    assert "traceback" not in response_text
    assert "password" not in response_text
    assert "token" not in response_text
    assert "/app/storage" not in response_text


def test_admin_dependency_rejects_regular_user() -> None:
    regular_user = _user()

    with pytest.raises(Exception) as exc_info:
        get_current_admin_user(regular_user)

    assert exc_info.value.status_code == 403
    assert "password" not in str(exc_info.value.detail).lower()


def test_ownership_helper_accepts_owner_and_admin() -> None:
    owner = _user()
    admin = _user(role="admin")
    resource = SimpleNamespace(user_id=owner.id)

    assert ensure_owner_or_admin(resource, owner, owner_id_from_user_field) is resource
    assert ensure_owner_or_admin(resource, admin, owner_id_from_user_field) is resource


def test_ownership_helper_rejects_missing_and_cross_owner_same_way() -> None:
    owner = _user()
    other_user = _user()
    resource = SimpleNamespace(user_id=owner.id)

    missing_error = None
    cross_owner_error = None
    with pytest.raises(Exception) as missing_exc:
        ensure_owner_or_admin(None, other_user, owner_id_from_user_field)
    missing_error = missing_exc.value

    with pytest.raises(Exception) as cross_owner_exc:
        ensure_owner_or_admin(resource, other_user, owner_id_from_user_field)
    cross_owner_error = cross_owner_exc.value

    assert missing_error.status_code == 404
    assert cross_owner_error.status_code == 404
    assert missing_error.detail == cross_owner_error.detail


def test_ownership_helper_supports_media_and_job_indirect_ownership() -> None:
    owner = _user()
    media = SimpleNamespace(user_id=owner.id)
    job = SimpleNamespace(user_id=uuid4(), media_file=media)
    detection = SimpleNamespace(job=job)

    assert ensure_owner_or_admin(media, owner, owner_id_from_media) is media
    assert ensure_owner_or_admin(detection, owner, owner_id_from_job) is detection


@pytest.mark.parametrize(
    "relative_path",
    [
        "uploads/user-id/media-id/original.jpg",
        "results/job-id/detections.csv",
        "models/model-id/weights.pt",
    ],
)
def test_validate_relative_storage_path_accepts_safe_paths(relative_path: str) -> None:
    assert validate_relative_storage_path(relative_path) == relative_path


@pytest.mark.parametrize(
    "relative_path",
    [
        "",
        "/app/storage/uploads/file.jpg",
        r"C:\storage\uploads\file.jpg",
        r"\\server\share\file.jpg",
        "../secret.txt",
        r"..\secret.txt",
        "uploads/../secret.txt",
        r"uploads\..\secret.txt",
        "uploads/path/..",
        "uploads//file.jpg",
        "uploads/\x00/file.jpg",
    ],
)
def test_validate_relative_storage_path_rejects_unsafe_paths(relative_path: str) -> None:
    with pytest.raises(ValueError):
        validate_relative_storage_path(relative_path)


def test_safe_join_storage_path_stays_under_storage_root(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"

    result = safe_join_storage_path(storage_root, "uploads/user/media/original.png")

    assert result == storage_root.resolve() / "uploads" / "user" / "media" / "original.png"


@pytest.mark.parametrize(
    ("raw_name", "expected"),
    [
        ("drone.jpg", "drone.jpg"),
        (r"..\evil.mp4", "evil.mp4"),
        ("../../secret.txt", "secret.txt"),
        ("CON", "file"),
        ("NUL.txt", "file.txt"),
        ("unsafe<>name?.png", "unsafe_name_.png"),
        ("name. ", "name"),
        ("", "file"),
        ("////", "file"),
    ],
)
def test_sanitize_upload_filename(raw_name: str, expected: str) -> None:
    assert sanitize_upload_filename(raw_name) == expected


@pytest.mark.parametrize("raw_name", ["../result.csv", r"..\result.csv", "NUL", "report. "])
def test_safe_download_filename_has_no_path_separators(raw_name: str) -> None:
    filename = safe_download_filename(raw_name)

    assert "/" not in filename
    assert "\\" not in filename
    assert filename
