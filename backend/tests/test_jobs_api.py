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
from app.db.models import (
    Base,
    Detection,
    MediaFile,
    ModelVersion,
    ProcessingJob,
    Track,
    User,
    utc_now,
)
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


def _create_job(
    user_id: UUID,
    media_id: UUID,
    model_id: UUID,
    *,
    status: str = "queued",
    result_media_path: str | None = None,
    csv_path: str | None = None,
    json_path: str | None = None,
    summary_json: dict[str, object] | None = None,
    deleted: bool = False,
) -> UUID:
    job_id = uuid4()
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        job = ProcessingJob(
            id=job_id,
            user_id=user_id,
            media_file_id=media_id,
            model_version_id=model_id,
            status=status,
            input_params_json={
                "confidence_threshold": 0.25,
                "iou_threshold": 0.45,
                "image_size": 640,
                "tracker_type": "bytetrack",
                "frame_stride": 1,
            },
            summary_json=summary_json,
            result_media_path=result_media_path,
            csv_path=csv_path,
            json_path=json_path,
            progress_percent=100 if status == "completed" else 0,
            retry_count=0,
            deleted_at=utc_now() if deleted else None,
        )
        session.add(job)
        session.commit()
        return job.id


def _create_detection(job_id: UUID, media_id: UUID, *, track_id: int | None = None) -> UUID:
    detection_id = uuid4()
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        detection = Detection(
            id=detection_id,
            job_id=job_id,
            media_file_id=media_id,
            frame_index=3,
            timestamp_ms=100,
            class_id=0,
            class_name="drone",
            confidence=0.8,
            bbox_x1=10,
            bbox_y1=20,
            bbox_x2=50,
            bbox_y2=80,
            frame_width=640,
            frame_height=480,
            track_id=track_id,
        )
        session.add(detection)
        session.commit()
        return detection.id


def _create_track(job_id: UUID) -> UUID:
    track_row_id = uuid4()
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        track = Track(
            id=track_row_id,
            job_id=job_id,
            track_id=7,
            class_name="drone",
            first_frame_index=3,
            last_frame_index=9,
            frames_count=4,
            average_confidence=0.74,
            max_confidence=0.91,
        )
        session.add(track)
        session.commit()
        return track.id


def _write_storage_file(relative_path: str, content: bytes = b"result") -> None:
    storage_root = Path(Settings().storage_root)
    full_path = storage_root / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(content)


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


