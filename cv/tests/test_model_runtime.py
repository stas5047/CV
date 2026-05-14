from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from aerovision_worker.model_runtime import (
    ModelLoadingError,
    ModelRuntime,
    resolve_model_metadata,
    resolve_weights_path,
)
from aerovision_worker.settings import WorkerSettings


def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                create table processing_jobs (
                    id text primary key,
                    model_version_id text null,
                    status text not null,
                    deleted_at timestamp null,
                    created_at timestamp not null
                )
                """
            )
        )
        connection.execute(
            text(
                """
                create table model_versions (
                    id text primary key,
                    name text not null,
                    model_family text not null,
                    variant text null,
                    weights_path text not null,
                    is_active boolean not null,
                    created_at timestamp not null
                )
                """
            )
        )
    return factory


def insert_model(
    factory: sessionmaker[Session],
    *,
    model_id: str,
    family: str = "YOLO26",
    variant: str = "s",
    weights_path: str | None = None,
    is_active: bool = False,
    created_at: datetime | None = None,
) -> None:
    created_at = created_at or datetime(2026, 5, 14, 12, 0, tzinfo=UTC)
    with factory.begin() as session:
        session.execute(
            text(
                """
                insert into model_versions (
                    id, name, model_family, variant, weights_path, is_active, created_at
                )
                values (
                    :id, :name, :model_family, :variant, :weights_path, :is_active, :created_at
                )
                """
            ),
            {
                "id": model_id,
                "name": f"{family} {variant}",
                "model_family": family,
                "variant": variant,
                "weights_path": weights_path or f"models/{model_id}/weights.pt",
                "is_active": is_active,
                "created_at": created_at,
            },
        )


def insert_job(
    factory: sessionmaker[Session],
    *,
    job_id: str = "job-1",
    model_version_id: str | None = None,
) -> None:
    with factory.begin() as session:
        session.execute(
            text(
                """
                insert into processing_jobs (id, model_version_id, status, deleted_at, created_at)
                values (:id, :model_version_id, 'processing', null, :created_at)
                """
            ),
            {
                "id": job_id,
                "model_version_id": model_version_id,
                "created_at": datetime(2026, 5, 14, 12, 0, tzinfo=UTC),
            },
        )


def test_resolve_model_metadata_uses_job_model_before_active_and_env_fallback() -> None:
    factory = session_factory()
    insert_model(factory, model_id="job-model", family="YOLO26", is_active=False)
    insert_model(factory, model_id="active-model", family="YOLO26", is_active=True)
    insert_model(factory, model_id="env-model", family="YOLO26", is_active=False)
    insert_job(factory, model_version_id="job-model")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        active_model_id="env-model",
    )

    metadata = resolve_model_metadata(factory, job_id="job-1", settings=settings)

    assert metadata.id == "job-model"


def test_resolve_model_metadata_uses_active_model_before_env_fallback() -> None:
    factory = session_factory()
    insert_model(factory, model_id="env-model", is_active=False)
    insert_model(factory, model_id="active-model", is_active=True)
    insert_job(factory, model_version_id=None)
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        active_model_id="env-model",
    )

    metadata = resolve_model_metadata(factory, job_id="job-1", settings=settings)

    assert metadata.id == "active-model"


def test_resolve_model_metadata_uses_env_fallback_only_without_active_model() -> None:
    factory = session_factory()
    insert_model(factory, model_id="env-model", is_active=False)
    insert_job(factory, model_version_id=None)
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        active_model_id="env-model",
    )

    metadata = resolve_model_metadata(factory, job_id="job-1", settings=settings)

    assert metadata.id == "env-model"


def test_resolve_model_metadata_fails_safely_when_no_model_available() -> None:
    factory = session_factory()
    insert_job(factory, model_version_id=None)
    settings = WorkerSettings(database_url="sqlite+pysqlite:///:memory:")

    with pytest.raises(ModelLoadingError) as excinfo:
        resolve_model_metadata(factory, job_id="job-1", settings=settings)

    assert str(excinfo.value) == "No model version available for job"


def test_resolve_weights_path_uses_documented_storage_root_without_double_models(
    tmp_path: Path,
) -> None:
    storage_root = tmp_path / "storage"
    weights = storage_root / "models" / "model-a" / "weights.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"fake")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )

    resolved = resolve_weights_path(settings, "models/model-a/weights.pt")

    assert resolved == weights.resolve()


def test_resolve_weights_path_supports_bare_models_root_compatibility(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    weights = storage_root / "models" / "model-a" / "weights.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"fake")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )

    resolved = resolve_weights_path(settings, "model-a/weights.pt")

    assert resolved == weights.resolve()


@pytest.mark.parametrize(
    "weights_path",
    [
        "/app/storage/models/model-a/weights.pt",
        r"C:\storage\models\model-a\weights.pt",
        "../models/model-a/weights.pt",
        "models/../model-a/weights.pt",
    ],
)
def test_resolve_weights_path_rejects_unsafe_paths(tmp_path: Path, weights_path: str) -> None:
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(tmp_path / "storage"),
        models_root=str(tmp_path / "storage" / "models"),
    )

    with pytest.raises(ModelLoadingError) as excinfo:
        resolve_weights_path(settings, weights_path)

    assert str(excinfo.value) == "Model weights path is unsafe"


def test_resolve_weights_path_missing_file_error_hides_absolute_path(tmp_path: Path) -> None:
    storage_root = tmp_path / "storage"
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )

    with pytest.raises(ModelLoadingError) as excinfo:
        resolve_weights_path(settings, "models/model-a/weights.pt")

    message = str(excinfo.value)
    assert message == "Model weights file is missing"
    assert str(storage_root) not in message


def test_model_runtime_caches_by_model_id_and_device(tmp_path: Path) -> None:
    factory = session_factory()
    storage_root = tmp_path / "storage"
    for model_id in ("model-a", "model-b"):
        weights = storage_root / "models" / model_id / "weights.pt"
        weights.parent.mkdir(parents=True)
        weights.write_bytes(b"fake")
        insert_model(factory, model_id=model_id, weights_path=f"models/{model_id}/weights.pt")
    insert_job(factory, job_id="job-a", model_version_id="model-a")
    insert_job(factory, job_id="job-b", model_version_id="model-b")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )
    loads: list[tuple[Path, str]] = []

    def loader(path: Path):
        model = SimpleNamespace(path=path, moved_to=None)

        def to(device: str):
            model.moved_to = device
            return model

        model.to = to
        loads.append((path, "load"))
        return model

    runtime = ModelRuntime(settings=settings, selected_device="cpu", model_loader=loader)

    first = runtime.load_for_job(factory, job_id="job-a")
    second = runtime.load_for_job(factory, job_id="job-a")
    third = runtime.load_for_job(factory, job_id="job-b")

    assert first.model is second.model
    assert first.model is not third.model
    assert len(loads) == 2
    assert first.model.moved_to == "cpu"


def test_model_runtime_preserves_yolo_family_metadata(tmp_path: Path) -> None:
    factory = session_factory()
    storage_root = tmp_path / "storage"
    weights = storage_root / "models" / "fallback" / "weights.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"fake")
    insert_model(
        factory,
        model_id="fallback",
        family="YOLO11",
        variant="s",
        weights_path="models/fallback/weights.pt",
        is_active=True,
    )
    insert_job(factory, model_version_id="fallback")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )
    runtime = ModelRuntime(
        settings=settings,
        selected_device="cpu",
        model_loader=lambda path: SimpleNamespace(to=lambda device: None),
    )

    loaded = runtime.load_for_job(factory, job_id="job-1")

    assert loaded.metadata.model_family == "YOLO11"


def test_model_runtime_logs_without_absolute_paths(tmp_path: Path, caplog) -> None:
    factory = session_factory()
    storage_root = tmp_path / "storage"
    weights = storage_root / "models" / "model-a" / "weights.pt"
    weights.parent.mkdir(parents=True)
    weights.write_bytes(b"fake")
    insert_model(factory, model_id="model-a", weights_path="models/model-a/weights.pt")
    insert_job(factory, model_version_id="model-a")
    settings = WorkerSettings(
        database_url="sqlite+pysqlite:///:memory:",
        storage_root=str(storage_root),
        models_root=str(storage_root / "models"),
    )
    runtime = ModelRuntime(
        settings=settings,
        selected_device="cpu",
        model_loader=lambda path: SimpleNamespace(to=lambda device: None),
    )
    caplog.set_level(logging.INFO, logger="aerovision_worker.model_runtime")

    runtime.load_for_job(factory, job_id="job-1")

    assert "model_loaded model_id=model-a model_family=YOLO26 variant=s device=cpu" in caplog.text
    assert str(storage_root) not in caplog.text
