from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.auth import get_current_active_user
from app.core.config import Settings, get_settings
from app.db.models import User
from app.schemas.jobs import JobCreateRequest, JobResponse
from app.services.jobs import create_processing_job

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
