from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal, cast
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.storage_paths import safe_download_filename, safe_join_storage_path
from app.db.models import Detection, MediaFile, ProcessingJob, Track, User, utc_now
from app.schemas.jobs import (
    DetectionResponse,
    JobDetailResponse,
    JobDownloadReference,
    JobMediaReference,
    JobModelReference,
    JobResultReferences,
    JobResultResponse,
    TrackResponse,
)

DownloadKind = Literal["media", "csv", "json"]
VALID_JOB_STATUSES = {"queued", "processing", "completed", "failed", "cancelled"}
VALID_MEDIA_TYPES = {"image", "video"}
DOWNLOAD_MEDIA_TYPES = {
    "csv": "text/csv",
    "json": "application/json",
}
RESULT_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
}


def list_visible_jobs(
    *,
    session: Session,
    current_user: User,
    settings_storage_root: str,
    limit: int,
    offset: int,
    status_filter: str | None,
    media_type: str | None,
    model_version_id: UUID | None,
    owner_id: UUID | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> tuple[list[JobDetailResponse], int]:
    statement = _visible_job_statement(current_user).options(
        selectinload(ProcessingJob.media_file),
        selectinload(ProcessingJob.model_version),
    )
    count_statement = _visible_job_count_statement(current_user)

    for predicate in _job_filter_predicates(
        current_user=current_user,
        status_filter=status_filter,
        media_type=media_type,
        model_version_id=model_version_id,
        owner_id=owner_id,
        created_from=created_from,
        created_to=created_to,
    ):
        statement = statement.where(predicate)
        count_statement = count_statement.where(predicate)

    total = session.scalar(count_statement) or 0
    jobs = list(
        session.scalars(
            statement.order_by(ProcessingJob.created_at.desc()).limit(limit).offset(offset)
        )
    )
    return [_job_detail(job, settings_storage_root) for job in jobs], total


def get_visible_job_detail(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
    settings_storage_root: str,
) -> JobDetailResponse:
    return _job_detail(
        get_visible_job(session=session, job_id=job_id, current_user=current_user),
        settings_storage_root,
    )


def get_visible_job(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
) -> ProcessingJob:
    job = session.scalar(
        select(ProcessingJob)
        .options(
            selectinload(ProcessingJob.media_file),
            selectinload(ProcessingJob.model_version),
        )
        .where(ProcessingJob.id == job_id, ProcessingJob.deleted_at.is_(None))
    )
    if job is None or (current_user.role != "admin" and job.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return job


def soft_delete_job(*, session: Session, job_id: UUID, current_user: User) -> None:
    job = get_visible_job(session=session, job_id=job_id, current_user=current_user)
    if job.status == "queued":
        job.status = "cancelled"
    job.deleted_at = utc_now()
    session.commit()


def get_job_summary(*, session: Session, job_id: UUID, current_user: User) -> dict[str, object]:
    job = get_visible_job(session=session, job_id=job_id, current_user=current_user)
    return {"job_id": job.id, "status": job.status, "summary": job.summary_json or {}}


def list_job_detections(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
    limit: int,
    offset: int,
    frame_index: int | None,
    min_confidence: float | None,
    max_confidence: float | None,
    track_id: int | None,
) -> tuple[list[DetectionResponse], int]:
    get_visible_job(session=session, job_id=job_id, current_user=current_user)
    statement = select(Detection).where(Detection.job_id == job_id)
    count_statement = select(func.count()).select_from(Detection).where(Detection.job_id == job_id)

    if frame_index is not None:
        statement = statement.where(Detection.frame_index == frame_index)
        count_statement = count_statement.where(Detection.frame_index == frame_index)
    if min_confidence is not None:
        statement = statement.where(Detection.confidence >= min_confidence)
        count_statement = count_statement.where(Detection.confidence >= min_confidence)
    if max_confidence is not None:
        statement = statement.where(Detection.confidence <= max_confidence)
        count_statement = count_statement.where(Detection.confidence <= max_confidence)
    if track_id is not None:
        statement = statement.where(Detection.track_id == track_id)
        count_statement = count_statement.where(Detection.track_id == track_id)

    total = session.scalar(count_statement) or 0
    detections = list(
        session.scalars(
            statement.order_by(Detection.frame_index, Detection.created_at)
            .limit(limit)
            .offset(offset)
        )
    )
    return [_detection_response(detection) for detection in detections], total


def list_job_tracks(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
    limit: int,
    offset: int,
) -> tuple[list[TrackResponse], int]:
    get_visible_job(session=session, job_id=job_id, current_user=current_user)
    statement = select(Track).where(Track.job_id == job_id)
    count_statement = select(func.count()).select_from(Track).where(Track.job_id == job_id)
    total = session.scalar(count_statement) or 0
    tracks = list(session.scalars(statement.order_by(Track.track_id).limit(limit).offset(offset)))
    return [TrackResponse.model_validate(track) for track in tracks], total


def get_job_result_metadata(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
    storage_root: str,
) -> JobResultResponse:
    job = get_visible_job(session=session, job_id=job_id, current_user=current_user)
    refs = _result_references(job, storage_root)
    return JobResultResponse(
        job_id=job.id,
        status=job.status,
        summary=job.summary_json,
        media=refs.media,
        csv=refs.csv,
        json_export=refs.json_export,
    )


def resolve_job_download(
    *,
    session: Session,
    job_id: UUID,
    current_user: User,
    storage_root: str,
    kind: DownloadKind,
) -> tuple[Path, str, str]:
    job = get_visible_job(session=session, job_id=job_id, current_user=current_user)
    relative_path = _path_for_kind(job, kind)
    resolved_path = _resolve_associated_result_path(
        storage_root=storage_root,
        job_id=job.id,
        relative_path=relative_path,
    )
    if not resolved_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result file not found")
    return (
        resolved_path,
        _download_media_type(kind, relative_path),
        _download_filename(job, kind, relative_path),
    )


def parse_download_kind(kind: str) -> DownloadKind:
    if kind not in {"media", "csv", "json"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return cast(DownloadKind, kind)


def _visible_job_statement(current_user: User):
    statement = select(ProcessingJob).where(ProcessingJob.deleted_at.is_(None))
    if current_user.role != "admin":
        statement = statement.where(ProcessingJob.user_id == current_user.id)
    return statement


def _visible_job_count_statement(current_user: User):
    statement = (
        select(func.count()).select_from(ProcessingJob).where(ProcessingJob.deleted_at.is_(None))
    )
    if current_user.role != "admin":
        statement = statement.where(ProcessingJob.user_id == current_user.id)
    return statement


def _job_filter_predicates(
    *,
    current_user: User,
    status_filter: str | None,
    media_type: str | None,
    model_version_id: UUID | None,
    owner_id: UUID | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> list[object]:
    predicates: list[object] = []
    if status_filter is not None:
        if status_filter not in VALID_JOB_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid job status",
            )
        predicates.append(ProcessingJob.status == status_filter)
    if media_type is not None:
        if media_type not in VALID_MEDIA_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid media type",
            )
        predicates.append(ProcessingJob.media_file.has(MediaFile.media_type == media_type))
    if model_version_id is not None:
        predicates.append(ProcessingJob.model_version_id == model_version_id)
    if owner_id is not None and current_user.role == "admin":
        predicates.append(ProcessingJob.user_id == owner_id)
    if created_from is not None:
        predicates.append(ProcessingJob.created_at >= created_from)
    if created_to is not None:
        predicates.append(ProcessingJob.created_at <= created_to)
    return predicates


def _job_detail(job: ProcessingJob, storage_root: str) -> JobDetailResponse:
    refs = _result_references(job, storage_root)
    return JobDetailResponse(
        id=job.id,
        user_id=job.user_id,
        media_file_id=job.media_file_id,
        model_version_id=job.model_version_id,
        status=job.status,
        input_params_json=job.input_params_json,
        summary_json=job.summary_json,
        error_message=job.error_message,
        progress_percent=job.progress_percent,
        last_heartbeat_at=job.last_heartbeat_at,
        locked_by=job.locked_by,
        locked_at=job.locked_at,
        retry_count=job.retry_count,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
        media=JobMediaReference(
            id=job.media_file.id,
            original_filename=job.media_file.original_filename,
            media_type=job.media_file.media_type,
            width=job.media_file.width,
            height=job.media_file.height,
            frame_count=job.media_file.frame_count,
            fps=job.media_file.fps,
            duration_seconds=job.media_file.duration_seconds,
        ),
        model=(
            JobModelReference(
                id=job.model_version.id,
                name=job.model_version.name,
                model_family=job.model_version.model_family,
                variant=job.model_version.variant,
            )
            if job.model_version is not None
            else None
        ),
        result=refs,
    )


def _result_references(job: ProcessingJob, storage_root: str) -> JobResultReferences:
    return JobResultReferences(
        media=_download_reference(job, storage_root, "media"),
        csv=_download_reference(job, storage_root, "csv"),
        json_export=_download_reference(job, storage_root, "json"),
    )


def _download_reference(
    job: ProcessingJob,
    storage_root: str,
    kind: DownloadKind,
) -> JobDownloadReference:
    available = False
    try:
        relative_path = _path_for_kind(job, kind)
        path = _resolve_associated_result_path(
            storage_root=storage_root,
            job_id=job.id,
            relative_path=relative_path,
        )
        available = path.is_file()
    except HTTPException:
        available = False
    return JobDownloadReference(
        available=available,
        download_url=f"/api/jobs/{job.id}/download/{kind}",
    )


def _path_for_kind(job: ProcessingJob, kind: DownloadKind) -> str | None:
    if kind == "media":
        return job.result_media_path
    if kind == "csv":
        return job.csv_path
    return job.json_path


def _resolve_associated_result_path(
    *,
    storage_root: str,
    job_id: UUID,
    relative_path: str | None,
) -> Path:
    if relative_path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result file not found")
    expected_prefix = f"results/{job_id}/"
    try:
        normalized_path = safe_join_storage_path(storage_root, relative_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Result file not found",
        ) from exc
    normalized_relative = str(relative_path).replace("\\", "/")
    if not normalized_relative.startswith(expected_prefix):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result file not found")
    return normalized_path


def _download_filename(
    job: ProcessingJob,
    kind: DownloadKind,
    relative_path: str | None,
) -> str:
    suffix = Path(relative_path or "").suffix
    stem = f"job-{job.id}-{kind}"
    return safe_download_filename(f"{stem}{suffix}", fallback=f"{kind}-download")


def _download_media_type(kind: DownloadKind, relative_path: str | None) -> str:
    if kind != "media":
        return DOWNLOAD_MEDIA_TYPES[kind]
    suffix = Path(relative_path or "").suffix.lower()
    return RESULT_MEDIA_TYPES.get(suffix, "application/octet-stream")


def _detection_response(detection: Detection) -> DetectionResponse:
    width = detection.bbox_x2 - detection.bbox_x1
    height = detection.bbox_y2 - detection.bbox_y1
    return DetectionResponse(
        id=detection.id,
        job_id=detection.job_id,
        media_file_id=detection.media_file_id,
        frame_index=detection.frame_index,
        timestamp_ms=detection.timestamp_ms,
        class_id=detection.class_id,
        class_name=detection.class_name,
        confidence=detection.confidence,
        bbox_x1=detection.bbox_x1,
        bbox_y1=detection.bbox_y1,
        bbox_x2=detection.bbox_x2,
        bbox_y2=detection.bbox_y2,
        center_x=detection.bbox_x1 + width / 2,
        center_y=detection.bbox_y1 + height / 2,
        bbox_width=width,
        bbox_height=height,
        frame_width=detection.frame_width,
        frame_height=detection.frame_height,
        track_id=detection.track_id,
        created_at=detection.created_at,
    )
