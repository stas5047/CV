from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.auth import get_current_active_user
from app.core.authorization import get_current_admin_user
from app.core.config import Settings, get_settings
from app.db.models import User
from app.schemas.models import ModelCreateRequest, ModelListResponse, ModelResponse
from app.services.models import (
    activate_model_version,
    create_model_version,
    get_model_version,
    list_model_versions,
)

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=ModelListResponse)
def list_models(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    is_active: Annotated[bool | None, Query()] = None,
    model_family: Annotated[str | None, Query()] = None,
    variant: Annotated[str | None, Query()] = None,
) -> ModelListResponse:
    del current_user
    items, total = list_model_versions(
        session=session,
        limit=limit,
        offset=offset,
        is_active=is_active,
        model_family=model_family,
        variant=variant,
    )
    return ModelListResponse(
        items=[ModelResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(
    model_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ModelResponse:
    del current_user
    return ModelResponse.model_validate(get_model_version(session, model_id))


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    payload: ModelCreateRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> ModelResponse:
    model = create_model_version(
        session=session,
        payload=payload,
        current_user=current_user,
        storage_root=settings.storage_root,
        models_root=settings.models_root,
    )
    return ModelResponse.model_validate(model)


@router.patch("/{model_id}/activate", response_model=ModelResponse)
def activate_model(
    model_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> ModelResponse:
    del current_user
    return ModelResponse.model_validate(
        activate_model_version(
            session=session,
            model_id=model_id,
            storage_root=settings.storage_root,
            models_root=settings.models_root,
        )
    )
