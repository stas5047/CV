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
from app.schemas.experiments import (
    ExperimentImportRequest,
    ExperimentListResponse,
    ExperimentResponse,
    ExperimentType,
)
from app.services.experiments import get_experiment, import_experiment, list_experiments

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=ExperimentListResponse)
def list_experiment_runs(
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    experiment_type: Annotated[ExperimentType | None, Query()] = None,
    is_published: Annotated[bool | None, Query()] = None,
) -> ExperimentListResponse:
    items, total = list_experiments(
        session=session,
        current_user=current_user,
        limit=limit,
        offset=offset,
        experiment_type=experiment_type,
        is_published=is_published,
    )
    return ExperimentListResponse(
        items=[ExperimentResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/import", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def import_experiment_run(
    payload: ExperimentImportRequest,
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_admin_user)],
) -> ExperimentResponse:
    return ExperimentResponse.model_validate(
        import_experiment(
            session=session,
            payload=payload,
            current_user=current_user,
            storage_root=settings.storage_root,
        )
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment_run(
    experiment_id: UUID,
    session: Annotated[Session, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ExperimentResponse:
    return ExperimentResponse.model_validate(
        get_experiment(
            session=session,
            experiment_id=experiment_id,
            current_user=current_user,
        )
    )
