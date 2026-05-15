from __future__ import annotations

import base64
import csv
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.passwords import hash_password
from app.db.models import Base, User
from app.db.session import get_engine
from app.main import create_app

ROOT = Path(__file__).resolve().parents[2]
CV_PATH = ROOT / "cv"
if str(CV_PATH) not in sys.path:
    sys.path.insert(0, str(CV_PATH))

from aerovision_worker import video_processing  # noqa: E402
from aerovision_worker.main import run_poll_iteration  # noqa: E402
from aerovision_worker.model_runtime import ModelRuntime  # noqa: E402
from aerovision_worker.settings import WorkerSettings  # noqa: E402

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/"
    "AAX+Av4N70a4AAAAAElFTkSuQmCC"
)

DEFAULT_POSTGRES_URL = (
    "postgresql+psycopg://aerovision:change-me-postgres-password@localhost:5432/aerovision"
)


FORBIDDEN_RESPONSE_TERMS = [
    "targeting",
    "navigation",
    "interception",
    "geospatial",
    "engagement",
    "payload",
    "weapon",
    "motor",
    "autopilot",
    "traceback",
]


@pytest.fixture
def phase23_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    base_url = _postgres_base_url()
    admin_engine = create_engine(
        base_url,
        isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 2},
    )
    try:
        with admin_engine.connect() as connection:
            connection.execute(text("select 1"))
    except OperationalError as exc:
        admin_engine.dispose()
        pytest.skip(f"PostgreSQL unavailable for Phase 23 smoke: {exc}")

    schema = f"phase23_{uuid4().hex}"
    database_url = _url_with_search_path(base_url, schema)
    storage_root = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))
    monkeypatch.setenv("MODELS_ROOT", str(storage_root / "models"))
    monkeypatch.setenv("CV_DEVICE", "cpu")
    monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "1")
    monkeypatch.setenv("MAX_VIDEO_SIZE_MB", "1")
    monkeypatch.delenv("ACTIVE_MODEL_ID", raising=False)
    get_engine.cache_clear()
    with admin_engine.begin() as connection:
        connection.execute(text(f'create schema "{schema}"'))
    engine = get_engine()
    Base.metadata.create_all(engine)

    try:
        with TestClient(create_app()) as client:
            yield client
    finally:
        get_engine().dispose()
        get_engine.cache_clear()
        with admin_engine.begin() as connection:
            connection.execute(text(f'drop schema if exists "{schema}" cascade'))
        admin_engine.dispose()


def _postgres_base_url() -> str:
    base_url = os.getenv("POSTGRES_TEST_DATABASE_URL") or DEFAULT_POSTGRES_URL
    return base_url.replace("@postgres:", "@localhost:")


def _url_with_search_path(base_url: str, schema: str) -> str:
    parts = urlsplit(base_url)
    separator = "&" if parts.query else ""
    query = f"{parts.query}{separator}options={quote(f'-csearch_path={schema}')}"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def _create_admin() -> None:
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        session.add(
            User(
                email="admin@example.local",
                password_hash=hash_password("admin-secret-value"),
                role="admin",
                is_active=True,
            )
        )
        session.commit()


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _register_user(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "user-secret-value"},
    )
    assert response.status_code == 201, response.text
    return _login(client, email, "user-secret-value")


def _write_weights(storage_root: Path, relative_path: str) -> None:
    path = storage_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fake-weights")


