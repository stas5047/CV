from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.auth import get_current_active_user
from app.core.config import Settings, get_settings
from app.db.models import User
from app.schemas.media import MediaListResponse, MediaResponse
from app.services.media import (
    create_media_from_upload,
    get_visible_media,
    list_visible_media,
    soft_delete_media,
)

router = APIRouter(prefix="/media", tags=["media"])


@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
def upload_media(
    file: Annotated[UploadFile, File()],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> MediaResponse:
    media = create_media_from_upload(
        session=session,
        current_user=current_user,
        upload=file,
        storage_root=settings.storage_root,
        max_image_size_mb=settings.max_image_size_mb,
        max_video_size_mb=settings.max_video_size_mb,
    )
    return MediaResponse.model_validate(media)


@router.get("", response_model=MediaListResponse)
def list_media(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    media_type: Annotated[str | None, Query()] = None,
    owner_id: Annotated[UUID | None, Query()] = None,
) -> MediaListResponse:
    items, total = list_visible_media(
        session=session,
        current_user=current_user,
        limit=limit,
        offset=offset,
        media_type=media_type,
        owner_id=owner_id,
    )
    return MediaListResponse(
        items=[MediaResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{media_id}", response_model=MediaResponse)
def get_media(
    media_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> MediaResponse:
    return MediaResponse.model_validate(get_visible_media(session, media_id, current_user))


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    soft_delete_media(session, media_id, current_user)
