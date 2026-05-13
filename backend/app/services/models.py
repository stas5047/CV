from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.storage_paths import safe_join_storage_path, validate_relative_storage_path
from app.db.models import ModelVersion, User, utc_now
from app.schemas.models import ModelCreateRequest

ALLOWED_MODEL_FAMILIES = {"YOLO26", "YOLO11"}


def list_model_versions(
    *,
    session: Session,
    limit: int,
    offset: int,
    is_active: bool | None,
    model_family: str | None,
    variant: str | None,
) -> tuple[list[ModelVersion], int]:
    statement = select(ModelVersion)
    count_statement = select(func.count()).select_from(ModelVersion)

    if is_active is not None:
        statement = statement.where(ModelVersion.is_active.is_(is_active))
        count_statement = count_statement.where(ModelVersion.is_active.is_(is_active))
    if model_family is not None:
        _validate_model_family(model_family)
        statement = statement.where(ModelVersion.model_family == model_family)
        count_statement = count_statement.where(ModelVersion.model_family == model_family)
    if variant is not None:
        statement = statement.where(ModelVersion.variant == variant)
        count_statement = count_statement.where(ModelVersion.variant == variant)

    total = session.scalar(count_statement) or 0
    items = list(
        session.scalars(
            statement.order_by(ModelVersion.created_at.desc()).limit(limit).offset(offset)
        )
    )
    return items, total


def get_model_version(session: Session, model_id: UUID) -> ModelVersion:
    model = session.get(ModelVersion, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return model


def create_model_version(
    *,
    session: Session,
    payload: ModelCreateRequest,
    current_user: User,
    storage_root: str,
    models_root: str,
) -> ModelVersion:
    weights_path = _validate_weights_path(payload.weights_path, storage_root, models_root)
    if payload.is_active:
        _deactivate_other_models(session)

    model = ModelVersion(
        name=payload.name,
        model_family=payload.model_family,
        variant=payload.variant,
        weights_path=weights_path,
        dataset_name=payload.dataset_name,
        dataset_split_description=payload.dataset_split_description,
        metrics_json=payload.metrics_json,
        is_active=payload.is_active,
        created_by_user_id=current_user.id,
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model


def activate_model_version(
    *,
    session: Session,
    model_id: UUID,
    storage_root: str,
    models_root: str,
) -> ModelVersion:
    model = get_model_version(session, model_id)
    _validate_weights_path(model.weights_path, storage_root, models_root)
    _deactivate_other_models(session, except_model_id=model.id)
    model.is_active = True
    model.updated_at = utc_now()
    session.commit()
    session.refresh(model)
    return model


def _validate_weights_path(weights_path: str, storage_root: str, models_root: str) -> str:
    try:
        validated_path = validate_relative_storage_path(weights_path)
        resolved_path = safe_join_storage_path(storage_root, validated_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model weights path",
        ) from exc

    if not validated_path.startswith("models/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model weights path must be under model storage",
        )

    resolved_models_root = Path(models_root).resolve()
    if resolved_path != resolved_models_root and resolved_models_root not in resolved_path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model weights path must be under model storage",
        )
    if not resolved_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model weights file does not exist",
        )
    return validated_path


def _validate_model_family(model_family: str) -> None:
    if model_family not in ALLOWED_MODEL_FAMILIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid model family",
        )


def _deactivate_other_models(session: Session, except_model_id: UUID | None = None) -> None:
    statement = update(ModelVersion).where(ModelVersion.is_active.is_(True))
    if except_model_id is not None:
        statement = statement.where(ModelVersion.id != except_model_id)
    session.execute(statement.values(is_active=False, updated_at=utc_now()))
    session.flush()