def _register_active_model(client: TestClient, token: str, storage_root: Path) -> dict[str, object]:
    weights_path = "models/phase23-yolo26s/weights.pt"
    _write_weights(storage_root, weights_path)
    response = client.post(
        "/api/models",
        headers=_auth(token),
        json={
            "name": "YOLO26s Phase 23 smoke",
            "model_family": "YOLO26",
            "variant": "s",
            "weights_path": weights_path,
            "dataset_name": "Seraphim",
            "dataset_split_description": "Phase 23 smoke fixture",
            "metrics_json": {"map50": 0.7},
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _upload_image(client: TestClient, token: str, filename: str = "drone.png") -> dict[str, object]:
    response = client.post(
        "/api/media",
        headers=_auth(token),
        files={"file": (filename, PNG_1X1, "image/png")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _upload_video(client: TestClient, token: str, tmp_path: Path) -> dict[str, object]:
    video_path = tmp_path / "fixture.mp4"
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10.0,
        (32, 24),
    )
    if not writer.isOpened():
        pytest.skip("OpenCV MP4 writer is not available")
    for index in range(3):
        frame = np.full((24, 32, 3), 30 + index * 20, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    response = client.post(
        "/api/media",
        headers=_auth(token),
        files={"file": ("drone.mp4", video_path.read_bytes(), "video/mp4")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_job(client: TestClient, token: str, media_id: str) -> str:
    response = client.post("/api/jobs", headers=_auth(token), json={"media_id": media_id})
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "queued"
    return str(response.json()["id"])


def _worker_settings(storage_root: Path) -> WorkerSettings:
    return WorkerSettings(
        database_url=os.environ["DATABASE_URL"],
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
        cv_device="cpu",
    )


def _worker_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)


def _model_runtime(storage_root: Path, detections_by_call: list[list[list[float]]]) -> ModelRuntime:
    fake_model = FakeImageModel(detections_by_call)
    return _runtime_for_fake_model(storage_root, fake_model)


def _video_model_runtime(
    storage_root: Path,
    detections_by_frame: list[list[list[float]]],
) -> ModelRuntime:
    return _runtime_for_fake_model(storage_root, FakeTrackModel(detections_by_frame))


def _runtime_for_fake_model(storage_root: Path, fake_model: object) -> ModelRuntime:
    return ModelRuntime(
        settings=_worker_settings(storage_root),
        selected_device="cpu",
        model_loader=lambda _weights_path: fake_model,
    )


def _poll_once(storage_root: Path, runtime: ModelRuntime) -> None:
    claimed = run_poll_iteration(
        _worker_settings(storage_root),
        _worker_session_factory(),
        worker_id="phase23-worker",
        model_runtime=runtime,
    )
    assert claimed is True


def _assert_safe_response_text(response_text: str, storage_root: Path) -> None:
    lowered = response_text.lower()
    assert str(storage_root).lower() not in lowered
    for term in FORBIDDEN_RESPONSE_TERMS:
        assert term not in lowered


def _assert_cross_owner_denied(client: TestClient, token: str, job_id: str) -> None:
    routes = [
        f"/api/jobs/{job_id}",
        f"/api/jobs/{job_id}/summary",
        f"/api/jobs/{job_id}/detections",
        f"/api/jobs/{job_id}/tracks",
        f"/api/jobs/{job_id}/result",
        f"/api/jobs/{job_id}/download/media",
        f"/api/jobs/{job_id}/download/csv",
        f"/api/jobs/{job_id}/download/json",
    ]
    for route in routes:
        response = client.get(route, headers=_auth(token))
        assert response.status_code == 404, route


class FakeImageModel:
    def __init__(self, detections_by_call: list[list[list[float]]]) -> None:
        self._detections_by_call = detections_by_call
        self._call_index = 0

    def to(self, _device: str):
        return self

    def __call__(self, _image, **_kwargs):
        detections = self._detections_by_call[self._call_index]
        self._call_index += 1
        boxes = SimpleNamespace(
            xyxy=SimpleArray([row[:4] for row in detections]),
            conf=SimpleArray([row[4] for row in detections]),
            cls=SimpleArray([row[5] for row in detections]),
        )
        return [SimpleNamespace(boxes=boxes, speed={"inference": 11.0})]


class FakeTrackModel:
    def __init__(self, detections_by_frame: list[list[list[float]]]) -> None:
        self._detections_by_frame = detections_by_frame
        self._frame_index = 0

    def to(self, _device: str):
        return self

    def track(self, _frame, **_kwargs):
        detections = self._detections_by_frame[self._frame_index]
        self._frame_index += 1
        boxes = SimpleNamespace(
            xyxy=SimpleArray([row[:4] for row in detections]),
            conf=SimpleArray([row[4] for row in detections]),
            cls=SimpleArray([row[5] for row in detections]),
            id=SimpleArray([row[6] for row in detections]),
        )
        return [SimpleNamespace(boxes=boxes)]


class SimpleArray:
    def __init__(self, value) -> None:
        self._value = value

    def cpu(self):
        return self

    def numpy(self):
        return np.array(self._value, dtype=float)


def test_phase23_image_and_no_detection_smoke_through_backend_worker_and_api(
    phase23_client: TestClient,
    tmp_path: Path,
) -> None:
    storage_root = tmp_path / "storage"
    _create_admin()
    admin_token = _login(phase23_client, "admin@example.local", "admin-secret-value")
    owner_token = _register_user(phase23_client, "owner@example.local")
    other_token = _register_user(phase23_client, "other@example.local")
    _register_active_model(phase23_client, admin_token, storage_root)
    runtime = _model_runtime(
        storage_root,
        [
            [[0, 0, 1, 1, 0.92, 0]],
            [],
        ],
    )

    detected_media = _upload_image(phase23_client, owner_token, "detected.png")
    detected_job_id = _create_job(phase23_client, owner_token, str(detected_media["id"]))
    _poll_once(storage_root, runtime)

    detail = phase23_client.get(f"/api/jobs/{detected_job_id}", headers=_auth(owner_token))
    summary = phase23_client.get(
        f"/api/jobs/{detected_job_id}/summary",
        headers=_auth(owner_token),
    )
    detections = phase23_client.get(
        f"/api/jobs/{detected_job_id}/detections",
        headers=_auth(owner_token),
    )
    tracks = phase23_client.get(
        f"/api/jobs/{detected_job_id}/tracks",
        headers=_auth(owner_token),
    )
    result = phase23_client.get(
        f"/api/jobs/{detected_job_id}/result",
        headers=_auth(owner_token),
    )
    downloads = {
        "media": phase23_client.get(
            f"/api/jobs/{detected_job_id}/download/media",
            headers=_auth(owner_token),
        ),
        "csv": phase23_client.get(
            f"/api/jobs/{detected_job_id}/download/csv",
            headers=_auth(owner_token),
        ),
        "json": phase23_client.get(
            f"/api/jobs/{detected_job_id}/download/json",
            headers=_auth(owner_token),
        ),
    }

    for response in [detail, summary, detections, tracks, result, *downloads.values()]:
        assert response.status_code == 200, response.text
        _assert_safe_response_text(response.text, storage_root)
    assert detail.json()["status"] == "completed"
    assert detail.json()["progress_percent"] == 100
    assert summary.json()["summary"]["total_detections"] == 1
    assert detections.json()["total"] == 1
    detection = detections.json()["items"][0]
    assert detection["frame_index"] == 0
    assert detection["timestamp_ms"] == 0
    assert detection["track_id"] is None
    assert tracks.json()["items"] == []
    assert result.json()["media"]["available"] is True
    assert result.json()["csv"]["available"] is True
    assert result.json()["json"]["available"] is True
    assert downloads["media"].content
    csv_rows = list(csv.DictReader(downloads["csv"].text.splitlines()))
    assert len(csv_rows) == 1
    exported_json = downloads["json"].json()
    assert len(exported_json["detections"]) == 1
    assert exported_json["tracks"] == []
    _assert_cross_owner_denied(phase23_client, other_token, detected_job_id)

    empty_media = _upload_image(phase23_client, owner_token, "empty.png")
    empty_job_id = _create_job(phase23_client, owner_token, str(empty_media["id"]))
    _poll_once(storage_root, runtime)

    empty_summary = phase23_client.get(
        f"/api/jobs/{empty_job_id}/summary",
        headers=_auth(owner_token),
    )
    empty_detections = phase23_client.get(
        f"/api/jobs/{empty_job_id}/detections",
        headers=_auth(owner_token),
    )
    empty_tracks = phase23_client.get(
        f"/api/jobs/{empty_job_id}/tracks",
        headers=_auth(owner_token),
    )
    empty_media_download = phase23_client.get(
        f"/api/jobs/{empty_job_id}/download/media",
        headers=_auth(owner_token),
    )
    empty_csv = phase23_client.get(
        f"/api/jobs/{empty_job_id}/download/csv",
        headers=_auth(owner_token),
    )
    empty_json = phase23_client.get(
        f"/api/jobs/{empty_job_id}/download/json",
        headers=_auth(owner_token),
    )

    for response in [
        empty_summary,
        empty_detections,
        empty_tracks,
        empty_media_download,
        empty_csv,
        empty_json,
    ]:
        assert response.status_code == 200, response.text
        _assert_safe_response_text(response.text, storage_root)
    assert empty_summary.json()["summary"]["total_detections"] == 0
    assert empty_summary.json()["summary"]["frames_with_detections"] == 0
    assert empty_summary.json()["summary"]["average_confidence"] is None
    assert empty_summary.json()["summary"]["maximum_confidence"] is None
    assert empty_detections.json()["items"] == []
    assert empty_tracks.json()["items"] == []
    assert empty_media_download.content
    assert list(csv.DictReader(empty_csv.text.splitlines())) == []
    assert empty_json.json()["detections"] == []
    assert empty_json.json()["tracks"] == []


def test_phase23_missing_model_file_marks_job_failed_with_safe_api_payload(
    phase23_client: TestClient,
    tmp_path: Path,
) -> None:
    storage_root = tmp_path / "storage"
    _create_admin()
    admin_token = _login(phase23_client, "admin@example.local", "admin-secret-value")
    owner_token = _register_user(phase23_client, "owner@example.local")
    model = _register_active_model(phase23_client, admin_token, storage_root)
    (storage_root / str(model["weights_path"])).unlink()
    media = _upload_image(phase23_client, owner_token, "missing-model.png")
    job_id = _create_job(phase23_client, owner_token, str(media["id"]))

    _poll_once(
        storage_root,
        ModelRuntime(settings=_worker_settings(storage_root), selected_device="cpu"),
    )

    detail = phase23_client.get(f"/api/jobs/{job_id}", headers=_auth(owner_token))
    result = phase23_client.get(f"/api/jobs/{job_id}/result", headers=_auth(owner_token))

    assert detail.status_code == 200, detail.text
    assert result.status_code == 200, result.text
    assert detail.json()["status"] == "failed"
    assert detail.json()["error_message"] == "Model weights file is missing"
    assert result.json()["status"] == "failed"
    _assert_safe_response_text(detail.text, storage_root)
    _assert_safe_response_text(result.text, storage_root)


def test_phase23_video_smoke_processes_tracks_and_downloads_through_api(
    phase23_client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    _create_admin()
    admin_token = _login(phase23_client, "admin@example.local", "admin-secret-value")
    owner_token = _register_user(phase23_client, "owner@example.local")
    other_token = _register_user(phase23_client, "other@example.local")
    _register_active_model(phase23_client, admin_token, storage_root)
    runtime = _video_model_runtime(
        storage_root,
        [
            [[2, 3, 18, 14, 0.9, 0, 7]],
            [[3, 4, 19, 15, 0.8, 0, 7]],
            [[4, 5, 20, 16, 0.7, 0, np.nan]],
        ],
    )
    media = _upload_video(phase23_client, owner_token, tmp_path)
    job_id = _create_job(phase23_client, owner_token, str(media["id"]))

    def fake_finalize(source_path: Path, final_path: Path) -> None:
        final_path.write_bytes(source_path.read_bytes())
        source_path.unlink()

    monkeypatch.setattr(video_processing, "finalize_browser_playable_mp4", fake_finalize)

    _poll_once(storage_root, runtime)

    detail = phase23_client.get(f"/api/jobs/{job_id}", headers=_auth(owner_token))
    summary = phase23_client.get(f"/api/jobs/{job_id}/summary", headers=_auth(owner_token))
    detections = phase23_client.get(f"/api/jobs/{job_id}/detections", headers=_auth(owner_token))
    tracks = phase23_client.get(f"/api/jobs/{job_id}/tracks", headers=_auth(owner_token))
    result = phase23_client.get(f"/api/jobs/{job_id}/result", headers=_auth(owner_token))
    media_download = phase23_client.get(
        f"/api/jobs/{job_id}/download/media",
        headers=_auth(owner_token),
    )
    csv_download = phase23_client.get(
        f"/api/jobs/{job_id}/download/csv",
        headers=_auth(owner_token),
    )
    json_download = phase23_client.get(
        f"/api/jobs/{job_id}/download/json",
        headers=_auth(owner_token),
    )

    for response in [
        detail,
        summary,
        detections,
        tracks,
        result,
        media_download,
        csv_download,
        json_download,
    ]:
        assert response.status_code == 200, response.text
        _assert_safe_response_text(response.text, storage_root)
    assert detail.json()["status"] == "completed"
    assert detail.json()["progress_percent"] == 100
    assert summary.json()["summary"]["total_detections"] == 3
    assert summary.json()["summary"]["unique_track_ids"] == 1
    assert detections.json()["total"] == 3
    assert detections.json()["items"][0]["track_id"] == 7
    assert detections.json()["items"][2]["track_id"] is None
    assert tracks.json()["total"] == 1
    assert tracks.json()["items"][0]["track_id"] == 7
    assert result.json()["media"]["available"] is True
    assert result.json()["csv"]["available"] is True
    assert result.json()["json"]["available"] is True
    assert media_download.content
    assert len(list(csv.DictReader(csv_download.text.splitlines()))) == 3
    export = json.loads(json_download.text)
    assert len(export["detections"]) == 3
    assert len(export["tracks"]) == 1
    _assert_cross_owner_denied(phase23_client, other_token, job_id)
