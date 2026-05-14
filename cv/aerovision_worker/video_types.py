from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SUPPORTED_TRACKERS = {"bytetrack": "bytetrack.yaml", "botsort": "botsort.yaml"}


@dataclass(frozen=True)
class VideoJob:
    id: str
    media_id: str
    media_type: str
    stored_path: str
    original_filename: str
    file_size_bytes: int
    db_width: int | None
    db_height: int | None
    db_frame_count: int | None
    db_fps: float | None
    db_duration_seconds: float | None
    input_params: dict[str, Any]


@dataclass(frozen=True)
class VideoDetection:
    job_id: str
    media_id: str
    frame_index: int
    timestamp_ms: int
    class_id: int
    class_name: str
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    frame_width: int
    frame_height: int
    track_id: int | None = None


@dataclass(frozen=True)
class TrackSummary:
    job_id: str
    track_id: int
    class_name: str
    first_frame_index: int
    last_frame_index: int
    frames_count: int
    average_confidence: float | None
    max_confidence: float | None


class VideoProcessingError(RuntimeError):
    pass
