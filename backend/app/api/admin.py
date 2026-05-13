from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.authorization import get_current_admin_user
from app.core.config import Settings, get_settings
from app.db.models import User
from app.schemas.admin import (
    AdminJobListResponse,
    AdminStatsResponse,
    AdminUserListResponse,
    StorageCleanupRequest,
    StorageCleanupResponse,
)
from app.services.admin import cleanup_storage, get_admin_stats, list_admin_users
from app.services.results import list_visible_jobs

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> AdminStatsResponse:
    del current_user
    return get_admin_stats(session)


@router.get("/jobs", response_model=AdminJobListResponse)
def list_jobs(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    media_type: str | None = None,
    model_version_id: UUID | None = None,
    owner_id: UUID | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> AdminJobListResponse:
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
    return AdminJobListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AdminUserListResponse:
    del current_user
    items, total = list_admin_users(session, limit=limit, offset=offset)
    return AdminUserListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/storage/cleanup", response_model=StorageCleanupResponse)
def cleanup(
    payload: StorageCleanupRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> StorageCleanupResponse:
    del current_user
    return cleanup_storage(session, storage_root=settings.storage_root, dry_run=payload.dry_run)
