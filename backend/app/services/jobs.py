from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MediaFile, ModelVersion, ProcessingJob, User
from app.schemas.jobs import JobCreateRequest

DEFAULT_CONFIDENCE_THRESHOLD = 0.25
DEFAULT_IOU_THRESHOLD = 0.45
DEFAULT_IMAGE_SIZE = 640
DEFAULT_TRACKER_TYPE = "bytetrack"
DEFAULT_FRAME_STRIDE = 1


def create_processing_job(
    *,
    session: Session,
    current_user: User,
    payload: JobCreateRequest,
    active_model_id: str | None,
) -> ProcessingJob:
    media = _get_owned_media(session, payload.media_id, current_user)
    input_params = _resolve_input_params(payload, media)
    model = _resolve_model_version(
        session=session,
        explicit_model_id=payload.model_version_id,
        active_model_id=active_model_id,
    )

    job = ProcessingJob(
        user_id=current_user.id,
        media_file_id=media.id,
        model_version_id=model.id,
        status="queued",
        input_params_json=input_params,
        progress_percent=0,
        retry_count=0,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def _get_owned_media(session: Session, media_id: UUID, current_user: User) -> MediaFile:
    media = session.scalar(
        select(MediaFile).where(MediaFile.id == media_id, MediaFile.deleted_at.is_(None))
    )
    if media is None or media.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return media


def _resolve_input_params(payload: JobCreateRequest, media: MediaFile) -> dict[str, object]:
    if media.media_type == "image" and payload.tracker_type is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Tracker type is only configurable for video media",
        )

    return {
        "confidence_threshold": (
            payload.confidence_threshold
            if payload.confidence_threshold is not None
            else DEFAULT_CONFIDENCE_THRESHOLD
        ),
        "iou_threshold": (
            payload.iou_threshold if payload.iou_threshold is not None else DEFAULT_IOU_THRESHOLD
        ),
        "image_size": DEFAULT_IMAGE_SIZE,
        "tracker_type": payload.tracker_type or DEFAULT_TRACKER_TYPE,
        "frame_stride": DEFAULT_FRAME_STRIDE,
    }


def _resolve_model_version(
    *,
    session: Session,
    explicit_model_id: UUID | None,
    active_model_id: str | None,
) -> ModelVersion:
    if explicit_model_id is not None:
        model = session.get(ModelVersion, explicit_model_id)
        if model is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            )
        return model

    active_model = session.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))
    if active_model is not None:
        return active_model

    fallback_id = _parse_fallback_model_id(active_model_id)
    fallback_model = session.get(ModelVersion, fallback_id)
    if fallback_model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configured active model is unavailable",
        )
    return fallback_model


def _parse_fallback_model_id(active_model_id: str | None) -> UUID:
    if not active_model_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active model is available",
        )
    try:
        return UUID(active_model_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Configured active model id is invalid",
        ) from exc
