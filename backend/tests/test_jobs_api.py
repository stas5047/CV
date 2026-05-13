from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings
from app.core.passwords import hash_password
from app.db.models import Base, MediaFile, ModelVersion, ProcessingJob, User, utc_now
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture
def jobs_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'jobs.db'}"
    storage_root = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))
    monkeypatch.setenv("MODELS_ROOT", str(storage_root / "models"))
    monkeypatch.delenv("ACTIVE_MODEL_ID", raising=False)
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


def _create_media(
    user_id: UUID,
    *,
    media_type: str = "image",
    deleted: bool = False,
) -> UUID:
    media_id = uuid4()
    extension = ".png" if media_type == "image" else ".mp4"
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        media = MediaFile(
            id=media_id,
            user_id=user_id,
            original_filename=f"source{extension}",
            stored_path=f"uploads/{user_id}/{media_id}/original{extension}",
            media_type=media_type,
            mime_type="image/png" if media_type == "image" else "video/mp4",
            file_size_bytes=128,
            width=640,
            height=480,
            frame_count=1 if media_type == "image" else 60,
            fps=None if media_type == "image" else 30.0,
            duration_seconds=None if media_type == "image" else 2.0,
            deleted_at=utc_now() if deleted else None,
        )
        session.add(media)
        session.commit()
        return media.id


def _create_model(*, active: bool = False, name: str = "YOLO26s") -> UUID:
    model_id = uuid4()
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        model = ModelVersion(
            id=model_id,
            name=name,
            model_family="YOLO26",
            variant="s",
            weights_path=f"models/{model_id}/weights.pt",
            dataset_name="Seraphim",
            dataset_split_description="test split",
            metrics_json={},
            is_active=active,
        )
        session.add(model)
        session.commit()
        return model.id


def _job_count() -> int:
    with sessionmaker(bind=get_engine())() as session:
        return session.scalar(select(func.count()).select_from(ProcessingJob)) or 0


def test_job_creation_requires_active_user(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    media_id = _create_media(user_id)
    _create_model(active=True)

    guest_response = jobs_client.post("/api/jobs", json={"media_id": str(media_id)})

    inactive_id = _create_user("inactive@example.local", "user-secret-value", is_active=False)
    token = jwt.encode({"sub": str(inactive_id)}, Settings().jwt_secret_key, algorithm="HS256")
    inactive_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id)},
        headers=_auth(token),
    )

    assert guest_response.status_code == 401
    assert inactive_response.status_code == 401
    assert _job_count() == 0


def test_user_creates_queued_image_job_with_defaults(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id, media_type="image")
    active_model_id = _create_model(active=True)

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id)},
        headers=_auth(token),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user_id"] == str(user_id)
    assert body["media_file_id"] == str(media_id)
    assert body["model_version_id"] == str(active_model_id)
    assert body["status"] == "queued"
    assert body["progress_percent"] == 0
    assert body["retry_count"] == 0
    assert body["input_params_json"] == {
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45,
        "image_size": 640,
        "tracker_type": "bytetrack",
        "frame_stride": 1,
    }
    assert "result_media_path" not in body
    assert "csv_path" not in body
    assert "json_path" not in body
    assert str(Path.cwd()) not in response.text
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, UUID(body["id"]))
    assert job is not None
    assert job.status == "queued"
    assert job.progress_percent == 0
    assert job.retry_count == 0
    assert job.result_media_path is None
    assert job.csv_path is None
    assert job.json_path is None


def test_admin_job_creation_is_scoped_to_admin_owned_media(jobs_client: TestClient) -> None:
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    other_id = _create_user("other@example.local", "user-secret-value")
    token = _login(jobs_client, "admin@example.local", "admin-secret-value")
    admin_media_id = _create_media(admin_id)
    other_media_id = _create_media(other_id)
    _create_model(active=True)

    own_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(admin_media_id)},
        headers=_auth(token),
    )
    cross_owner_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(other_media_id)},
        headers=_auth(token),
    )

    assert own_response.status_code == 201
    assert cross_owner_response.status_code == 404
    assert _job_count() == 1


