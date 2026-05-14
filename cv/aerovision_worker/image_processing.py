from __future__ import annotations

import csv
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.model_runtime import LoadedModel
from aerovision_worker.queue import fail_processing_job, utc_now
from aerovision_worker.settings import WorkerSettings
from aerovision_worker.storage_paths import safe_join_storage_path, validate_relative_storage_path

LOGGER = logging.getLogger("aerovision_worker.image_processing")

CSV_COLUMNS = [
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


@dataclass(frozen=True)
class ImageJob:
    id: str
    media_id: str
    media_type: str
    stored_path: str
    original_filename: str
    file_size_bytes: int
    input_params: dict[str, Any]


@dataclass(frozen=True)
class ImageDetection:
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


def process_image_job(
    settings: WorkerSettings,
    session_factory: sessionmaker[Session],
    *,
    job_id: Any,
    worker_id: str,
    loaded_model: LoadedModel,
) -> None:
    started = time.perf_counter()
    try:
        job = _load_image_job(session_factory, job_id=job_id)
        source_path = _source_path(settings, job.stored_path)
        if not source_path.is_file():
            raise ImageProcessingError("Source image file is missing")

        image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ImageProcessingError("Source image could not be decoded")

        frame_height, frame_width = image.shape[:2]
        params = _processing_params(job.input_params)
        inference_started = time.perf_counter()
        result = _run_inference(loaded_model, image, params)
        inference_ms = (time.perf_counter() - inference_started) * 1000
        detections = _detections_from_result(
            result,
            job_id=str(job.id),
            media_id=str(job.media_id),
            frame_width=frame_width,
            frame_height=frame_height,
        )
        result_paths = _result_paths(str(job.id), source_path.suffix)
        _write_annotated_image(settings, result_paths["media"], image, detections)
        _write_csv_export(settings, result_paths["csv"], detections, loaded_model, params)
        summary = _build_summary(
            job=job,
            detections=detections,
            loaded_model=loaded_model,
            params=params,
            total_processing_time=time.perf_counter() - started,
            inference_latency_ms=inference_ms,
            model_size_mb=_model_size_mb(settings, loaded_model.metadata.weights_path),
        )
        _write_json_export(
            settings,
            result_paths["json"],
            job,
            loaded_model,
            params,
            summary,
            detections,
        )
        try:
            _complete_image_job(
                session_factory,
                job_id=str(job.id),
                media_id=str(job.media_id),
                worker_id=worker_id,
                result_paths=result_paths,
                summary=summary,
                detections=detections,
            )
        except SQLAlchemyError as exc:
            raise ImageProcessingError("Image job database update failed") from exc
        LOGGER.info("image_job_completed job_id=%s detections=%s", job.id, len(detections))
    except ImageProcessingError as exc:
        fail_processing_job(
            session_factory,
            job_id=job_id,
            worker_id=worker_id,
            error_message=str(exc),
            now=utc_now(),
        )
        LOGGER.info("image_job_failed job_id=%s error=%s", job_id, str(exc))


class ImageProcessingError(RuntimeError):
    pass


def _load_image_job(session_factory: sessionmaker[Session], *, job_id: Any) -> ImageJob:
    with session_factory() as session:
        row = (
            session.execute(
                text(
                    """
                    select
                        pj.id as job_id,
                        pj.input_params_json,
                        mf.id as media_id,
                        mf.media_type,
                        mf.stored_path,
                        mf.original_filename,
                        mf.file_size_bytes
                    from processing_jobs pj
                    join media_files mf on mf.id = pj.media_file_id
                    where pj.id = :job_id
                      and pj.deleted_at is null
                      and mf.deleted_at is null
                    """
                ),
                {"job_id": job_id},
            )
            .mappings()
            .one_or_none()
        )
    if row is None:
        raise ImageProcessingError("Image job metadata is unavailable")
    if row["media_type"] != "image":
        raise ImageProcessingError("Job media type is not supported by image processor")
    try:
        stored_path = validate_relative_storage_path(str(row["stored_path"]))
    except ValueError as exc:
        raise ImageProcessingError("Source image path is unsafe") from exc
    return ImageJob(
        id=str(row["job_id"]),
        media_id=str(row["media_id"]),
        media_type=str(row["media_type"]),
        stored_path=stored_path,
        original_filename=str(row["original_filename"]),
        file_size_bytes=int(row["file_size_bytes"]),
        input_params=_parse_input_params(row["input_params_json"]),
    )


def _parse_input_params(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _processing_params(input_params: dict[str, Any]) -> dict[str, Any]:
    return {
        "confidence_threshold": float(input_params.get("confidence_threshold", 0.25)),
        "iou_threshold": float(input_params.get("iou_threshold", 0.45)),
        "image_size": int(input_params.get("image_size", 640)),
        "tracker_type": str(input_params.get("tracker_type", "bytetrack")),
        "frame_stride": int(input_params.get("frame_stride", 1)),
    }


def _source_path(settings: WorkerSettings, stored_path: str) -> Path:
    try:
        return safe_join_storage_path(settings.storage_root, stored_path)
    except ValueError as exc:
        raise ImageProcessingError("Source image path is unsafe") from exc


def _run_inference(loaded_model: LoadedModel, image: np.ndarray, params: dict[str, Any]) -> Any:
    try:
        results = loaded_model.model(
            image,
            conf=params["confidence_threshold"],
            iou=params["iou_threshold"],
            imgsz=params["image_size"],
            device=loaded_model.device,
            verbose=False,
        )
    except TypeError:
        results = loaded_model.model(
            image,
            conf=params["confidence_threshold"],
            iou=params["iou_threshold"],
            imgsz=params["image_size"],
        )
    except Exception as exc:
        raise ImageProcessingError("Image inference failed") from exc
    return results[0] if isinstance(results, list | tuple) else results


def _detections_from_result(
    result: Any,
    *,
    job_id: str,
    media_id: str,
    frame_width: int,
    frame_height: int,
) -> list[ImageDetection]:
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []
    xyxy = _array(getattr(boxes, "xyxy", []))
    confs = _array(getattr(boxes, "conf", []))
    classes = _array(getattr(boxes, "cls", []))
    detections: list[ImageDetection] = []
    for index, box in enumerate(xyxy):
        x1, y1, x2, y2 = _clamp_box(box, frame_width=frame_width, frame_height=frame_height)
        if x2 <= x1 or y2 <= y1:
            continue
        confidence = float(confs[index]) if index < len(confs) else 0.0
        class_id = int(classes[index]) if index < len(classes) else 0
        detections.append(
            ImageDetection(
                job_id=job_id,
                media_id=media_id,
                frame_index=0,
                timestamp_ms=0,
                class_id=class_id,
                class_name="drone",
                confidence=confidence,
                bbox_x1=x1,
                bbox_y1=y1,
                bbox_x2=x2,
                bbox_y2=y2,
                frame_width=frame_width,
                frame_height=frame_height,
                track_id=None,
            )
        )
    return detections


def _array(value: Any) -> np.ndarray:
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        value = value.numpy()
    return np.asarray(value)


def _clamp_box(
    box: Any,
    *,
    frame_width: int,
    frame_height: int,
) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = [float(value) for value in box[:4]]
    return (
        max(0.0, min(float(frame_width), x1)),
        max(0.0, min(float(frame_height), y1)),
        max(0.0, min(float(frame_width), x2)),
        max(0.0, min(float(frame_height), y2)),
    )


def _result_paths(job_id: str, source_suffix: str) -> dict[str, str]:
    suffix = source_suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    return {
        "media": f"results/{job_id}/annotated{suffix}",
        "csv": f"results/{job_id}/detections.csv",
        "json": f"results/{job_id}/detections.json",
    }


def _write_annotated_image(
    settings: WorkerSettings,
    relative_path: str,
    image: np.ndarray,
    detections: list[ImageDetection],
) -> None:
    annotated = image.copy()
    for detection in detections:
        p1 = (int(round(detection.bbox_x1)), int(round(detection.bbox_y1)))
        p2 = (int(round(detection.bbox_x2)), int(round(detection.bbox_y2)))
        cv2.rectangle(annotated, p1, p2, (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"drone {detection.confidence:.2f}",
            (p1[0], max(12, p1[1] - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
    path = _output_path(settings, relative_path)
    if not cv2.imwrite(str(path), annotated):
        raise ImageProcessingError("Annotated image output could not be created")


def _write_csv_export(
    settings: WorkerSettings,
    relative_path: str,
    detections: list[ImageDetection],
    loaded_model: LoadedModel,
    params: dict[str, Any],
) -> None:
    path = _output_path(settings, relative_path)
    try:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for detection in detections:
                writer.writerow(_export_detection(detection, loaded_model, params))
    except OSError as exc:
        raise ImageProcessingError("CSV export could not be created") from exc


def _write_json_export(
    settings: WorkerSettings,
    relative_path: str,
    job: ImageJob,
    loaded_model: LoadedModel,
    params: dict[str, Any],
    summary: dict[str, Any],
    detections: list[ImageDetection],
) -> None:
    path = _output_path(settings, relative_path)
    export = {
        "job": {"id": job.id, "status": "completed"},
        "media": {
            "id": job.media_id,
            "media_type": job.media_type,
            "original_filename": job.original_filename,
            "file_size_bytes": job.file_size_bytes,
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
            _export_detection(detection, loaded_model, params) for detection in detections
        ],
        "tracks": [],
    }
    try:
        path.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        raise ImageProcessingError("JSON export could not be created") from exc


def _output_path(settings: WorkerSettings, relative_path: str) -> Path:
    try:
        path = safe_join_storage_path(settings.storage_root, relative_path)
    except ValueError as exc:
        raise ImageProcessingError("Result path is unsafe") from exc
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ImageProcessingError("Result output directory could not be created") from exc
    return path


def _export_detection(
    detection: ImageDetection,
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


def _build_summary(
    *,
    job: ImageJob,
    detections: list[ImageDetection],
    loaded_model: LoadedModel,
    params: dict[str, Any],
    total_processing_time: float,
    inference_latency_ms: float,
    model_size_mb: float | None,
) -> dict[str, Any]:
    confidences = [detection.confidence for detection in detections]
    return {
        "media_type": "image",
        "original_filename": job.original_filename,
        "file_size_bytes": job.file_size_bytes,
        "processing_status": "completed",
        "total_frames_processed": 1,
        "total_detections": len(detections),
        "frames_with_detections": 1 if detections else 0,
        "unique_track_ids": 0,
        "average_confidence": sum(confidences) / len(confidences) if confidences else None,
        "maximum_confidence": max(confidences) if confidences else None,
        "average_fps": None,
        "inference_latency_ms_per_frame": inference_latency_ms,
        "total_processing_time_seconds": total_processing_time,
        "model_size_mb": model_size_mb,
        "selected_model_version": loaded_model.metadata.name,
        "selected_model_id": loaded_model.metadata.id,
        "confidence_threshold": params["confidence_threshold"],
        "iou_threshold": params["iou_threshold"],
        "tracker_type": params["tracker_type"],
    }


def _model_size_mb(settings: WorkerSettings, weights_path: str) -> float | None:
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


def _complete_image_job(
    session_factory: sessionmaker[Session],
    *,
    job_id: str,
    media_id: str,
    worker_id: str,
    result_paths: dict[str, str],
    summary: dict[str, Any],
    detections: list[ImageDetection],
) -> None:
    completed_at = utc_now()
    with session_factory.begin() as session:
        session.execute(text("delete from detections where job_id = :job_id"), {"job_id": job_id})
        for detection in detections:
            session.execute(
                text(
                    """
                    insert into detections (
                        id, job_id, media_file_id, frame_index, timestamp_ms, class_id,
                        class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                        frame_width, frame_height, track_id, created_at
                    )
                    values (
                        :id, :job_id, :media_file_id, :frame_index, :timestamp_ms, :class_id,
                        :class_name, :confidence, :bbox_x1, :bbox_y1, :bbox_x2, :bbox_y2,
                        :frame_width, :frame_height, :track_id, :created_at
                    )
                    """
                ),
                {
                    "id": uuid4().hex,
                    "job_id": job_id,
                    "media_file_id": media_id,
                    "frame_index": detection.frame_index,
                    "timestamp_ms": detection.timestamp_ms,
                    "class_id": detection.class_id,
                    "class_name": detection.class_name,
                    "confidence": detection.confidence,
                    "bbox_x1": detection.bbox_x1,
                    "bbox_y1": detection.bbox_y1,
                    "bbox_x2": detection.bbox_x2,
                    "bbox_y2": detection.bbox_y2,
                    "frame_width": detection.frame_width,
                    "frame_height": detection.frame_height,
                    "track_id": detection.track_id,
                    "created_at": completed_at,
                },
            )
        _update_completed_job(
            session,
            job_id=job_id,
            worker_id=worker_id,
            result_paths=result_paths,
            summary=summary,
            completed_at=completed_at,
        )


def _update_completed_job(
    session: Session,
    *,
    job_id: str,
    worker_id: str,
    result_paths: dict[str, str],
    summary: dict[str, Any],
    completed_at,
) -> None:
    summary_json = json.dumps(summary)
    dialect = session.get_bind().dialect.name
    summary_expr = "cast(:summary_json as jsonb)" if dialect == "postgresql" else ":summary_json"
    result = session.execute(
        text(
            f"""
            update processing_jobs
            set status = 'completed',
                summary_json = {summary_expr},
                result_media_path = :result_media_path,
                csv_path = :csv_path,
                json_path = :json_path,
                error_message = null,
                progress_percent = 100,
                completed_at = :completed_at,
                last_heartbeat_at = :completed_at,
                locked_by = null,
                locked_at = null,
                updated_at = :completed_at
            where id = :job_id
              and locked_by = :worker_id
              and status = 'processing'
              and deleted_at is null
            """
        ),
        {
            "job_id": job_id,
            "worker_id": worker_id,
            "summary_json": summary_json,
            "result_media_path": result_paths["media"],
            "csv_path": result_paths["csv"],
            "json_path": result_paths["json"],
            "completed_at": completed_at,
        },
    )
    if result.rowcount != 1:
        raise ImageProcessingError("Image job could not be finalized")
