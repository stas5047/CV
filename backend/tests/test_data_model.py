from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import (
    Base,
    Detection,
    ExperimentMetric,
    ExperimentRun,
    MediaFile,
    ModelVersion,
    ProcessingJob,
    Track,
    User,
)

REQUIRED_TABLES = {
    "users",
    "media_files",
    "processing_jobs",
    "detections",
    "tracks",
    "model_versions",
    "experiment_runs",
    "experiment_metrics",
}

REQUIRED_INDEXES = {
    "media_files": {"ix_media_files_user_created_at"},
    "processing_jobs": {
        "ix_processing_jobs_status_created_at",
        "ix_processing_jobs_user_created_at",
        "ix_processing_jobs_media_created_at",
    },
    "detections": {
        "ix_detections_job_frame",
        "ix_detections_media_frame",
    },
    "tracks": {"ix_tracks_job_track"},
    "experiment_runs": {"ix_experiment_runs_type_created_at"},
    "experiment_metrics": {"ix_experiment_metrics_run"},
}


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


def commit_raises(session: Session) -> None:
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def add_user(session: Session, *, email: str = "user@example.local", role: str = "user") -> User:
    user = User(email=email, password_hash="hashed-password", role=role)
    session.add(user)
    session.commit()
    return user


def add_media(
    session: Session,
    user: User,
    *,
    media_type: str = "image",
    stored_path: str = "uploads/user/media/original.jpg",
) -> MediaFile:
    media = MediaFile(
        user_id=user.id,
        original_filename="original.jpg",
        stored_path=stored_path,
        media_type=media_type,
        mime_type="image/jpeg" if media_type == "image" else "video/mp4",
        file_size_bytes=1234,
        width=640,
        height=480,
        frame_count=1 if media_type == "image" else 10,
        fps=None if media_type == "image" else 30.0,
        duration_seconds=None if media_type == "image" else 0.33,
    )
    session.add(media)
    session.commit()
    return media


def add_model(
    session: Session,
    user: User,
    *,
    name: str,
    is_active: bool,
    weights_path: str = "models/model/weights.pt",
) -> ModelVersion:
    model = ModelVersion(
        name=name,
        model_family="YOLO26",
        variant="s",
        weights_path=weights_path,
        dataset_name="Seraphim",
        dataset_split_description="train/val/test",
        metrics_json={"map50": 0.7},
        is_active=is_active,
        created_by_user_id=user.id,
    )
    session.add(model)
    session.commit()
    return model


def add_job(session: Session, user: User, media: MediaFile, model: ModelVersion) -> ProcessingJob:
    job = ProcessingJob(
        user_id=user.id,
        media_file_id=media.id,
        model_version_id=model.id,
        status="queued",
        input_params_json={
            "confidence_threshold": 0.25,
            "iou_threshold": 0.45,
            "image_size": 640,
            "tracker_type": "bytetrack",
            "frame_stride": 1,
        },
        progress_percent=0,
    )
    session.add(job)
    session.commit()
    return job


def test_metadata_registers_all_required_tables() -> None:
    assert REQUIRED_TABLES <= set(Base.metadata.tables)


def test_required_indexes_are_declared() -> None:
    for table_name, index_names in REQUIRED_INDEXES.items():
        table = Base.metadata.tables[table_name]
        assert index_names <= {index.name for index in table.indexes}


def test_users_enforce_unique_email_and_valid_role(db_session: Session) -> None:
    add_user(db_session)

    db_session.add(User(email="user@example.local", password_hash="hash", role="user"))
    commit_raises(db_session)

    db_session.add(User(email="bad-role@example.local", password_hash="hash", role="owner"))
    commit_raises(db_session)


def test_media_enforces_type_image_invariants_and_relative_path(db_session: Session) -> None:
    user = add_user(db_session)
    add_media(db_session, user)

    db_session.add(
        MediaFile(
            user_id=user.id,
            original_filename="bad.jpg",
            stored_path="uploads/user/bad/original.jpg",
            media_type="image",
            mime_type="image/jpeg",
            file_size_bytes=1,
            width=100,
            height=100,
            frame_count=2,
            fps=None,
            duration_seconds=None,
        )
    )
    commit_raises(db_session)

    db_session.add(
        MediaFile(
            user_id=user.id,
            original_filename="bad.jpg",
            stored_path="uploads/user/bad-null-frame/original.jpg",
            media_type="image",
            mime_type="image/jpeg",
            file_size_bytes=1,
            width=100,
            height=100,
            frame_count=None,
            fps=None,
            duration_seconds=None,
        )
    )
    commit_raises(db_session)

    db_session.add(
        MediaFile(
            user_id=user.id,
            original_filename="bad.jpg",
            stored_path="uploads/user/bad2/original.jpg",
            media_type="image",
            mime_type="image/jpeg",
            file_size_bytes=1,
            width=100,
            height=100,
            frame_count=1,
            fps=30.0,
            duration_seconds=None,
        )
    )
    commit_raises(db_session)

    db_session.add(
        MediaFile(
            user_id=user.id,
            original_filename="bad.jpg",
            stored_path="uploads/user/bad3/original.jpg",
            media_type="image",
            mime_type="image/jpeg",
            file_size_bytes=1,
            width=100,
            height=100,
            frame_count=1,
            fps=None,
            duration_seconds=1.0,
        )
    )
    commit_raises(db_session)

    for unsafe_path in [
        "/app/storage/uploads/file.jpg",
        "C:/storage/uploads/file.jpg",
        "\\\\server\\share\\file.jpg",
        "uploads/../secret/file.jpg",
        "uploads/secret/..",
        "uploads\\secret\\..",
    ]:
        db_session.add(
            MediaFile(
                user_id=user.id,
                original_filename="bad.jpg",
                stored_path=unsafe_path,
                media_type="image",
                mime_type="image/jpeg",
                file_size_bytes=1,
                width=100,
                height=100,
                frame_count=1,
                fps=None,
                duration_seconds=None,
            )
        )
        commit_raises(db_session)


