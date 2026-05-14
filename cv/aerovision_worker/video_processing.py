from __future__ import annotations

import json
import logging
import time
from typing import Any

import cv2
import numpy as np
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.model_runtime import LoadedModel
from aerovision_worker.queue import fail_processing_job, update_job_heartbeat, utc_now
from aerovision_worker.settings import WorkerSettings
from aerovision_worker.storage_paths import validate_relative_storage_path
from aerovision_worker.video_detection import annotated_frame, detections_from_result
from aerovision_worker.video_exports import (
    build_summary,
    build_track_summaries,
    model_size_mb,
    output_path,
    result_paths,
    write_csv_export,
    write_json_export,
)
from aerovision_worker.video_io import (
    capture_metadata,
    metadata_from_first_frame,
    open_writer,
    optional_float,
    optional_int,
    source_path,
)
from aerovision_worker.video_persistence import complete_video_job
from aerovision_worker.video_types import (
    SUPPORTED_TRACKERS,
    VideoDetection,
    VideoJob,
    VideoProcessingError,
)

LOGGER = logging.getLogger("aerovision_worker.video_processing")


def process_video_job(
    settings: WorkerSettings,
    session_factory: sessionmaker[Session],
    *,
    job_id: Any,
    worker_id: str,
    loaded_model: LoadedModel,
) -> None:
    started = time.perf_counter()
    writer = None
    capture = None
    try:
        job = _load_video_job(session_factory, job_id=job_id)
        LOGGER.info(
            "video_job_started job_id=%s media_id=%s model_id=%s",
            job.id,
            job.media_id,
            loaded_model.metadata.id,
        )
        source = source_path(settings, job.stored_path)
        if not source.is_file():
            raise VideoProcessingError("Source video file is missing")

        capture = cv2.VideoCapture(str(source))
        if not capture.isOpened():
            raise VideoProcessingError("Source video could not be opened")

        metadata = capture_metadata(capture, job)
        ok, first_frame = capture.read()
        if not ok or first_frame is None:
            raise VideoProcessingError("Source video could not be decoded")
        metadata = metadata_from_first_frame(metadata, first_frame)

        paths = result_paths(str(job.id))
        writer = open_writer(
            output_path(settings, paths["media"]),
            metadata["fps"],
            metadata["width"],
            metadata["height"],
        )
        params = _processing_params(job.input_params)
        result = _process_frames(
            settings,
            session_factory,
            job=job,
            worker_id=worker_id,
            loaded_model=loaded_model,
            params=params,
            capture=capture,
            writer=writer,
            first_frame=first_frame,
            metadata=metadata,
        )
        writer.release()
        writer = None
        capture.release()
        capture = None

        tracks = build_track_summaries(job.id, result["detections"])
        write_csv_export(settings, paths["csv"], result["detections"], loaded_model, params)
        elapsed = time.perf_counter() - started
        summary = build_summary(
            job=job,
            detections=result["detections"],
            tracks=tracks,
            loaded_model=loaded_model,
            params=params,
            processed_frames=result["processed_frames"],
            total_processing_time=elapsed,
            inference_latency_ms=result["inference_ms_per_frame"],
            average_fps=result["processed_frames"] / elapsed if elapsed > 0 else None,
            model_size_mb=model_size_mb(settings, loaded_model.metadata.weights_path),
        )
        write_json_export(
            settings,
            paths["json"],
            job,
            loaded_model,
            params,
            summary,
            result["detections"],
            tracks,
        )
        LOGGER.info("video_exports_written job_id=%s csv=true json=true", job.id)
        try:
            complete_video_job(
                session_factory,
                job_id=job.id,
                media_id=job.media_id,
                worker_id=worker_id,
                result_paths=paths,
                summary=summary,
                detections=result["detections"],
                tracks=tracks,
            )
        except SQLAlchemyError as exc:
            raise VideoProcessingError("Video job database update failed") from exc
        LOGGER.info(
            "video_job_completed job_id=%s frames=%s detections=%s tracks=%s duration_ms=%s",
            job.id,
            result["processed_frames"],
            len(result["detections"]),
            len(tracks),
            int((time.perf_counter() - started) * 1000),
        )
    except VideoProcessingError as exc:
        fail_processing_job(
            session_factory,
            job_id=job_id,
            worker_id=worker_id,
            error_message=str(exc),
            now=utc_now(),
        )
        LOGGER.info("video_job_failed job_id=%s error=%s", job_id, str(exc))
    finally:
        if writer is not None:
            writer.release()
        if capture is not None:
            capture.release()