def test_user_lists_only_own_non_deleted_jobs_and_admin_can_filter_by_owner(
    jobs_client: TestClient,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    other_id = _create_user("other@example.local", "user-secret-value")
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    owner_token = _login(jobs_client, "owner@example.local", "user-secret-value")
    admin_token = _login(jobs_client, "admin@example.local", "admin-secret-value")
    model_id = _create_model(active=True)
    owner_media_id = _create_media(owner_id, media_type="image")
    other_media_id = _create_media(other_id, media_type="video")
    visible_job_id = _create_job(owner_id, owner_media_id, model_id, status="completed")
    _create_job(owner_id, owner_media_id, model_id, deleted=True)
    other_job_id = _create_job(other_id, other_media_id, model_id, status="processing")
    _create_job(admin_id, _create_media(admin_id), model_id)

    owner_response = jobs_client.get("/api/jobs", headers=_auth(owner_token))
    owner_video_filter = jobs_client.get(
        "/api/jobs?media_type=video&owner_id=" + str(other_id),
        headers=_auth(owner_token),
    )
    admin_response = jobs_client.get(
        f"/api/jobs?owner_id={other_id}&status=processing&media_type=video",
        headers=_auth(admin_token),
    )

    assert owner_response.status_code == 200, owner_response.text
    assert [item["id"] for item in owner_response.json()["items"]] == [str(visible_job_id)]
    assert owner_response.json()["total"] == 1
    assert owner_video_filter.status_code == 200
    assert owner_video_filter.json()["items"] == []
    assert admin_response.status_code == 200, admin_response.text
    assert [item["id"] for item in admin_response.json()["items"]] == [str(other_job_id)]
    assert admin_response.json()["total"] == 1


def test_job_detail_summary_detections_tracks_and_result_metadata_are_owner_scoped_and_safe(
    jobs_client: TestClient,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    _create_user("other@example.local", "user-secret-value")
    owner_token = _login(jobs_client, "owner@example.local", "user-secret-value")
    other_token = _login(jobs_client, "other@example.local", "user-secret-value")
    model_id = _create_model(active=True)
    media_id = _create_media(owner_id, media_type="video")
    job_id = _create_job(
        owner_id,
        media_id,
        model_id,
        status="completed",
        result_media_path=f"results/{uuid4()}/wrong.mp4",
        csv_path=f"results/{uuid4()}/wrong.csv",
        json_path=f"results/{uuid4()}/wrong.json",
        summary_json={
            "total_detections": 1,
            "frames_with_detections": 1,
            "average_confidence": 0.8,
        },
    )
    expected_media_path = f"results/{job_id}/annotated.mp4"
    expected_csv_path = f"results/{job_id}/detections.csv"
    expected_json_path = f"results/{job_id}/detections.json"
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, job_id)
        assert job is not None
        job.result_media_path = expected_media_path
        job.csv_path = expected_csv_path
        job.json_path = expected_json_path
        session.commit()
    _write_storage_file(expected_media_path, b"media")
    _write_storage_file(expected_csv_path, b"job_id,media_id\n")
    _write_storage_file(expected_json_path, b'{"detections":[]}')
    detection_id = _create_detection(job_id, media_id, track_id=7)
    track_row_id = _create_track(job_id)

    detail_response = jobs_client.get(f"/api/jobs/{job_id}", headers=_auth(owner_token))
    summary_response = jobs_client.get(f"/api/jobs/{job_id}/summary", headers=_auth(owner_token))
    detections_response = jobs_client.get(
        f"/api/jobs/{job_id}/detections",
        headers=_auth(owner_token),
    )
    tracks_response = jobs_client.get(f"/api/jobs/{job_id}/tracks", headers=_auth(owner_token))
    result_response = jobs_client.get(f"/api/jobs/{job_id}/result", headers=_auth(owner_token))
    cross_owner_response = jobs_client.get(f"/api/jobs/{job_id}/result", headers=_auth(other_token))

    for response in [
        detail_response,
        summary_response,
        detections_response,
        tracks_response,
        result_response,
    ]:
        assert response.status_code == 200, response.text
        assert "result_media_path" not in response.text
        assert "csv_path" not in response.text
        assert "json_path" not in response.text
        assert str(Path(Settings().storage_root)) not in response.text
    detail = detail_response.json()
    assert detail["id"] == str(job_id)
    assert detail["media"]["id"] == str(media_id)
    assert detail["model"]["id"] == str(model_id)
    assert detail["result"]["media"]["download_url"] == f"/api/jobs/{job_id}/download/media"
    assert summary_response.json()["summary"]["total_detections"] == 1
    detection = detections_response.json()["items"][0]
    assert detection["id"] == str(detection_id)
    assert detection["center_x"] == 30
    assert detection["center_y"] == 50
    assert detection["bbox_width"] == 40
    assert detection["bbox_height"] == 60
    assert tracks_response.json()["items"][0]["id"] == str(track_row_id)
    result = result_response.json()
    assert result["media"]["available"] is True
    assert result["csv"]["available"] is True
    assert result["json"]["available"] is True
    assert cross_owner_response.status_code == 404


def test_inactive_user_cannot_access_result_or_download_routes(jobs_client: TestClient) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    inactive_id = _create_user("inactive@example.local", "user-secret-value", is_active=False)
    model_id = _create_model(active=True)
    media_id = _create_media(owner_id)
    job_id = _create_job(
        owner_id,
        media_id,
        model_id,
        status="completed",
        csv_path=f"results/{uuid4()}/detections.csv",
    )
    token = jwt.encode({"sub": str(inactive_id)}, Settings().jwt_secret_key, algorithm="HS256")

    result_response = jobs_client.get(f"/api/jobs/{job_id}/result", headers=_auth(token))
    download_response = jobs_client.get(f"/api/jobs/{job_id}/download/csv", headers=_auth(token))

    assert result_response.status_code == 401
    assert download_response.status_code == 401


def test_delete_soft_deletes_job_and_cancels_queued_job_without_removing_files(
    jobs_client: TestClient,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    owner_token = _login(jobs_client, "owner@example.local", "user-secret-value")
    model_id = _create_model(active=True)
    media_id = _create_media(owner_id)
    csv_path = f"results/{uuid4()}/detections.csv"
    job_id = _create_job(owner_id, media_id, model_id, status="queued", csv_path=csv_path)
    _write_storage_file(csv_path, b"job_id\n")

    response = jobs_client.delete(f"/api/jobs/{job_id}", headers=_auth(owner_token))
    list_response = jobs_client.get("/api/jobs", headers=_auth(owner_token))
    detail_response = jobs_client.get(f"/api/jobs/{job_id}", headers=_auth(owner_token))

    assert response.status_code == 204
    assert list_response.status_code == 200
    assert list_response.json()["items"] == []
    assert detail_response.status_code == 404
    assert (Path(Settings().storage_root) / csv_path).is_file()
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, job_id)
        assert job is not None
        assert job.status == "cancelled"
        assert job.deleted_at is not None


def test_downloads_require_job_owned_existing_files_under_job_results_directory(
    jobs_client: TestClient,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    _create_user("other@example.local", "user-secret-value")
    owner_token = _login(jobs_client, "owner@example.local", "user-secret-value")
    other_token = _login(jobs_client, "other@example.local", "user-secret-value")
    model_id = _create_model(active=True)
    media_id = _create_media(owner_id, media_type="image")
    job_id = _create_job(
        owner_id,
        media_id,
        model_id,
        status="completed",
        csv_path=f"results/{uuid4()}/wrong-job.csv",
        json_path=f"results/{uuid4()}/missing.json",
    )
    csv_path = f"results/{job_id}/detections.csv"
    json_path = f"results/{job_id}/detections.json"
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, job_id)
        assert job is not None
        job.csv_path = csv_path
        job.json_path = json_path
        session.commit()
    _write_storage_file(csv_path, b"job_id,media_id\n")

    csv_response = jobs_client.get(f"/api/jobs/{job_id}/download/csv", headers=_auth(owner_token))
    missing_json_response = jobs_client.get(
        f"/api/jobs/{job_id}/download/json",
        headers=_auth(owner_token),
    )
    cross_owner_response = jobs_client.get(
        f"/api/jobs/{job_id}/download/csv",
        headers=_auth(other_token),
    )
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, job_id)
        assert job is not None
        job.csv_path = f"results/{uuid4()}/wrong-job.csv"
        session.commit()
    wrong_directory_response = jobs_client.get(
        f"/api/jobs/{job_id}/download/csv",
        headers=_auth(owner_token),
    )

    assert csv_response.status_code == 200, csv_response.text
    assert csv_response.content == b"job_id,media_id\n"
    assert "attachment" in csv_response.headers["content-disposition"]
    assert missing_json_response.status_code == 404
    assert str(Path(Settings().storage_root)) not in missing_json_response.text
    assert cross_owner_response.status_code == 404
    assert wrong_directory_response.status_code == 404