def test_model_versions_allow_many_inactive_but_only_one_active(db_session: Session) -> None:
    admin = add_user(db_session, email="admin@example.local", role="admin")
    add_model(db_session, admin, name="inactive-1", is_active=False)
    add_model(db_session, admin, name="inactive-2", is_active=False)
    add_model(db_session, admin, name="active-1", is_active=True)

    db_session.add(
        ModelVersion(
            name="active-2",
            model_family="YOLO26",
            variant="s",
            weights_path="models/active-2/weights.pt",
            dataset_name="Seraphim",
            dataset_split_description="train/val/test",
            metrics_json={},
            is_active=True,
            created_by_user_id=admin.id,
        )
    )
    commit_raises(db_session)

    for unsafe_path in ["../weights.pt", "models/..", "models\\.."]:
        db_session.add(
            ModelVersion(
                name=f"unsafe-{unsafe_path}",
                model_family="YOLO26",
                variant="s",
                weights_path=unsafe_path,
                dataset_name="Seraphim",
                dataset_split_description="train/val/test",
                metrics_json={},
                is_active=False,
                created_by_user_id=admin.id,
            )
        )
        commit_raises(db_session)


def test_processing_jobs_enforce_status_progress_paths_and_foreign_keys(
    db_session: Session,
) -> None:
    user = add_user(db_session)
    admin = add_user(db_session, email="admin@example.local", role="admin")
    media = add_media(db_session, user)
    model = add_model(db_session, admin, name="active", is_active=True)
    add_job(db_session, user, media, model)

    db_session.add(
        ProcessingJob(
            user_id=user.id,
            media_file_id=media.id,
            model_version_id=model.id,
            status="waiting",
            input_params_json={},
            progress_percent=0,
        )
    )
    commit_raises(db_session)

    db_session.add(
        ProcessingJob(
            user_id=user.id,
            media_file_id=media.id,
            model_version_id=model.id,
            status="queued",
            input_params_json={},
            progress_percent=101,
        )
    )
    commit_raises(db_session)

    db_session.add(
        ProcessingJob(
            user_id=user.id,
            media_file_id=uuid4(),
            model_version_id=model.id,
            status="queued",
            input_params_json={},
            progress_percent=0,
        )
    )
    commit_raises(db_session)


def test_detections_tracks_and_metrics_relationship_constraints(db_session: Session) -> None:
    user = add_user(db_session)
    admin = add_user(db_session, email="admin@example.local", role="admin")
    media = add_media(db_session, user, media_type="video", stored_path="uploads/u/m/original.mp4")
    model = add_model(db_session, admin, name="active", is_active=True)
    job = add_job(db_session, user, media, model)

    db_session.add(
        Detection(
            job_id=job.id,
            media_file_id=media.id,
            frame_index=0,
            timestamp_ms=0,
            class_id=0,
            class_name="drone",
            confidence=0.9,
            bbox_x1=1,
            bbox_y1=2,
            bbox_x2=100,
            bbox_y2=120,
            frame_width=640,
            frame_height=480,
            track_id=7,
        )
    )
    db_session.add(
        Track(
            job_id=job.id,
            track_id=7,
            class_name="drone",
            first_frame_index=0,
            last_frame_index=5,
            frames_count=6,
            average_confidence=0.8,
            max_confidence=0.9,
        )
    )
    db_session.commit()

    db_session.add(
        Track(
            job_id=job.id,
            track_id=7,
            class_name="drone",
            first_frame_index=1,
            last_frame_index=6,
            frames_count=6,
            average_confidence=0.8,
            max_confidence=0.9,
        )
    )
    commit_raises(db_session)

    run = ExperimentRun(
        name="Threshold analysis",
        experiment_type="threshold_analysis",
        description="Imported metrics",
        model_version_id=model.id,
        dataset_name="Seraphim",
        config_json={},
        artifacts_path="reports/experiment/metrics.json",
        is_published=True,
        created_by_user_id=admin.id,
    )
    db_session.add(run)
    db_session.commit()

    db_session.add(
        ExperimentMetric(
            experiment_run_id=run.id,
            metric_name="map50",
            metric_value=None,
            metric_unit=None,
            metadata_json={},
        )
    )
    db_session.commit()

    db_session.add(
        ExperimentRun(
            name="Bad type",
            experiment_type="tracking_accuracy",
            description=None,
            model_version_id=model.id,
            dataset_name="Seraphim",
            config_json={},
            artifacts_path=None,
            is_published=False,
            created_by_user_id=admin.id,
            created_at=datetime.now(UTC),
        )
    )
    commit_raises(db_session)
