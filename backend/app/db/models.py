from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def utc_now() -> datetime:
    return datetime.now(UTC)


def uuid_pk() -> Mapped[UUID]:
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)


def created_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


def updated_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


def relative_path_check(column_name: str) -> CheckConstraint:
    return CheckConstraint(
        f"{column_name} IS NULL OR ("
        f"{column_name} <> '' AND "
        f"{column_name} <> '..' AND "
        f"substr({column_name}, 1, 1) <> '/' AND "
        f"substr({column_name}, 1, 1) <> '\\' AND "
        f"substr({column_name}, 2, 1) <> ':' AND "
        f"{column_name} NOT LIKE '../%' AND "
        f"{column_name} NOT LIKE '%/../%' AND "
        f"{column_name} NOT LIKE '%/..' AND "
        f"{column_name} NOT LIKE '..\\%' AND "
        f"{column_name} NOT LIKE '%\\..\\%' AND "
        f"{column_name} NOT LIKE '%\\..'"
        ")",
        name=f"{column_name}_relative_path",
    )


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name="role_valid"),
    )

    id: Mapped[UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    media_files: Mapped[list[MediaFile]] = relationship(back_populates="user")
    processing_jobs: Mapped[list[ProcessingJob]] = relationship(back_populates="user")
    created_models: Mapped[list[ModelVersion]] = relationship(back_populates="created_by_user")
    created_experiments: Mapped[list[ExperimentRun]] = relationship(
        back_populates="created_by_user"
    )


class MediaFile(Base):
    __tablename__ = "media_files"
    __table_args__ = (
        CheckConstraint("media_type IN ('image', 'video')", name="media_type_valid"),
        CheckConstraint(
            "media_type <> 'image' OR "
            "(frame_count IS NOT NULL AND frame_count = 1 "
            "AND fps IS NULL AND duration_seconds IS NULL)",
            name="image_metadata_valid",
        ),
        relative_path_check("stored_path"),
        Index("ix_media_files_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[UUID] = uuid_pk()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    frame_count: Mapped[int | None] = mapped_column(Integer)
    fps: Mapped[float | None] = mapped_column(Float)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at_column()

    user: Mapped[User] = relationship(back_populates="media_files")
    processing_jobs: Mapped[list[ProcessingJob]] = relationship(back_populates="media_file")
    detections: Mapped[list[Detection]] = relationship(back_populates="media_file")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        CheckConstraint("model_family IN ('YOLO26', 'YOLO11')", name="model_family_valid"),
        relative_path_check("weights_path"),
        Index(
            "uq_model_versions_active_true",
            "is_active",
            unique=True,
            postgresql_where=text("is_active"),
            sqlite_where=text("is_active = 1"),
        ),
    )

    id: Mapped[UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_family: Mapped[str] = mapped_column(String(20), nullable=False)
    variant: Mapped[str] = mapped_column(String(50), nullable=False)
    weights_path: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_name: Mapped[str | None] = mapped_column(String(255))
    dataset_split_description: Mapped[str | None] = mapped_column(Text)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    created_by_user: Mapped[User | None] = relationship(back_populates="created_models")
    processing_jobs: Mapped[list[ProcessingJob]] = relationship(back_populates="model_version")
    experiment_runs: Mapped[list[ExperimentRun]] = relationship(back_populates="model_version")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')",
            name="status_valid",
        ),
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="progress_percent_range",
        ),
        relative_path_check("result_media_path"),
        relative_path_check("csv_path"),
        relative_path_check("json_path"),
        Index("ix_processing_jobs_status_created_at", "status", "created_at"),
        Index("ix_processing_jobs_user_created_at", "user_id", "created_at"),
        Index("ix_processing_jobs_media_created_at", "media_file_id", "created_at"),
    )

    id: Mapped[UUID] = uuid_pk()
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    media_file_id: Mapped[UUID] = mapped_column(ForeignKey("media_files.id"), nullable=False)
    model_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("model_versions.id"))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    input_params_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    summary_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    result_media_path: Mapped[str | None] = mapped_column(Text)
    csv_path: Mapped[str | None] = mapped_column(Text)
    json_path: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    progress_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_by: Mapped[str | None] = mapped_column(String(255))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = updated_at_column()

    user: Mapped[User] = relationship(back_populates="processing_jobs")
    media_file: Mapped[MediaFile] = relationship(back_populates="processing_jobs")
    model_version: Mapped[ModelVersion | None] = relationship(back_populates="processing_jobs")
    detections: Mapped[list[Detection]] = relationship(back_populates="job")
    tracks: Mapped[list[Track]] = relationship(back_populates="job")


