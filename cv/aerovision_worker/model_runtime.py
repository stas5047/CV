from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.settings import WorkerSettings
from aerovision_worker.storage_paths import safe_join_storage_path

LOGGER = logging.getLogger("aerovision_worker.model_runtime")


class ModelLoadingError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelMetadata:
    id: str
    name: str
    model_family: str
    variant: str | None
    weights_path: str


@dataclass(frozen=True)
class LoadedModel:
    metadata: ModelMetadata
    model: Any
    device: str


ModelLoader = Callable[[Path], Any]


class ModelRuntime:
    def __init__(
        self,
        *,
        settings: WorkerSettings,
        selected_device: str,
        model_loader: ModelLoader | None = None,
    ) -> None:
        self._settings = settings
        self._selected_device = selected_device
        self._model_loader = model_loader or _load_ultralytics_model
        self._cache: dict[tuple[str, str], LoadedModel] = {}

    def load_for_job(
        self,
        session_factory: sessionmaker[Session],
        *,
        job_id: Any,
    ) -> LoadedModel:
        metadata = resolve_model_metadata(session_factory, job_id=job_id, settings=self._settings)
        cache_key = (metadata.id, self._selected_device)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        weights_path = resolve_weights_path(self._settings, metadata.weights_path)
        LOGGER.info(
            "model_loading model_id=%s model_family=%s variant=%s device=%s",
            metadata.id,
            metadata.model_family,
            metadata.variant,
            self._selected_device,
        )
        model = self._model_loader(weights_path)
        model = _move_model_to_device(model, self._selected_device)
        loaded = LoadedModel(metadata=metadata, model=model, device=self._selected_device)
        self._cache[cache_key] = loaded
        LOGGER.info(
            "model_loaded model_id=%s model_family=%s variant=%s device=%s",
            metadata.id,
            metadata.model_family,
            metadata.variant,
            self._selected_device,
        )
        return loaded


def resolve_model_metadata(
    session_factory: sessionmaker[Session],
    *,
    job_id: Any,
    settings: WorkerSettings,
) -> ModelMetadata:
    with session_factory() as session:
        job_model_id = session.execute(
            text(
                """
                select model_version_id
                from processing_jobs
                where id = :job_id
                  and deleted_at is null
                """
            ),
            {"job_id": job_id},
        ).scalar_one_or_none()
        if job_model_id is not None:
            return _fetch_model_by_id(session, model_id=job_model_id)

        active = _fetch_active_model(session)
        if active is not None:
            return active

        if settings.active_model_id:
            return _fetch_model_by_id(session, model_id=settings.active_model_id)

    raise ModelLoadingError("No model version available for job")


def resolve_weights_path(settings: WorkerSettings, weights_path: str) -> Path:
    try:
        if _is_documented_storage_path(weights_path):
            resolved = safe_join_storage_path(settings.storage_root, weights_path)
        else:
            resolved = safe_join_storage_path(settings.models_root, weights_path)
    except ValueError as exc:
        raise ModelLoadingError("Model weights path is unsafe") from exc

    if not resolved.is_file():
        raise ModelLoadingError("Model weights file is missing")
    return resolved


def _fetch_model_by_id(session: Session, *, model_id: Any) -> ModelMetadata:
    row = (
        session.execute(
            text(
                """
                select id, name, model_family, variant, weights_path
                from model_versions
                where id = :model_id
                """
            ),
            {"model_id": model_id},
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        raise ModelLoadingError("Model version is unavailable")
    return _metadata_from_row(row)


def _fetch_active_model(session: Session) -> ModelMetadata | None:
    row = (
        session.execute(
            text(
                """
                select id, name, model_family, variant, weights_path
                from model_versions
                where is_active = true
                order by created_at desc
                limit 1
                """
            )
        )
        .mappings()
        .one_or_none()
    )
    if row is None:
        return None
    return _metadata_from_row(row)


def _metadata_from_row(row) -> ModelMetadata:
    return ModelMetadata(
        id=str(row["id"]),
        name=str(row["name"]),
        model_family=str(row["model_family"]),
        variant=None if row["variant"] is None else str(row["variant"]),
        weights_path=str(row["weights_path"]),
    )


def _is_documented_storage_path(weights_path: str) -> bool:
    normalized = weights_path.replace("\\", "/").strip()
    return normalized == "models" or normalized.startswith("models/")


def _load_ultralytics_model(weights_path: Path):
    try:
        from ultralytics import YOLO
    except Exception as exc:
        raise ModelLoadingError("Ultralytics YOLO runtime is unavailable") from exc

    try:
        return YOLO(str(weights_path))
    except Exception as exc:
        raise ModelLoadingError("Model weights could not be loaded") from exc


def _move_model_to_device(model, selected_device: str):
    to_device = getattr(model, "to", None)
    if callable(to_device):
        moved = to_device(selected_device)
        return model if moved is None else moved
    return model
