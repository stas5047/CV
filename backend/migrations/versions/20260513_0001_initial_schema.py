"""initial schema

Revision ID: 20260513_0001
Revises:
Create Date: 2026-05-13 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260513_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def relative_path_check(column_name: str) -> str:
    return (
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
        ")"
    )


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('user', 'admin')", name=op.f("ck_users_role_valid")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)

    op.create_table(
        "media_files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.Text(), nullable=False),
        sa.Column("media_type", sa.String(length=20), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("frame_count", sa.Integer(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "media_type IN ('image', 'video')",
            name=op.f("ck_media_files_media_type_valid"),
        ),
        sa.CheckConstraint(
            "media_type <> 'image' OR "
            "(frame_count IS NOT NULL AND frame_count = 1 "
            "AND fps IS NULL AND duration_seconds IS NULL)",
            name=op.f("ck_media_files_image_metadata_valid"),
        ),
        sa.CheckConstraint(
            relative_path_check("stored_path"),
            name=op.f("ck_media_files_stored_path_relative_path"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_media_files_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_files")),
    )
    op.create_index(
        "ix_media_files_user_created_at",
        "media_files",
        ["user_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "model_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("model_family", sa.String(length=20), nullable=False),
        sa.Column("variant", sa.String(length=50), nullable=False),
        sa.Column("weights_path", sa.Text(), nullable=False),
        sa.Column("dataset_name", sa.String(length=255), nullable=True),
        sa.Column("dataset_split_description", sa.Text(), nullable=True),
        sa.Column("metrics_json", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "model_family IN ('YOLO26', 'YOLO11')",
            name=op.f("ck_model_versions_model_family_valid"),
        ),
        sa.CheckConstraint(
            relative_path_check("weights_path"),
            name=op.f("ck_model_versions_weights_path_relative_path"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_model_versions_created_by_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_model_versions")),
    )
    op.create_index(
        "uq_model_versions_active_true",
        "model_versions",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active"),
        sqlite_where=sa.text("is_active = 1"),
    )

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("media_file_id", sa.Uuid(), nullable=False),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("input_params_json", sa.JSON(), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=True),
        sa.Column("result_media_path", sa.Text(), nullable=True),
        sa.Column("csv_path", sa.Text(), nullable=True),
        sa.Column("json_path", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(length=255), nullable=True),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')",
            name=op.f("ck_processing_jobs_status_valid"),
        ),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name=op.f("ck_processing_jobs_progress_percent_range"),
        ),
        sa.CheckConstraint(
            relative_path_check("result_media_path"),
            name=op.f("ck_processing_jobs_result_media_path_relative_path"),
        ),
        sa.CheckConstraint(
            relative_path_check("csv_path"),
            name=op.f("ck_processing_jobs_csv_path_relative_path"),
        ),
        sa.CheckConstraint(
            relative_path_check("json_path"),
            name=op.f("ck_processing_jobs_json_path_relative_path"),
        ),
        sa.ForeignKeyConstraint(
            ["media_file_id"],
            ["media_files.id"],
            name=op.f("fk_processing_jobs_media_file_id_media_files"),
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_versions.id"],
            name=op.f("fk_processing_jobs_model_version_id_model_versions"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_processing_jobs_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_processing_jobs")),
    )
    op.create_index(
        "ix_processing_jobs_status_created_at",
        "processing_jobs",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_processing_jobs_user_created_at",
        "processing_jobs",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_processing_jobs_media_created_at",
        "processing_jobs",
        ["media_file_id", "created_at"],
        unique=False,
    )

    op.create_table(
        "experiment_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("experiment_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("dataset_name", sa.String(length=255), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("artifacts_path", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "experiment_type IN ('model_comparison', 'threshold_analysis', "
            "'tracker_comparison', 'false_positive_analysis')",
            name=op.f("ck_experiment_runs_experiment_type_valid"),
        ),
        sa.CheckConstraint(
            relative_path_check("artifacts_path"),
            name=op.f("ck_experiment_runs_artifacts_path_relative_path"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_experiment_runs_created_by_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["model_version_id"],
            ["model_versions.id"],
            name=op.f("fk_experiment_runs_model_version_id_model_versions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_experiment_runs")),
    )
    op.create_index(
        "ix_experiment_runs_type_created_at",
        "experiment_runs",
        ["experiment_type", "created_at"],
        unique=False,
    )

    op.create_table(
        "detections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("media_file_id", sa.Uuid(), nullable=False),
        sa.Column("frame_index", sa.Integer(), nullable=False),
        sa.Column("timestamp_ms", sa.Integer(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("class_name", sa.String(length=80), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("bbox_x1", sa.Float(), nullable=False),
        sa.Column("bbox_y1", sa.Float(), nullable=False),
        sa.Column("bbox_x2", sa.Float(), nullable=False),
        sa.Column("bbox_y2", sa.Float(), nullable=False),
        sa.Column("frame_width", sa.Integer(), nullable=False),
        sa.Column("frame_height", sa.Integer(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name=op.f("ck_detections_confidence_range"),
        ),
        sa.CheckConstraint(
            "bbox_x2 >= bbox_x1 AND bbox_y2 >= bbox_y1",
            name=op.f("ck_detections_bbox_order_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["processing_jobs.id"],
            name=op.f("fk_detections_job_id_processing_jobs"),
        ),
        sa.ForeignKeyConstraint(
            ["media_file_id"],
            ["media_files.id"],
            name=op.f("fk_detections_media_file_id_media_files"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_detections")),
    )
    op.create_index(
        "ix_detections_job_frame",
        "detections",
        ["job_id", "frame_index"],
        unique=False,
    )
    op.create_index(
        "ix_detections_media_frame",
        "detections",
        ["media_file_id", "frame_index"],
        unique=False,
    )

    op.create_table(
        "tracks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("track_id", sa.Integer(), nullable=False),
        sa.Column("class_name", sa.String(length=80), nullable=False),
        sa.Column("first_frame_index", sa.Integer(), nullable=False),
        sa.Column("last_frame_index", sa.Integer(), nullable=False),
        sa.Column("frames_count", sa.Integer(), nullable=False),
        sa.Column("average_confidence", sa.Float(), nullable=True),
        sa.Column("max_confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("frames_count >= 0", name=op.f("ck_tracks_frames_count_nonnegative")),
        sa.CheckConstraint(
            "last_frame_index >= first_frame_index",
            name=op.f("ck_tracks_frame_range_valid"),
        ),
        sa.CheckConstraint(
            "average_confidence IS NULL OR (average_confidence >= 0 AND average_confidence <= 1)",
            name=op.f("ck_tracks_average_confidence_range"),
        ),
        sa.CheckConstraint(
            "max_confidence IS NULL OR (max_confidence >= 0 AND max_confidence <= 1)",
            name=op.f("ck_tracks_max_confidence_range"),
        ),
        sa.ForeignKeyConstraint(
            ["job_id"],
            ["processing_jobs.id"],
            name=op.f("fk_tracks_job_id_processing_jobs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tracks")),
        sa.UniqueConstraint("job_id", "track_id", name="uq_tracks_job_track_id"),
    )
    op.create_index("ix_tracks_job_track", "tracks", ["job_id", "track_id"], unique=False)

    op.create_table(
        "experiment_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("experiment_run_id", sa.Uuid(), nullable=False),
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("metric_unit", sa.String(length=80), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["experiment_run_id"],
            ["experiment_runs.id"],
            name=op.f("fk_experiment_metrics_experiment_run_id_experiment_runs"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_experiment_metrics")),
    )
    op.create_index(
        "ix_experiment_metrics_run",
        "experiment_metrics",
        ["experiment_run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_experiment_metrics_run", table_name="experiment_metrics")
    op.drop_table("experiment_metrics")
    op.drop_index("ix_tracks_job_track", table_name="tracks")
    op.drop_table("tracks")
    op.drop_index("ix_detections_media_frame", table_name="detections")
    op.drop_index("ix_detections_job_frame", table_name="detections")
    op.drop_table("detections")
    op.drop_index("ix_experiment_runs_type_created_at", table_name="experiment_runs")
    op.drop_table("experiment_runs")
    op.drop_index("ix_processing_jobs_media_created_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_user_created_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_status_created_at", table_name="processing_jobs")
    op.drop_table("processing_jobs")
    op.drop_index("uq_model_versions_active_true", table_name="model_versions")
    op.drop_table("model_versions")
    op.drop_index("ix_media_files_user_created_at", table_name="media_files")
    op.drop_table("media_files")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
