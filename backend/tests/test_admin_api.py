from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import hash_password
from app.db.models import (
    Base,
    Detection,
    ExperimentRun,
    MediaFile,
    ModelVersion,
    ProcessingJob,
    Track,
    User,
)
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture
def admin_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'admin.db'}"
    storage_root = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))
    monkeypatch.setenv("MODELS_ROOT", str(storage_root / "models"))
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
    with sessionmaker(bind=get_engine())() as session:
        user = User(
            email=email,
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


def _create_media(user_id: UUID, *, stored_path: str | None = None) -> UUID:
    media_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            MediaFile(
                id=media_id,
                user_id=user_id,
                original_filename="source.png",
                stored_path=stored_path or f"uploads/{user_id}/{media_id}/original.png",
                media_type="image",
                mime_type="image/png",
                file_size_bytes=128,
                width=640,
                height=480,
                frame_count=1,
            )
        )
        session.commit()
        return media_id


def _create_model(*, active: bool = False, weights_path: str | None = None) -> UUID:
    model_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            ModelVersion(
                id=model_id,
                name="YOLO26s",
                model_family="YOLO26",
                variant="s",
                weights_path=weights_path or f"models/{model_id}/weights.pt",
                metrics_json={},
                is_active=active,
            )
        )
        session.commit()
        return model_id


def _create_job(
    user_id: UUID,
    media_id: UUID,
    model_id: UUID,
    *,
    status: str = "queued",
    result_media_path: str | None = None,
    csv_path: str | None = None,
    json_path: str | None = None,
) -> UUID:
    job_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            ProcessingJob(
                id=job_id,
                user_id=user_id,
                media_file_id=media_id,
                model_version_id=model_id,
                status=status,
                input_params_json={"frame_stride": 1},
                summary_json={"total_detections": 1} if status == "completed" else None,
                result_media_path=result_media_path,
                csv_path=csv_path,
                json_path=json_path,
                progress_percent=100 if status == "completed" else 0,
                retry_count=0,
            )
        )
        session.commit()
        return job_id


def _add_detection_and_track(job_id: UUID, media_id: UUID) -> None:
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            Detection(
                id=uuid4(),
                job_id=job_id,
                media_file_id=media_id,
                frame_index=0,
                timestamp_ms=0,
                class_id=0,
                class_name="drone",
                confidence=0.9,
                bbox_x1=1,
                bbox_y1=2,
                bbox_x2=3,
                bbox_y2=4,
                frame_width=640,
                frame_height=480,
            )
        )
        session.add(
            Track(
                id=uuid4(),
                job_id=job_id,
                track_id=1,
                class_name="drone",
                first_frame_index=0,
                last_frame_index=1,
                frames_count=2,
            )
        )
        session.commit()


def _write_storage_file(relative_path: str, content: bytes = b"x") -> Path:
    full_path = Path(Settings().storage_root) / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(content)
    return full_path


def test_admin_routes_reject_guest_regular_and_inactive_admin(
    admin_client: TestClient,
) -> None:
    user_id = _create_user("user@example.local", "user-secret-value")
    inactive_admin_id = _create_user(
        "inactive-admin@example.local",
        "admin-secret-value",
        role="admin",
        is_active=False,
    )
    user_token = _login(admin_client, "user@example.local", "user-secret-value")
    inactive_token = jwt.encode(
        {"sub": str(inactive_admin_id)},
        Settings().jwt_secret_key,
        algorithm="HS256",
    )

    assert admin_client.get("/api/admin/stats").status_code == 401
    assert admin_client.get("/api/admin/users", headers=_auth(user_token)).status_code == 403
    assert (
        admin_client.post(
            "/api/admin/storage/cleanup",
            headers=_auth(user_token),
            json={},
        ).status_code
        == 403
    )
    assert (
        admin_client.get("/api/admin/jobs", headers=_auth(inactive_token)).status_code == 401
    )
    assert user_id is not None