def _process_frames(
    settings: WorkerSettings,
    session_factory: sessionmaker[Session],
    *,
    job: VideoJob,
    worker_id: str,
    loaded_model: LoadedModel,
    params: dict[str, Any],
    capture,
    writer,
    first_frame: np.ndarray,
    metadata: dict[str, int | float],
) -> dict[str, Any]:
    detections: list[VideoDetection] = []
    inference_ms_total = 0.0
    processed_frames = 0
    last_heartbeat_perf = time.perf_counter()
    frame: np.ndarray | None = first_frame
    while frame is not None:
        frame_index = processed_frames
        inference_started = time.perf_counter()
        tracked = _run_tracking(loaded_model, frame, params)
        inference_ms_total += (time.perf_counter() - inference_started) * 1000
        frame_detections = detections_from_result(
            tracked,
            job_id=job.id,
            media_id=job.media_id,
            frame_index=frame_index,
            timestamp_ms=_timestamp_ms(frame_index, metadata["fps"]),
            frame_width=int(metadata["width"]),
            frame_height=int(metadata["height"]),
        )
        detections.extend(frame_detections)
        writer.write(annotated_frame(frame, frame_detections))
        processed_frames += 1
        last_heartbeat_perf = _heartbeat_if_needed(
            settings,
            session_factory,
            job_id=job.id,
            worker_id=worker_id,
            processed_frames=processed_frames,
            total_frames=int(metadata["frame_count"]),
            last_heartbeat_perf=last_heartbeat_perf,
        )
        ok, frame = capture.read()
        if not ok:
            frame = None
    if processed_frames == 0:
        raise VideoProcessingError("Source video could not be decoded")
    return {
        "detections": detections,
        "processed_frames": processed_frames,
        "inference_ms_per_frame": inference_ms_total / processed_frames,
    }


def _load_video_job(session_factory: sessionmaker[Session], *, job_id: Any) -> VideoJob:
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
                        mf.file_size_bytes,
                        mf.width,
                        mf.height,
                        mf.frame_count,
                        mf.fps,
                        mf.duration_seconds
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
        raise VideoProcessingError("Video job metadata is unavailable")
    if row["media_type"] != "video":
        raise VideoProcessingError("Job media type is not supported by video processor")
    try:
        stored_path = validate_relative_storage_path(str(row["stored_path"]))
    except ValueError as exc:
        raise VideoProcessingError("Source video path is unsafe") from exc
    return VideoJob(
        id=str(row["job_id"]),
        media_id=str(row["media_id"]),
        media_type=str(row["media_type"]),
        stored_path=stored_path,
        original_filename=str(row["original_filename"]),
        file_size_bytes=int(row["file_size_bytes"]),
        db_width=optional_int(row["width"]),
        db_height=optional_int(row["height"]),
        db_frame_count=optional_int(row["frame_count"]),
        db_fps=optional_float(row["fps"]),
        db_duration_seconds=optional_float(row["duration_seconds"]),
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
    tracker_type = str(input_params.get("tracker_type", "bytetrack")).lower()
    if tracker_type not in SUPPORTED_TRACKERS:
        raise VideoProcessingError("Video tracker type is unsupported")
    return {
        "confidence_threshold": float(input_params.get("confidence_threshold", 0.25)),
        "iou_threshold": float(input_params.get("iou_threshold", 0.45)),
        "image_size": int(input_params.get("image_size", 640)),
        "tracker_type": tracker_type,
        "frame_stride": int(input_params.get("frame_stride", 1)),
    }


def _run_tracking(loaded_model: LoadedModel, frame: np.ndarray, params: dict[str, Any]) -> Any:
    track = getattr(loaded_model.model, "track", None)
    if not callable(track):
        raise VideoProcessingError("Video tracker runtime is unavailable")
    kwargs = {
        "conf": params["confidence_threshold"],
        "iou": params["iou_threshold"],
        "imgsz": params["image_size"],
        "device": loaded_model.device,
        "tracker": SUPPORTED_TRACKERS[params["tracker_type"]],
        "persist": True,
        "verbose": False,
    }
    try:
        results = track(frame, **kwargs)
    except TypeError:
        kwargs.pop("device", None)
        try:
            results = track(frame, **kwargs)
        except Exception as exc:
            raise VideoProcessingError("Video tracker runtime is unavailable") from exc
    except Exception as exc:
        raise VideoProcessingError("Video tracker runtime is unavailable") from exc
    return results[0] if isinstance(results, list | tuple) else results


def _heartbeat_if_needed(
    settings: WorkerSettings,
    session_factory: sessionmaker[Session],
    *,
    job_id: str,
    worker_id: str,
    processed_frames: int,
    total_frames: int,
    last_heartbeat_perf: float,
) -> float:
    now_perf = time.perf_counter()
    if (
        processed_frames % settings.heartbeat_frames != 0
        and now_perf - last_heartbeat_perf < settings.heartbeat_seconds
    ):
        return last_heartbeat_perf
    progress = 99 if total_frames <= 0 else min(99, int(processed_frames / total_frames * 100))
    update_job_heartbeat(
        session_factory,
        job_id=job_id,
        worker_id=worker_id,
        progress_percent=progress,
        now=utc_now(),
    )
    return now_perf


def _timestamp_ms(frame_index: int, fps: float) -> int:
    if fps <= 0:
        return 0
    return int(round((frame_index / fps) * 1000))
