from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.queue import utc_now
from aerovision_worker.video_types import TrackSummary, VideoDetection, VideoProcessingError


def complete_video_job(
    session_factory: sessionmaker[Session],
    *,
    job_id: str,
    media_id: str,
    worker_id: str,
    result_paths: dict[str, str],
    summary: dict[str, Any],
    detections: list[VideoDetection],
    tracks: list[TrackSummary],
) -> None:
    completed_at = utc_now()
    with session_factory.begin() as session:
        session.execute(text("delete from detections where job_id = :job_id"), {"job_id": job_id})
        session.execute(text("delete from tracks where job_id = :job_id"), {"job_id": job_id})
        for detection in detections:
            _insert_detection(session, detection, media_id=media_id, created_at=completed_at)
        for track in tracks:
            _insert_track(session, track, created_at=completed_at)
        _update_completed_job(
            session,
            job_id=job_id,
            worker_id=worker_id,
            result_paths=result_paths,
            summary=summary,
            completed_at=completed_at,
        )


def _insert_detection(
    session: Session,
    detection: VideoDetection,
    *,
    media_id: str,
    created_at,
) -> None:
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
            "job_id": detection.job_id,
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
            "created_at": created_at,
        },
    )


def _insert_track(session: Session, track: TrackSummary, *, created_at) -> None:
    session.execute(
        text(
            """
            insert into tracks (
                id, job_id, track_id, class_name, first_frame_index, last_frame_index,
                frames_count, average_confidence, max_confidence, created_at
            )
            values (
                :id, :job_id, :track_id, :class_name, :first_frame_index, :last_frame_index,
                :frames_count, :average_confidence, :max_confidence, :created_at
            )
            """
        ),
        {
            "id": uuid4().hex,
            "job_id": track.job_id,
            "track_id": track.track_id,
            "class_name": track.class_name,
            "first_frame_index": track.first_frame_index,
            "last_frame_index": track.last_frame_index,
            "frames_count": track.frames_count,
            "average_confidence": track.average_confidence,
            "max_confidence": track.max_confidence,
            "created_at": created_at,
        },
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
        raise VideoProcessingError("Video job could not be finalized")
