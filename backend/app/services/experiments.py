from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.authorization import SAFE_NOT_FOUND_DETAIL
from app.core.storage_paths import safe_join_storage_path, validate_relative_storage_path
from app.db.models import ExperimentMetric, ExperimentRun, ModelVersion, User
from app.schemas.experiments import ExperimentImportRequest, ExperimentType

ALLOWED_EXPERIMENT_TYPES = {
    "model_comparison",
    "threshold_analysis",
    "tracker_comparison",
    "false_positive_analysis",
}
FORBIDDEN_TRACKER_TERMS = {"tracking_accuracy", "mota", "idf1", "hota"}


def list_experiments(
    *,
    session: Session,
    current_user: User,
    limit: int,
    offset: int,
    experiment_type: ExperimentType | None,
    is_published: bool | None,
) -> tuple[list[ExperimentRun], int]:
    statement = select(ExperimentRun).options(selectinload(ExperimentRun.metrics))
    count_statement = select(func.count()).select_from(ExperimentRun)

    statement, count_statement = _apply_visibility(
        statement=statement,
        count_statement=count_statement,
        current_user=current_user,
        is_published=is_published,
    )
    if experiment_type is not None:
        statement = statement.where(ExperimentRun.experiment_type == experiment_type)
        count_statement = count_statement.where(ExperimentRun.experiment_type == experiment_type)

    total = session.scalar(count_statement) or 0
    items = list(
        session.scalars(
            statement.order_by(ExperimentRun.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
    )
    return items, total


def get_experiment(
    *,
    session: Session,
    experiment_id: UUID,
    current_user: User,
) -> ExperimentRun:
    statement = (
        select(ExperimentRun)
        .options(selectinload(ExperimentRun.metrics))
        .where(ExperimentRun.id == experiment_id)
    )
    if current_user.role != "admin":
        statement = statement.where(ExperimentRun.is_published.is_(True))

    experiment = session.scalar(statement)
    if experiment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=SAFE_NOT_FOUND_DETAIL)
    return experiment


def import_experiment(
    *,
    session: Session,
    payload: ExperimentImportRequest,
    current_user: User,
    storage_root: str,
) -> ExperimentRun:
    if (
        payload.model_version_id is not None
        and session.get(ModelVersion, payload.model_version_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model version not found",
        )

    artifacts_path = _validate_artifacts_path(payload.artifacts_path, storage_root)
    _validate_metric_safety(payload)

    experiment = ExperimentRun(
        name=payload.name,
        experiment_type=payload.experiment_type,
        description=payload.description,
        model_version_id=payload.model_version_id,
        dataset_name=payload.dataset_name,
        config_json=payload.config_json,
        artifacts_path=artifacts_path,
        is_published=payload.is_published,
        created_by_user_id=current_user.id,
    )
    session.add(experiment)
    session.flush()
    for metric in payload.metrics:
        session.add(
            ExperimentMetric(
                experiment_run_id=experiment.id,
                metric_name=metric.metric_name,
                metric_value=metric.metric_value,
                metric_unit=metric.metric_unit,
                metadata_json=metric.metadata_json,
            )
        )
    session.commit()
    return get_experiment(session=session, experiment_id=experiment.id, current_user=current_user)


def _apply_visibility(
    *,
    statement: Any,
    count_statement: Any,
    current_user: User,
    is_published: bool | None,
) -> tuple[Any, Any]:
    if current_user.role == "admin":
        if is_published is not None:
            statement = statement.where(ExperimentRun.is_published.is_(is_published))
            count_statement = count_statement.where(ExperimentRun.is_published.is_(is_published))
        return statement, count_statement

    statement = statement.where(ExperimentRun.is_published.is_(True))
    count_statement = count_statement.where(ExperimentRun.is_published.is_(True))
    return statement, count_statement


def _validate_artifacts_path(artifacts_path: str | None, storage_root: str) -> str | None:
    if artifacts_path is None:
        return None
    try:
        validated_path = validate_relative_storage_path(artifacts_path)
        resolved_path = safe_join_storage_path(storage_root, validated_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid experiment artifact path",
        ) from exc

    if not validated_path.startswith("reports/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment artifact path must be under reports storage",
        )
    if not resolved_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment artifact path does not exist",
        )
    return validated_path


def _validate_metric_safety(payload: ExperimentImportRequest) -> None:
    _reject_unsafe_metadata_paths(payload.config_json)
    for metric in payload.metrics:
        _reject_unsafe_metadata_paths(metric.metadata_json)
        if payload.experiment_type == "tracker_comparison":
            _reject_forbidden_tracker_terms(metric.metric_name)
            _reject_forbidden_tracker_terms(metric.metadata_json)


def _reject_forbidden_tracker_terms(value: Any) -> None:
    for text in _walk_text(value):
        normalized = text.strip().lower()
        compact = re.sub(r"[^a-z0-9]+", "", normalized)
        if any(
            term in normalized or term.replace("_", "") in compact
            for term in FORBIDDEN_TRACKER_TERMS
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tracker comparison metrics must use behavior indicators",
            )


def _reject_unsafe_metadata_paths(value: Any) -> None:
    for text in _walk_text(value):
        if _looks_like_absolute_path(text):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Metric metadata must not expose absolute paths",
            )


def _walk_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        texts: list[str] = []
        for key, nested_value in value.items():
            texts.extend(_walk_text(key))
            texts.extend(_walk_text(nested_value))
        return texts
    if isinstance(value, list | tuple):
        texts = []
        for nested_value in value:
            texts.extend(_walk_text(nested_value))
        return texts
    return []


def _looks_like_absolute_path(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    posix = PurePosixPath(text.replace("\\", "/"))
    windows = PureWindowsPath(text)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        return True
    return Path(text).is_absolute()