def test_admin_stats_users_and_jobs_are_global_and_safe(admin_client: TestClient) -> None:
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    user_id = _create_user("user@example.local", "user-secret-value")
    admin_token = _login(admin_client, "admin@example.local", "admin-secret-value")
    model_id = _create_model(active=True)
    admin_media_id = _create_media(admin_id)
    user_media_id = _create_media(user_id)
    admin_job_id = _create_job(admin_id, admin_media_id, model_id, status="queued")
    user_job_id = _create_job(user_id, user_media_id, model_id, status="completed")
    _add_detection_and_track(user_job_id, user_media_id)

    stats_response = admin_client.get("/api/admin/stats", headers=_auth(admin_token))
    users_response = admin_client.get("/api/admin/users", headers=_auth(admin_token))
    jobs_response = admin_client.get("/api/admin/jobs", headers=_auth(admin_token))

    assert stats_response.status_code == 200, stats_response.text
    stats = stats_response.json()
    assert stats["users"]["total"] == 2
    assert stats["users"]["admins"] == 1
    assert stats["media"]["total"] == 2
    assert stats["jobs"]["total"] == 2
    assert stats["jobs"]["by_status"]["completed"] == 1
    assert stats["detections"]["total"] == 1
    assert stats["tracks"]["total"] == 1
    assert stats["models"]["active"] == 1
    assert users_response.status_code == 200, users_response.text
    assert users_response.json()["total"] == 2
    assert "password_hash" not in users_response.text
    assert "admin-secret-value" not in users_response.text
    assert jobs_response.status_code == 200, jobs_response.text
    returned_ids = {item["id"] for item in jobs_response.json()["items"]}
    assert returned_ids == {str(admin_job_id), str(user_job_id)}
    assert "result_media_path" not in jobs_response.text
    assert str(Path(Settings().storage_root)) not in jobs_response.text


def test_storage_cleanup_deletes_only_unreferenced_temp_files_and_hides_absolute_paths(
    admin_client: TestClient,
) -> None:
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(admin_client, "admin@example.local", "admin-secret-value")
    model_id = _create_model(active=True)
    media_id = _create_media(admin_id, stored_path="uploads/admin/source.png")
    job_id = _create_job(
        admin_id,
        media_id,
        model_id,
        status="completed",
        result_media_path="results/visible/annotated.png",
        csv_path="results/visible/detections.csv",
        json_path="results/visible/detections.json",
    )
    active_card = f"models/{model_id}/model_card.json"
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            ExperimentRun(
                id=uuid4(),
                name="Run",
                experiment_type="model_comparison",
                config_json={},
                artifacts_path="reports/exp-1",
            )
        )
        session.commit()
    protected_files = [
        "uploads/admin/source.png",
        "results/visible/annotated.png",
        "results/visible/detections.csv",
        "results/visible/detections.json",
        f"models/{model_id}/weights.pt",
        active_card,
        "reports/exp-1/metrics.json",
        "results/fresh-unreferenced/keep.csv",
    ]
    for path in protected_files:
        _write_storage_file(path)
    temp_file = _write_storage_file("temp/orphan.tmp")

    dry_run_response = admin_client.post(
        "/api/admin/storage/cleanup",
        headers=_auth(token),
        json={"dry_run": True},
    )

    assert dry_run_response.status_code == 200, dry_run_response.text
    dry_run_body = dry_run_response.json()
    assert dry_run_body["dry_run"] is True
    assert dry_run_body["deleted_files"] == 0
    assert dry_run_body["deleted_by_category"] == {}
    assert dry_run_body["would_delete_files"] == 1
    assert dry_run_body["would_delete_by_category"]["temp"] == 1
    assert temp_file.is_file()
    assert str(Path(Settings().storage_root)) not in dry_run_response.text

    response = admin_client.post("/api/admin/storage/cleanup", headers=_auth(token), json={})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["dry_run"] is False
    assert body["deleted_files"] == 1
    assert body["deleted_by_category"]["temp"] == 1
    assert body["would_delete_files"] == 0
    assert body["would_delete_by_category"] == {}
    assert body["reported_by_category"]["results"] >= 1
    assert not temp_file.exists()
    for path in protected_files:
        assert (Path(Settings().storage_root) / path).is_file()
    assert str(Path(Settings().storage_root)) not in response.text
    assert str(job_id) not in body.get("unsafe_paths", [])