def test_completed_no_detection_job_returns_empty_rows_and_csv_json_downloads(
    jobs_client: TestClient,
) -> None:
    owner_id = _create_user("owner@example.local", "user-secret-value")
    token = _login(jobs_client, "owner@example.local", "user-secret-value")
    model_id = _create_model(active=True)
    media_id = _create_media(owner_id)
    job_id = _create_job(
        owner_id,
        media_id,
        model_id,
        status="completed",
        summary_json={
            "total_detections": 0,
            "frames_with_detections": 0,
            "average_confidence": None,
            "maximum_confidence": None,
        },
    )
    csv_path = f"results/{job_id}/detections.csv"
    json_path = f"results/{job_id}/detections.json"
    with sessionmaker(bind=get_engine())() as session:
        job = session.get(ProcessingJob, job_id)
        assert job is not None
        job.csv_path = csv_path
        job.json_path = json_path
        session.commit()
    _write_storage_file(csv_path, b"job_id,media_id,frame_index\n")
    _write_storage_file(json_path, b'{"detections":[],"tracks":[]}')

    summary_response = jobs_client.get(f"/api/jobs/{job_id}/summary", headers=_auth(token))
    detections_response = jobs_client.get(f"/api/jobs/{job_id}/detections", headers=_auth(token))
    tracks_response = jobs_client.get(f"/api/jobs/{job_id}/tracks", headers=_auth(token))
    csv_response = jobs_client.get(f"/api/jobs/{job_id}/download/csv", headers=_auth(token))
    json_response = jobs_client.get(f"/api/jobs/{job_id}/download/json", headers=_auth(token))

    assert summary_response.status_code == 200
    assert summary_response.json()["summary"]["total_detections"] == 0
    assert summary_response.json()["summary"]["average_confidence"] is None
    assert detections_response.status_code == 200
    assert detections_response.json()["items"] == []
    assert tracks_response.status_code == 200
    assert tracks_response.json()["items"] == []
    assert csv_response.status_code == 200
    assert json_response.status_code == 200
