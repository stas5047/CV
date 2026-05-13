from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.auth import get_current_active_user
from app.core.config import Settings, get_settings
from app.db.models import User
from app.schemas.jobs import (
    DetectionListResponse,
    JobCreateRequest,
    JobDetailResponse,
    JobListResponse,
    JobResponse,
    JobResultResponse,
    JobSummaryResponse,
    TrackListResponse,
)
from app.services.jobs import create_processing_job
from app.services.results import (
    get_job_result_metadata,
    get_job_summary,
    get_visible_job_detail,
    list_job_detections,
    list_job_tracks,
    list_visible_jobs,
    parse_download_kind,
    resolve_job_download,
    soft_delete_job,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> JobResponse:
    job = create_processing_job(
        session=session,
        current_user=current_user,
        payload=payload,
        active_model_id=settings.active_model_id,
    )
    return JobResponse.model_validate(job)


@router.get("", response_model=JobListResponse)
def list_jobs(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    media_type: str | None = None,
    model_version_id: UUID | None = None,
    owner_id: UUID | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> JobListResponse:
    items, total = list_visible_jobs(
        session=session,
        current_user=current_user,
        settings_storage_root=settings.storage_root,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        media_type=media_type,
        model_version_id=model_version_id,
        owner_id=owner_id,
        created_from=created_from,
        created_to=created_to,
    )
    return JobListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> JobDetailResponse:
    return get_visible_job_detail(
        session=session,
        job_id=job_id,
        current_user=current_user,
        settings_storage_root=settings.storage_root,
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Response:
    soft_delete_job(session=session, job_id=job_id, current_user=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{job_id}/summary", response_model=JobSummaryResponse)
def get_summary(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, object]:
    return get_job_summary(session=session, job_id=job_id, current_user=current_user)


@router.get("/{job_id}/detections", response_model=DetectionListResponse)
def get_detections(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    frame_index: int | None = None,
    min_confidence: Annotated[float | None, Query(ge=0, le=1)] = None,
    max_confidence: Annotated[float | None, Query(ge=0, le=1)] = None,
    track_id: int | None = None,
) -> DetectionListResponse:
    items, total = list_job_detections(
        session=session,
        job_id=job_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
        frame_index=frame_index,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        track_id=track_id,
    )
    return DetectionListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{job_id}/tracks", response_model=TrackListResponse)
def get_tracks(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TrackListResponse:
    items, total = list_job_tracks(
        session=session,
        job_id=job_id,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return TrackListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{job_id}/result", response_model=JobResultResponse)
def get_result(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> JobResultResponse:
    return get_job_result_metadata(
        session=session,
        job_id=job_id,
        current_user=current_user,
        storage_root=settings.storage_root,
    )


def _download_result_by_kind(
    job_id: UUID,
    kind: str,
    session: Session,
    settings: Settings,
    current_user: User,
) -> FileResponse:
    path, media_type, filename = resolve_job_download(
        session=session,
        job_id=job_id,
        current_user=current_user,
        storage_root=settings.storage_root,
        kind=parse_download_kind(kind),
    )
    return FileResponse(path=path, media_type=media_type, filename=filename)


@router.get("/{job_id}/download/media")
def download_result_media(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FileResponse:
    return _download_result_by_kind(
        job_id=job_id,
        kind="media",
        session=session,
        settings=settings,
        current_user=current_user,
    )


@router.get("/{job_id}/download/csv")
def download_result_csv(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FileResponse:
    return _download_result_by_kind(
        job_id=job_id,
        kind="csv",
        session=session,
        settings=settings,
        current_user=current_user,
    )


@router.get("/{job_id}/download/json")
def download_result_json(
    job_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FileResponse:
    return _download_result_by_kind(
        job_id=job_id,
        kind="json",
        session=session,
        settings=settings,
        current_user=current_user,
    )
