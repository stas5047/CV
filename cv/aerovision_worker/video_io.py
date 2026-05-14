from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np

from aerovision_worker.settings import WorkerSettings
from aerovision_worker.storage_paths import safe_join_storage_path
from aerovision_worker.video_types import VideoJob, VideoProcessingError


def source_path(settings: WorkerSettings, stored_path: str) -> Path:
    try:
        return safe_join_storage_path(settings.storage_root, stored_path)
    except ValueError as exc:
        raise VideoProcessingError("Source video path is unsafe") from exc


def capture_metadata(capture, job: VideoJob) -> dict[str, int | float]:
    fps = _positive_float(capture.get(cv2.CAP_PROP_FPS)) or job.db_fps or 30.0
    frame_count = _positive_int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or job.db_frame_count or 0
    width = _positive_int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or job.db_width or 0
    height = _positive_int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or job.db_height or 0
    return {"fps": fps, "frame_count": frame_count, "width": width, "height": height}


def metadata_from_first_frame(
    metadata: dict[str, int | float],
    frame: np.ndarray,
) -> dict[str, int | float]:
    frame_height, frame_width = frame.shape[:2]
    return {
        "fps": float(metadata["fps"]),
        "frame_count": int(metadata["frame_count"]),
        "width": int(metadata["width"]) or int(frame_width),
        "height": int(metadata["height"]) or int(frame_height),
    }


def open_writer(path: Path, fps: float, width: int, height: int):
    try:
        writer = cv2.VideoWriter(
            str(path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps if fps > 0 else 30.0,
            (width, height),
        )
    except Exception as exc:
        raise VideoProcessingError("Annotated video output could not be created") from exc
    if not writer.isOpened():
        raise VideoProcessingError("Annotated video output could not be created")
    return writer


def optional_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def optional_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _positive_int(value: Any) -> int | None:
    return optional_int(value)


def _positive_float(value: Any) -> float | None:
    return optional_float(value)
