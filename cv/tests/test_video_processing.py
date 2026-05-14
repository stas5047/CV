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

from aerovision_worker import video_processing
from aerovision_worker.image_processing import CSV_COLUMNS
from aerovision_worker.model_runtime import LoadedModel, ModelMetadata
from aerovision_worker.settings import WorkerSettings
from aerovision_worker.video_processing import process_video_job

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
        connection.execute(
            text(
                """
                create table tracks (
                    id text primary key,
                    job_id text not null,
                    track_id integer not null,
                    class_name text not null,
                    first_frame_index integer not null,
                    last_frame_index integer not null,
                    frames_count integer not null,
                    average_confidence real null,
                    max_confidence real null,
                    created_at timestamp not null
                )
                """
            )
        )
    return factory


def write_video(
    storage_root: Path,
    relative_path: str,
    *,
    frames: int = 3,
    width: int = 32,
    height: int = 24,
    fps: float = 10.0,
) -> Path:
    path = storage_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    assert writer.isOpened()
    for index in range(frames):
        frame = np.full((height, width, 3), 20 + index * 20, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return path


def insert_video_job(
    factory: sessionmaker[Session],
    *,
    storage_root: Path,
    job_id: str = "job-1",
    media_id: str = "media-1",
    stored_path: str = "uploads/user-1/media-1.mp4",
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
                    :id, 'user-1', 'drone.mp4', :stored_path, 'video', 'video/mp4',
                    :file_size_bytes, 32, 24, 3, 10.0, 0.3, null, :now
                )
                """
            ),
            {
                "id": media_id,
                "stored_path": stored_path,
                "file_size_bytes": file_size,
                "now": now,
            },
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


def loaded_model(frames: list[list[list[float]]]) -> LoadedModel:
    return LoadedModel(
        metadata=ModelMetadata(
            id="model-1",
            name="YOLO26s demo",
            model_family="YOLO26",
            variant="s",
            weights_path="models/model-1/weights.pt",
        ),
        model=FakeTrackModel(frames),
        device="cpu",
    )


class FakeTrackModel:
    def __init__(self, frames: list[list[list[float]]]) -> None:
        self.calls: list[dict[str, object]] = []
        self._frames = frames
        self._index = 0

    def track(self, frame, **kwargs):
        self.calls.append(kwargs)
        detections = self._frames[self._index] if self._index < len(self._frames) else []
        self._index += 1
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


def worker_settings(storage_root: Path, **kwargs) -> WorkerSettings:
    return WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        **kwargs,
    )


def fetch_job(factory: sessionmaker[Session], job_id: str = "job-1") -> dict[str, object]:
    with factory() as session:
        row = session.execute(
            text("select * from processing_jobs where id = :id"), {"id": job_id}
        ).mappings().one()
    job = dict(row)
    if isinstance(job.get("summary_json"), str):
        job["summary_json"] = json.loads(job["summary_json"])
    return job


def fetch_rows(factory: sessionmaker[Session], table: str) -> list[dict[str, object]]:
    with factory() as session:
        rows = session.execute(text(f"select * from {table} order by created_at")).mappings().all()
    return [dict(row) for row in rows]


def test_process_video_job_completes_with_detections_tracks_exports_and_progress(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    (storage_root / "models" / "model-1").mkdir(parents=True)
    (storage_root / "models" / "model-1" / "weights.pt").write_bytes(b"weights")
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=3)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root, heartbeat_frames=1, heartbeat_seconds=99)
    model = loaded_model(
        [
            [[2, 3, 18, 14, 0.9, 0, 7]],
            [[3, 4, 19, 15, 0.8, 0, 7]],
            [[4, 5, 20, 16, 0.7, 0, np.nan]],
        ]
    )
    heartbeat_updates: list[int] = []
    original_heartbeat = video_processing.update_job_heartbeat

    def capture_heartbeat(*args, **kwargs):
        heartbeat_updates.append(kwargs["progress_percent"])
        return original_heartbeat(*args, **kwargs)

    monkeypatch.setattr(video_processing, "update_job_heartbeat", capture_heartbeat)

    process_video_job(settings, factory, job_id="job-1", worker_id="worker-a", loaded_model=model)

    job = fetch_job(factory)
    detections = fetch_rows(factory, "detections")
    tracks = fetch_rows(factory, "tracks")
    assert job["status"] == "completed"
    assert job["progress_percent"] == 100
    assert heartbeat_updates
    assert any(progress < 100 for progress in heartbeat_updates)
    assert job["result_media_path"] == "results/job-1/annotated.mp4"
    assert Path(storage_root / job["result_media_path"]).is_file()
    assert len(detections) == 3
    assert detections[0]["frame_index"] == 0
    assert detections[1]["timestamp_ms"] == 100
    assert detections[0]["track_id"] == 7
    assert detections[2]["track_id"] is None
    assert len(tracks) == 1
    assert tracks[0]["track_id"] == 7
    assert tracks[0]["first_frame_index"] == 0
    assert tracks[0]["last_frame_index"] == 1
    assert tracks[0]["frames_count"] == 2
    assert job["summary_json"]["average_fps"] > 0
    assert job["summary_json"]["total_frames_processed"] == 3
    assert job["summary_json"]["total_detections"] == 3

    with (storage_root / job["csv_path"]).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == CSV_COLUMNS
    export = json.loads((storage_root / job["json_path"]).read_text(encoding="utf-8"))
    assert set(export) == {"job", "media", "model", "parameters", "summary", "detections", "tracks"}
    assert len(rows) == 3
    assert float(rows[0]["center_x"]) == 10.0
    assert float(rows[0]["center_y"]) == 8.5
    assert float(rows[0]["bbox_width"]) == 16.0
    assert float(rows[0]["bbox_height"]) == 11.0
    assert export["tracks"][0]["track_id"] == tracks[0]["track_id"]
    assert len(export["tracks"]) == 1
    forbidden = json.dumps(export).lower()
    assert str(storage_root).lower() not in forbidden
    for term in FORBIDDEN_EXPORT_TERMS:
        assert term not in forbidden


def test_process_video_job_logs_lifecycle_without_paths(tmp_path: Path, caplog) -> None:
    storage_root = tmp_path / "storage"
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=1)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)
    caplog.set_level(logging.INFO, logger="aerovision_worker.video_processing")

    process_video_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[]]),
    )

    log_text = caplog.text
    assert "video_job_started job_id=job-1" in log_text
    assert "video_exports_written job_id=job-1 csv=true json=true" in log_text
    assert (
        "video_job_completed job_id=job-1 frames=1 detections=0 tracks=0 duration_ms="
        in log_text
    )
    assert str(storage_root) not in log_text


def test_process_video_job_completes_no_detection_with_empty_exports(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=2)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    process_video_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[], []]),
    )

    job = fetch_job(factory)
    export = json.loads((storage_root / job["json_path"]).read_text(encoding="utf-8"))
    with (storage_root / job["csv_path"]).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert job["status"] == "completed"
    assert fetch_rows(factory, "detections") == []
    assert fetch_rows(factory, "tracks") == []
    assert job["summary_json"]["total_detections"] == 0
    assert job["summary_json"]["frames_with_detections"] == 0
    assert job["summary_json"]["average_confidence"] is None
    assert job["summary_json"]["maximum_confidence"] is None
    assert rows == []
    assert export["summary"]["total_detections"] == 0
    assert export["summary"]["frames_with_detections"] == 0
    assert export["summary"]["average_confidence"] is None
    assert export["summary"]["maximum_confidence"] is None
    assert export["detections"] == []
    assert export["tracks"] == []
    assert job["result_media_path"] == "results/job-1/annotated.mp4"
    assert Path(storage_root / job["result_media_path"]).is_file()


@pytest.mark.parametrize(
    ("stored_path", "write_source", "expected_error"),
    [
        ("uploads/user-1/missing.mp4", False, "Source video file is missing"),
        ("uploads/user-1/media-1.mp4", "corrupt", "Source video could not be opened"),
        ("../escape.mp4", False, "Source video path is unsafe"),
    ],
)
def test_process_video_job_fails_safe_for_bad_sources(
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
        path.write_text("not video", encoding="utf-8")
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root, stored_path=stored_path)
    settings = worker_settings(storage_root)
    caplog.set_level(logging.INFO, logger="aerovision_worker.video_processing")

    process_video_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == expected_error
    assert str(storage_root) not in job["error_message"]
    assert f"video_job_failed job_id=job-1 error={expected_error}" in caplog.text
    assert str(storage_root) not in caplog.text


def test_process_video_job_fails_safe_when_writer_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage_root = tmp_path / "storage"
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=1)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root)
    settings = worker_settings(storage_root)

    class ClosedWriter:
        def isOpened(self):
            return False

        def release(self):
            return None

    monkeypatch.setattr(video_processing.cv2, "VideoWriter", lambda *args, **kwargs: ClosedWriter())

    process_video_job(
        settings,
        factory,
        job_id="job-1",
        worker_id="worker-a",
        loaded_model=loaded_model([[]]),
    )

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "Annotated video output could not be created"
    assert str(storage_root) not in job["error_message"]


def test_process_video_job_fails_safe_when_tracker_runtime_unavailable(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=1)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root, input_params={"tracker_type": "botsort"})
    settings = worker_settings(storage_root)
    model = LoadedModel(
        metadata=ModelMetadata(
            id="model-1",
            name="YOLO26s demo",
            model_family="YOLO26",
            variant="s",
            weights_path="models/model-1/weights.pt",
        ),
        model=object(),
        device="cpu",
    )

    process_video_job(settings, factory, job_id="job-1", worker_id="worker-a", loaded_model=model)

    job = fetch_job(factory)
    assert job["status"] == "failed"
    assert job["error_message"] == "Video tracker runtime is unavailable"
    assert str(storage_root) not in job["error_message"]


def test_process_video_job_passes_botsort_tracker_to_runtime(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    write_video(storage_root, "uploads/user-1/media-1.mp4", frames=1)
    factory = session_factory()
    insert_video_job(factory, storage_root=storage_root, input_params={"tracker_type": "botsort"})
    settings = worker_settings(storage_root)
    model = loaded_model([[]])

    process_video_job(settings, factory, job_id="job-1", worker_id="worker-a", loaded_model=model)

    assert model.model.calls[0]["tracker"] == "botsort.yaml"
    assert model.model.calls[0]["persist"] is True
