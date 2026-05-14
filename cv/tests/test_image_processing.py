from __future__ import annotations

import csv
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker import image_processing
from aerovision_worker.image_processing import process_image_job
from aerovision_worker.model_runtime import LoadedModel, ModelMetadata
from aerovision_worker.settings import WorkerSettings

FORBIDDEN_EXPORT_TERMS = [
    "targeting",
    "navigation",
    "interception",
    "geospatial",
    "engagement",
    "payload",
    "weapon",
    "motor",
    "autopilot",
]


def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                create table media_files (
                    id text primary key,
                    user_id text not null,
                    original_filename text not null,
                    stored_path text not null,
                    media_type text not null,
                    mime_type text not null,
                    file_size_bytes integer not null,
                    width integer null,
                    height integer null,
                    frame_count integer null,
                    fps real null,
                    duration_seconds real null,
                    deleted_at timestamp null,
                    created_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table model_versions (
                    id text primary key,
                    name text not null,
                    model_family text not null,
                    variant text null,
                    weights_path text not null,
                    is_active boolean not null,
                    created_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table processing_jobs (
                    id text primary key,
                    user_id text not null,
                    media_file_id text not null,
                    model_version_id text null,
                    status text not null,
                    input_params_json json null,
                    summary_json json null,
                    result_media_path text null,
                    csv_path text null,
                    json_path text null,
                    error_message text null,
                    progress_percent integer not null default 0,
                    last_heartbeat_at timestamp null,
                    locked_by text null,
                    locked_at timestamp null,
                    retry_count integer not null default 0,
                    started_at timestamp null,
                    completed_at timestamp null,
                    deleted_at timestamp null,
                    created_at timestamp not null,
                    updated_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table detections (
                    id text primary key,
                    job_id text not null,
                    media_file_id text not null,
                    frame_index integer not null,
                    timestamp_ms integer not null,
                    class_id integer not null,
                    class_name text not null,
                    confidence real not null,
                    bbox_x1 real not null,
                    bbox_y1 real not null,
                    bbox_x2 real not null,
                    bbox_y2 real not null,
                    frame_width integer not null,
                    frame_height integer not null,
                    track_id integer null,
                    created_at timestamp not null
                )
                """
            )
        )
    return factory


def write_image(storage_root: Path, relative_path: str, image: np.ndarray | None = None) -> Path:
    path = storage_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    image = image if image is not None else np.full((20, 30, 3), 255, dtype=np.uint8)
    assert cv2.imwrite(str(path), image)
    return path


def insert_image_job(
    factory: sessionmaker[Session],
    *,
    storage_root: Path,
    job_id: str = "job-1",
    media_id: str = "media-1",
    stored_path: str = "uploads/user-1/media-1.png",
    original_filename: str = "drone.png",
    input_params: dict[str, object] | None = None,
) -> None:
    now = datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    source_path = storage_root / stored_path
    file_size = source_path.stat().st_size if source_path.exists() else 123
    with factory.begin() as session:
        session.execute(
            text(
                """
                insert into media_files (
                    id, user_id, original_filename, stored_path, media_type, mime_type,
                    file_size_bytes, width, height, frame_count, fps, duration_seconds,
                    deleted_at, created_at
                )
                values (
                    :id, 'user-1', :original_filename, :stored_path, 'image', 'image/png',
                    :file_size_bytes, 30, 20, 1, null, null, null, :now
                )
                """
            ),
            {
                "id": media_id,
                "original_filename": original_filename,
                "stored_path": stored_path,
                "file_size_bytes": file_size,
                "now": now,
            },
        )
        session.execute(
            text(
                """
                insert into model_versions (
                    id, name, model_family, variant, weights_path, is_active, created_at
                )
                values (
                    'model-1', 'YOLO26s demo', 'YOLO26', 's',
                    'models/model-1/weights.pt', true, :now
                )
                """
            ),
            {"now": now},
        )
        session.execute(
            text(
                """
                insert into processing_jobs (
                    id, user_id, media_file_id, model_version_id, status, input_params_json,
                    progress_percent, locked_by, locked_at, started_at,
                    created_at, updated_at
                )
                values (
                    :id, 'user-1', :media_id, 'model-1', 'processing', :input_params,
                    10, 'worker-a', :now, :now, :now, :now
                )
                """
            ),
            {
                "id": job_id,
                "media_id": media_id,
                "input_params": json.dumps(
                    input_params
                    or {
                        "confidence_threshold": 0.25,
                        "iou_threshold": 0.45,
                        "image_size": 640,
                        "tracker_type": "bytetrack",
                    }
                ),
                "now": now,
            },
        )


def loaded_model(detections: list[list[float]]) -> LoadedModel:
    model = FakeModel(detections)
    return LoadedModel(
        metadata=ModelMetadata(
            id="model-1",
            name="YOLO26s demo",
            model_family="YOLO26",
            variant="s",
            weights_path="models/model-1/weights.pt",
        ),
        model=model,
        device="cpu",
    )


class FakeModel:
    def __init__(self, detections: list[list[float]]) -> None:
        self.calls: list[dict[str, object]] = []
        self._detections = detections

    def __call__(self, image, **kwargs):
        self.calls.append(kwargs)
        boxes = SimpleNamespace(
            xyxy=SimpleArray([row[:4] for row in self._detections]),
            conf=SimpleArray([row[4] for row in self._detections]),
            cls=SimpleArray([row[5] for row in self._detections]),
        )
        return [SimpleNamespace(boxes=boxes, speed={"inference": 12.5})]


class SimpleArray:
    def __init__(self, value) -> None:
        self._value = value

    def cpu(self):
        return self

    def numpy(self):
        return np.array(self._value, dtype=float)


def fetch_job(factory: sessionmaker[Session], job_id: str = "job-1") -> dict[str, object]:
    with factory() as session:
        row = session.execute(
            text("select * from processing_jobs where id = :id"), {"id": job_id}
        ).mappings().one()
    job = dict(row)
    if isinstance(job.get("summary_json"), str):
        job["summary_json"] = json.loads(job["summary_json"])
    return job


def fetch_detections(factory: sessionmaker[Session]) -> list[dict[str, object]]:
    with factory() as session:
        rows = (
            session.execute(text("select * from detections order by created_at"))
            .mappings()
            .all()
        )
    return [dict(row) for row in rows]


def worker_settings(storage_root: Path) -> WorkerSettings:
    return WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
    )


def test_process_image_job_completes_with_detection_exports_and_relative_paths(
    tmp_path: Path,
) -> None:
    storage_root = tmp_path / "storage"
    weights = storage_root / "models" / "model-1" / "weights.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"fake-weights")
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    detections = fetch_detections(factory)
    assert job["status"] == "completed"
    assert job["progress_percent"] == 100
    assert job["result_media_path"] == "results/job-1/annotated.png"
    assert job["csv_path"] == "results/job-1/detections.csv"
    assert job["json_path"] == "results/job-1/detections.json"
    assert (storage_root / job["result_media_path"]).is_file()
    assert (storage_root / job["csv_path"]).is_file()
    assert (storage_root / job["json_path"]).is_file()
    assert len(detections) == 1


def test_process_image_job_logs_lifecycle_without_paths(tmp_path: Path, caplog) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    caplog.set_level(logging.INFO, logger="aerovision_worker.image_processing")

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([]),
    )

    log_text = caplog.text
    assert "image_job_started job_id=job-1" in log_text
    assert "image_exports_written job_id=job-1 csv=true json=true" in log_text
    assert "image_job_completed job_id=job-1 detections=0 duration_ms=" in log_text
    assert str(storage_root) not in log_text


def test_process_image_job_stores_image_detection_invariants(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[-5, 3, 40, 14, 0.9, 0]]),
    )

    detection = fetch_detections(factory)[0]
    assert detection["frame_index"] == 0
    assert detection["timestamp_ms"] == 0
    assert detection["track_id"] is None
    assert detection["class_name"] == "drone"
    assert detection["bbox_x1"] == 0
    assert detection["bbox_y1"] == 3
    assert detection["bbox_x2"] == 30
    assert detection["bbox_y2"] == 14
    assert detection["frame_width"] == 30
    assert detection["frame_height"] == 20


def test_process_image_job_completes_no_detection_with_empty_exports(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([]),
    )

    job = fetch_job(factory)
    summary = job["summary_json"]
    with (storage_root / job["csv_path"]).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    export = json.loads((storage_root / job["json_path"]).read_text(encoding="utf-8"))
    assert job["status"] == "completed"
    assert fetch_detections(factory) == []
    assert summary["total_detections"] == 0
    assert summary["frames_with_detections"] == 0
    assert summary["average_confidence"] is None
    assert summary["maximum_confidence"] is None
    assert rows == []
    assert export["summary"]["total_detections"] == 0
    assert export["summary"]["frames_with_detections"] == 0
    assert export["summary"]["average_confidence"] is None
    assert export["summary"]["maximum_confidence"] is None
    assert export["detections"] == []


@pytest.mark.parametrize(
    ("stored_path", "write_source", "expected_error"),
    [
        ("uploads/user-1/missing.png", False, "Source image file is missing"),
        ("uploads/user-1/media-1.png", "corrupt", "Source image could not be decoded"),
    ],
)
def test_process_image_job_fails_safe_for_missing_or_corrupt_source(
    tmp_path: Path,
    caplog,
    stored_path: str,
    write_source: bool | str,
    expected_error: str,
) -> None:
    storage_root = tmp_path / "storage"
    if write_source == "corrupt":
        path = storage_root / stored_path
        path.parent.mkdir(parents=True)
        path.write_text("not an image", encoding="utf-8")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root, stored_path=stored_path)
    settings = worker_settings(storage_root)
    caplog.set_level(logging.INFO, logger="aerovision_worker.image_processing")

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == expected_error
    assert str(storage_root) not in job["error_message"]
    assert f"image_job_failed job_id=job-1 error={expected_error}" in caplog.text
    assert str(storage_root) not in caplog.text


def test_process_image_job_fails_safe_for_unsafe_stored_source_path(
    tmp_path: Path,
) -> None:
    storage_root = tmp_path / "storage"
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root, stored_path="../escape.png")
    settings = worker_settings(storage_root)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "Source image path is unsafe"
    assert str(storage_root) not in job["error_message"]


def test_process_image_job_fails_safe_when_output_directory_cannot_be_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    original_mkdir = image_processing.Path.mkdir

    def failing_mkdir(path: Path, *args, **kwargs):
        if path.name == "job-1":
            raise OSError("blocked")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(image_processing.Path, "mkdir", failing_mkdir)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "Result output directory could not be created"
    assert str(storage_root) not in job["error_message"]


def test_process_image_job_fails_safe_when_annotated_output_cannot_be_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    monkeypatch.setattr(image_processing.cv2, "imwrite", lambda *args, **kwargs: False)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "Annotated image output could not be created"
    assert str(storage_root) not in job["error_message"]


def test_process_image_job_fails_safe_when_csv_export_cannot_be_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    original_open = image_processing.Path.open

    def failing_open(path: Path, *args, **kwargs):
        if path.name == "detections.csv":
            raise OSError("blocked")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(image_processing.Path, "open", failing_open)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "CSV export could not be created"
    assert str(storage_root) not in job["error_message"]


def test_process_image_job_fails_safe_when_json_export_cannot_be_created(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    original_write_text = image_processing.Path.write_text

    def failing_write_text(path: Path, *args, **kwargs):
        if path.name == "detections.json":
            raise OSError("blocked")
        return original_write_text(path, *args, **kwargs)

    monkeypatch.setattr(image_processing.Path, "write_text", failing_write_text)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "JSON export could not be created"
    assert str(storage_root) not in job["error_message"]


def test_process_image_job_writes_csv_and_json_contract(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_image(storage_root, "uploads/user-1/media-1.png")
    factory = session_factory()
    insert_image_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    process_image_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[2, 3, 18, 14, 0.9, 0]]),
    )

    job = fetch_job(factory)
    with (storage_root / job["csv_path"]).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "job_id",
            "media_id",
            "frame_index",
            "timestamp_ms",
            "class_id",
            "class_name",
            "confidence",
            "bbox_x1",
            "bbox_y1",
            "bbox_x2",
            "bbox_y2",
            "center_x",
            "center_y",
            "bbox_width",
            "bbox_height",
            "frame_width",
            "frame_height",
            "track_id",
            "model_version",
            "tracker_type",
        ]
        rows = list(reader)
    assert len(rows) == 1
    assert float(rows[0]["center_x"]) == 10.0
    assert float(rows[0]["center_y"]) == 8.5
    assert float(rows[0]["bbox_width"]) == 16.0
    assert float(rows[0]["bbox_height"]) == 11.0
    export = json.loads((storage_root / job["json_path"]).read_text(encoding="utf-8"))
    assert set(export) == {"job", "media", "model", "parameters", "summary", "detections", "tracks"}
    assert export["tracks"] == []
    forbidden = json.dumps(export).lower()
    for term in FORBIDDEN_EXPORT_TERMS:
        assert term not in forbidden
    assert str(storage_root).lower() not in forbidden