class Detection(Base):
    __tablename__ = "detections"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        CheckConstraint("bbox_x2 >= bbox_x1 AND bbox_y2 >= bbox_y1", name="bbox_order_valid"),
        Index("ix_detections_job_frame", "job_id", "frame_index"),
        Index("ix_detections_media_frame", "media_file_id", "frame_index"),
    )

    id: Mapped[UUID] = uuid_pk()
    job_id: Mapped[UUID] = mapped_column(ForeignKey("processing_jobs.id"), nullable=False)
    media_file_id: Mapped[UUID] = mapped_column(ForeignKey("media_files.id"), nullable=False)
    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_name: Mapped[str] = mapped_column(String(80), nullable=False, default="drone")
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x2: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y2: Mapped[float] = mapped_column(Float, nullable=False)
    frame_width: Mapped[int] = mapped_column(Integer, nullable=False)
    frame_height: Mapped[int] = mapped_column(Integer, nullable=False)
    track_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = created_at_column()

    job: Mapped[ProcessingJob] = relationship(back_populates="detections")
    media_file: Mapped[MediaFile] = relationship(back_populates="detections")


class Track(Base):
    __tablename__ = "tracks"
    __table_args__ = (
        UniqueConstraint("job_id", "track_id", name="uq_tracks_job_track_id"),
        CheckConstraint("frames_count >= 0", name="frames_count_nonnegative"),
        CheckConstraint("last_frame_index >= first_frame_index", name="frame_range_valid"),
        CheckConstraint(
            "average_confidence IS NULL OR "
            "(average_confidence >= 0 AND average_confidence <= 1)",
            name="average_confidence_range",
        ),
        CheckConstraint(
            "max_confidence IS NULL OR (max_confidence >= 0 AND max_confidence <= 1)",
            name="max_confidence_range",
        ),
        Index("ix_tracks_job_track", "job_id", "track_id"),
    )

    id: Mapped[UUID] = uuid_pk()
    job_id: Mapped[UUID] = mapped_column(ForeignKey("processing_jobs.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_name: Mapped[str] = mapped_column(String(80), nullable=False, default="drone")
    first_frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    last_frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    frames_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_confidence: Mapped[float | None] = mapped_column(Float)
    max_confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = created_at_column()

    job: Mapped[ProcessingJob] = relationship(back_populates="tracks")


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"
    __table_args__ = (
        CheckConstraint(
            "experiment_type IN ("
            "'model_comparison', "
            "'threshold_analysis', "
            "'tracker_comparison', "
            "'false_positive_analysis'"
            ")",
            name="experiment_type_valid",
        ),
        relative_path_check("artifacts_path"),
        Index("ix_experiment_runs_type_created_at", "experiment_type", "created_at"),
    )

    id: Mapped[UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    experiment_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    model_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("model_versions.id"))
    dataset_name: Mapped[str | None] = mapped_column(String(255))
    config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    artifacts_path: Mapped[str | None] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = created_at_column()

    model_version: Mapped[ModelVersion | None] = relationship(back_populates="experiment_runs")
    created_by_user: Mapped[User | None] = relationship(back_populates="created_experiments")
    metrics: Mapped[list[ExperimentMetric]] = relationship(back_populates="experiment_run")


class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"
    __table_args__ = (
        Index("ix_experiment_metrics_run", "experiment_run_id"),
    )

    id: Mapped[UUID] = uuid_pk()
    experiment_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("experiment_runs.id"),
        nullable=False,
    )
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_value: Mapped[float | None] = mapped_column(Float)
    metric_unit: Mapped[str | None] = mapped_column(String(80))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = created_at_column()

    experiment_run: Mapped[ExperimentRun] = relationship(back_populates="metrics")
