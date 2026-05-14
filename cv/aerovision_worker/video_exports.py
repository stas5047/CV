from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from aerovision_worker.image_processing import CSV_COLUMNS
from aerovision_worker.model_runtime import LoadedModel
from aerovision_worker.settings import WorkerSettings
from aerovision_worker.storage_paths import safe_join_storage_path
from aerovision_worker.video_types import (
    TrackSummary,
    VideoDetection,
    VideoJob,
    VideoProcessingError,
)


def result_paths(job_id: str) -> dict[str, str]:
    return {
        "media": f"results/{job_id}/annotated.mp4",
        "csv": f"results/{job_id}/detections.csv",
        "json": f"results/{job_id}/detections.json",
    }


def output_path(settings: WorkerSettings, relative_path: str) -> Path:
    try:
        path = safe_join_storage_path(settings.storage_root, relative_path)
    except ValueError as exc:
        raise VideoProcessingError("Result path is unsafe") from exc
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise VideoProcessingError("Result output directory could not be created") from exc
    return path


def write_csv_export(
    settings: WorkerSettings,
    relative_path: str,
    detections: list[VideoDetection],
    loaded_model: LoadedModel,
    params: dict[str, Any],
) -> None:
    path = output_path(settings, relative_path)
    try:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for detection in detections:
                writer.writerow(export_detection(detection, loaded_model, params))
    except OSError as exc:
        raise VideoProcessingError("CSV export could not be created") from exc


def write_json_export(
    settings: WorkerSettings,
    relative_path: str,
    job: VideoJob,
    loaded_model: LoadedModel,
    params: dict[str, Any],
    summary: dict[str, Any],
    detections: list[VideoDetection],
    tracks: list[TrackSummary],
) -> None:
    path = output_path(settings, relative_path)
    export = {
        "job": {"id": job.id, "status": "completed"},
        "media": {
            "id": job.media_id,
            "media_type": job.media_type,
            "original_filename": job.original_filename,
            "file_size_bytes": job.file_size_bytes,
            "width": job.db_width,
            "height": job.db_height,
            "frame_count": job.db_frame_count,
            "fps": job.db_fps,
            "duration_seconds": job.db_duration_seconds,
        },
        "model": {
            "id": loaded_model.metadata.id,
            "name": loaded_model.metadata.name,
            "model_family": loaded_model.metadata.model_family,
            "variant": loaded_model.metadata.variant,
        },
        "parameters": params,
        "summary": summary,
        "detections": [
            export_detection(detection, loaded_model, params) for detection in detections
        ],
        "tracks": [export_track(track) for track in tracks],
    }
    try:
        path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        raise VideoProcessingError("JSON export could not be created") from exc


def export_detection(
    detection: VideoDetection,
    loaded_model: LoadedModel,
    params: dict[str, Any],
) -> dict[str, Any]:
    width = detection.bbox_x2 - detection.bbox_x1
    height = detection.bbox_y2 - detection.bbox_y1
    return {
        "job_id": detection.job_id,
        "media_id": detection.media_id,
        "frame_index": detection.frame_index,
        "timestamp_ms": detection.timestamp_ms,
        "class_id": detection.class_id,
        "class_name": detection.class_name,
        "confidence": detection.confidence,
        "bbox_x1": detection.bbox_x1,
        "bbox_y1": detection.bbox_y1,
        "bbox_x2": detection.bbox_x2,
        "bbox_y2": detection.bbox_y2,
        "center_x": detection.bbox_x1 + width / 2,
        "center_y": detection.bbox_y1 + height / 2,
        "bbox_width": width,
        "bbox_height": height,
        "frame_width": detection.frame_width,
        "frame_height": detection.frame_height,
        "track_id": detection.track_id,
        "model_version": loaded_model.metadata.name,
        "tracker_type": params["tracker_type"],
    }


def build_track_summaries(
    job_id: str,
    detections: list[VideoDetection],
) -> list[TrackSummary]:
    grouped: dict[int, list[VideoDetection]] = {}
    for detection in detections:
        if detection.track_id is None:
            continue
        grouped.setdefault(detection.track_id, []).append(detection)
    summaries: list[TrackSummary] = []
    for track_id, track_detections in sorted(grouped.items()):
        confidences = [detection.confidence for detection in track_detections]
        frames = [detection.frame_index for detection in track_detections]
        summaries.append(
            TrackSummary(
                job_id=job_id,
                track_id=track_id,
                class_name="drone",
                first_frame_index=min(frames),
                last_frame_index=max(frames),
                frames_count=len(set(frames)),
                average_confidence=sum(confidences) / len(confidences) if confidences else None,
                max_confidence=max(confidences) if confidences else None,
            )
        )
    return summaries


def export_track(track: TrackSummary) -> dict[str, Any]:
    return {
        "job_id": track.job_id,
        "track_id": track.track_id,
        "class_name": track.class_name,
        "first_frame_index": track.first_frame_index,
        "last_frame_index": track.last_frame_index,
        "frames_count": track.frames_count,
        "average_confidence": track.average_confidence,
        "max_confidence": track.max_confidence,
    }


def build_summary(
    *,
    job: VideoJob,
    detections: list[VideoDetection],
    tracks: list[TrackSummary],
    loaded_model: LoadedModel,
    params: dict[str, Any],
    processed_frames: int,
    total_processing_time: float,
    inference_latency_ms: float | None,
    average_fps: float | None,
    model_size_mb: float | None,
) -> dict[str, Any]:
    confidences = [detection.confidence for detection in detections]
    frames_with_detections = {detection.frame_index for detection in detections}
    return {
        "media_type": "video",
        "original_filename": job.original_filename,
        "file_size_bytes": job.file_size_bytes,
        "processing_status": "completed",
        "total_frames_processed": processed_frames,
        "total_detections": len(detections),
        "frames_with_detections": len(frames_with_detections),
        "unique_track_ids": len(tracks),
        "average_confidence": sum(confidences) / len(confidences) if confidences else None,
        "maximum_confidence": max(confidences) if confidences else None,
        "average_fps": average_fps,
        "inference_latency_ms_per_frame": inference_latency_ms,
        "total_processing_time_seconds": total_processing_time,
        "model_size_mb": model_size_mb,
        "selected_model_version": loaded_model.metadata.name,
        "selected_model_id": loaded_model.metadata.id,
        "confidence_threshold": params["confidence_threshold"],
        "iou_threshold": params["iou_threshold"],
        "tracker_type": params["tracker_type"],
    }


def model_size_mb(settings: WorkerSettings, weights_path: str) -> float | None:
    try:
        if weights_path.replace("\\", "/").startswith("models/"):
            path = safe_join_storage_path(settings.storage_root, weights_path)
        else:
            path = safe_join_storage_path(settings.models_root, weights_path)
    except ValueError:
        return None
    if not path.is_file():
        return None
    return path.stat().st_size / (1024 * 1024)