@pytest.mark.parametrize("deleted", [False, True])
def test_user_cannot_create_job_for_missing_cross_owner_or_deleted_media(
    jobs_client: TestClient,
    deleted: bool,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    other_id = _create_user("other@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    blocked_media_id = _create_media(other_id if not deleted else owner_id, deleted=deleted)
    _create_model(active=True)

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(blocked_media_id)},
        headers=_auth(token),
    )
    missing_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(uuid4())},
        headers=_auth(token),
    )

    assert response.status_code == 404
    assert missing_response.status_code == 404
    assert _job_count() == 0


def test_video_job_accepts_tracker_and_thresholds(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id, media_type="video")
    _create_model(active=True)

    response = jobs_client.post(
        "/api/jobs",
        json={
            "media_id": str(media_id),
            "confidence_threshold": 0.5,
            "iou_threshold": 0.6,
            "tracker_type": "botsort",
        },
        headers=_auth(token),
    )

    assert response.status_code == 201, response.text
    assert response.json()["input_params_json"] == {
        "confidence_threshold": 0.5,
        "iou_threshold": 0.6,
        "image_size": 640,
        "tracker_type": "botsort",
        "frame_stride": 1,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"confidence_threshold": -0.01},
        {"confidence_threshold": 1.01},
        {"iou_threshold": -0.01},
        {"iou_threshold": 1.01},
        {"tracker_type": "unknown"},
        {"frame_stride": 2},
    ],
)
def test_invalid_processing_params_do_not_create_job(
    jobs_client: TestClient,
    payload: dict[str, object],
) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id, media_type="video")
    _create_model(active=True)

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id), **payload},
        headers=_auth(token),
    )

    assert response.status_code in {400, 422}
    assert _job_count() == 0


def test_image_job_rejects_client_tracker_type(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id, media_type="image")
    _create_model(active=True)

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id), "tracker_type": "bytetrack"},
        headers=_auth(token),
    )

    assert response.status_code == 422
    assert _job_count() == 0


def test_explicit_model_wins_and_can_be_inactive(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id)
    active_model_id = _create_model(active=True, name="active")
    inactive_model_id = _create_model(active=False, name="inactive")

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id), "model_version_id": str(inactive_model_id)},
        headers=_auth(token),
    )

    assert response.status_code == 201, response.text
    assert response.json()["model_version_id"] == str(inactive_model_id)
    assert response.json()["model_version_id"] != str(active_model_id)


def test_fallback_model_used_only_when_no_active_db_model(
    jobs_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    fallback_id = _create_model(active=False, name="fallback")
    monkeypatch.setenv("ACTIVE_MODEL_ID", str(fallback_id))
    get_settings.cache_clear()

    fallback_media_id = _create_media(user_id)
    fallback_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(fallback_media_id)},
        headers=_auth(token),
    )

    active_id = _create_model(active=True, name="active")
    active_media_id = _create_media(user_id)
    active_response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(active_media_id)},
        headers=_auth(token),
    )

    assert fallback_response.status_code == 201, fallback_response.text
    assert fallback_response.json()["model_version_id"] == str(fallback_id)
    assert active_response.status_code == 201, active_response.text
    assert active_response.json()["model_version_id"] == str(active_id)


@pytest.mark.parametrize("fallback_id", [None, "not-a-uuid", str(uuid4())])
def test_unavailable_model_selection_rejects_without_job(
    jobs_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    fallback_id: str | None,
) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id)
    if fallback_id is None:
        monkeypatch.delenv("ACTIVE_MODEL_ID", raising=False)
    else:
        monkeypatch.setenv("ACTIVE_MODEL_ID", fallback_id)
    get_settings.cache_clear()

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id)},
        headers=_auth(token),
    )

    assert response.status_code in {400, 422}
    assert _job_count() == 0


def test_missing_explicit_model_rejects_without_job(jobs_client: TestClient) -> None:
    user_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    media_id = _create_media(user_id)

    response = jobs_client.post(
        "/api/jobs",
        json={"media_id": str(media_id), "model_version_id": str(uuid4())},
        headers=_auth(token),
    )

    assert response.status_code == 404
    assert _job_count() == 0
