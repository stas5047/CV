# DATA_MODEL.md

## Purpose

This document defines the database model for the Drone Computer Vision Subsystem.

This document is canonical for:

- required PostgreSQL tables;
- required fields;
- relationships;
- constraints;
- indexes;
- soft deletion rules;
- path field rules;
- derived value rules.

This document is not canonical for route definitions, UI layout, upload validation, worker implementation, or training procedure.

## Database Principles

PostgreSQL stores structured data and metadata only.

PostgreSQL must not store:

- uploaded image/video binary data;
- annotated result media;
- CSV files;
- JSON export files;
- model weights;
- datasets;
- generated report images;
- large training artifacts.

All binary and generated files must be stored in filesystem storage volumes. Database fields that reference those files must store relative paths only.

UUID primary keys are preferred for public-facing IDs and storage-path compatibility.

## Required Tables

The database must include at least these tables:

1. `users`
2. `media_files`
3. `processing_jobs`
4. `detections`
5. `tracks`
6. `model_versions`
7. `experiment_runs`
8. `experiment_metrics`

Additional tables may be added only when they support the same architecture and do not change the project scope.

## Entity Overview

| Table | Purpose |
|---|---|
| `users` | Authenticated user and admin accounts. |
| `media_files` | Metadata for uploaded images and videos. |
| `processing_jobs` | Queue items, processing status, parameters, summaries, and result paths. |
| `detections` | One row per detected object. |
| `tracks` | Per-job video track summaries. |
| `model_versions` | Registered YOLO model versions and active model state. |
| `experiment_runs` | Imported experiment runs and their metadata. |
| `experiment_metrics` | Metric values attached to experiment runs. |

## `users`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `email` | Unique login email. |
| `password_hash` | Secure password hash, never plain text. |
| `role` | `user` or `admin`. |
| `is_active` | Allows disabling an account without deleting it. |
| `created_at` | Creation timestamp. |
| `updated_at` | Last update timestamp. |

Rules:

- `email` must be unique.
- `role` must be either `user` or `admin`.
- Public registration creates only `user` accounts.
- Admin accounts are created through seed/setup flow, not public registration.

## `media_files`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `user_id` | Owner user. |
| `original_filename` | Sanitized display reference to the original filename. |
| `stored_path` | Relative path to the uploaded file under `STORAGE_ROOT`. |
| `media_type` | `image` or `video`. |
| `mime_type` | Detected or validated MIME type. |
| `file_size_bytes` | Uploaded file size. |
| `width` | Media width in pixels when known. |
| `height` | Media height in pixels when known. |
| `frame_count` | `1` for images; video frame count for videos. |
| `fps` | `null` for images; FPS for videos when known. |
| `duration_seconds` | `null` for images; duration for videos when known. |
| `deleted_at` | Soft deletion timestamp. |
| `created_at` | Creation timestamp. |

Rules:

- `media_type` must be `image` or `video`.
- Image media must have `frame_count = 1`.
- Image media must have `fps = null`.
- Image media must have `duration_seconds = null`.
- Soft-deleted media must be hidden from normal user lists.
- Soft-deleted media may remain available for referential integrity and admin audit.
- Physical file deletion may happen only through safe admin storage cleanup rules.

## `processing_jobs`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `user_id` | Job owner. |
| `media_file_id` | Uploaded media being processed. |
| `model_version_id` | Selected model version, when explicitly selected or resolved. |
| `status` | `queued`, `processing`, `completed`, `failed`, or `cancelled`. |
| `input_params_json` | Confidence, IoU, image size, tracker type, frame stride. |
| `summary_json` | Processing summary metrics. |
| `result_media_path` | Relative path to annotated image/video, when available. |
| `csv_path` | Relative path to detection CSV export, when available. |
| `json_path` | Relative path to detection JSON export, when available. |
| `error_message` | Stored failure message for failed jobs. |
| `progress_percent` | Numeric value from 0 to 100. |
| `last_heartbeat_at` | Worker progress/heartbeat timestamp. |
| `locked_by` | Worker instance identifier. |
| `locked_at` | Timestamp when worker claimed the job. |
| `retry_count` | Stale-recovery retry counter. |
| `started_at` | Processing start timestamp. |
| `completed_at` | Processing completion timestamp. |
| `deleted_at` | Soft deletion timestamp. |
| `created_at` | Creation timestamp. |
| `updated_at` | Last update timestamp. |

`input_params_json` should contain at least:

| Key | Default |
|---|---|
| `confidence_threshold` | `0.25` |
| `iou_threshold` | `0.45` |
| `image_size` | `640` |
| `tracker_type` | `bytetrack` |
| `frame_stride` | `1` |

Rules:

- `progress_percent` must remain between 0 and 100.
- `frame_stride` exists as an internal parameter but must not be exposed in the standard UI.
- `last_heartbeat_at`, `locked_by`, `locked_at`, and `retry_count` are required for queue reliability.
- `deleted_at` is soft deletion only and must not physically remove result files.
- Jobs in `processing` state should not be physically interrupted in the MVP unless explicit cancellation is later implemented.
- No-detection cases must complete successfully with `status = completed`.

## `detections`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `job_id` | Processing job that produced the detection. |
| `media_file_id` | Media file associated with the detection. |
| `frame_index` | `0` for images; video frame index for videos. |
| `timestamp_ms` | `0` for images; timestamp in milliseconds for video detections. |
| `class_id` | Numeric detector class ID. |
| `class_name` | Must be `drone` for the primary task. |
| `confidence` | Detection confidence score. |
| `bbox_x1` | Top-left x coordinate in original media pixels. |
| `bbox_y1` | Top-left y coordinate in original media pixels. |
| `bbox_x2` | Bottom-right x coordinate in original media pixels. |
| `bbox_y2` | Bottom-right y coordinate in original media pixels. |
| `frame_width` | Original frame/media width. |
| `frame_height` | Original frame/media height. |
| `track_id` | Tracker ID when available; otherwise `null`. |
| `created_at` | Creation timestamp. |

Rules:

- Bounding boxes must be stored in original-resolution pixel coordinates.
- Image detections must have `frame_index = 0` and `timestamp_ms = 0`.
- Image detections must have `track_id = null`.
- Video detections must include `track_id` when the tracker provides it.
- `track_id` may be `null` for video frames when the tracker does not associate an ID.
- Derived center-size values are calculated from stored corner coordinates.

## `tracks`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `job_id` | Processing job. |
| `track_id` | Tracker-provided track identifier. |
| `class_name` | Expected to be `drone`. |
| `first_frame_index` | First frame where this track appears. |
| `last_frame_index` | Last frame where this track appears. |
| `frames_count` | Number of frames associated with this track. |
| `average_confidence` | Average confidence over detections in the track. |
| `max_confidence` | Maximum confidence over detections in the track. |
| `created_at` | Creation timestamp. |

Rules:

- `tracks` summarizes video tracking output.
- `tracks` must not be used for physical trajectory planning.
- The table is an analysis/visualization summary only.
- A unique constraint must exist on `(job_id, track_id)`.

## `model_versions`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `name` | Human-readable model version name. |
| `model_family` | `YOLO26` or documented fallback `YOLO11`. |
| `variant` | Model size/variant, such as `n` or `s`. |
| `weights_path` | Relative path to weights under model storage. |
| `dataset_name` | Dataset used for training/evaluation. |
| `dataset_split_description` | Human-readable split description. |
| `metrics_json` | Stored key metrics or imported metric summary. |
| `is_active` | Whether this is the active default model. |
| `created_by_user_id` | Admin user who registered the version, if applicable. |
| `created_at` | Creation timestamp. |
| `updated_at` | Last update timestamp. |

Rules:

- Only one model version may be active by default at a time.
- The main model after training should be a fine-tuned YOLO26s model, unless documented fallback is used.
- YOLO11 fallback must be represented accurately through `model_family`.
- First implementation should register existing relative paths under `STORAGE_ROOT/models`.
- Direct upload of large `.pt` files through the web UI is optional and not required.

## `experiment_runs`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `name` | Experiment name. |
| `experiment_type` | Required experiment category. |
| `description` | Human-readable description. |
| `model_version_id` | Related model version when applicable. |
| `dataset_name` | Dataset used for the experiment. |
| `config_json` | Experiment configuration and parameters. |
| `artifacts_path` | Relative path to report artifacts. |
| `is_published` | Whether regular users can see the experiment. |
| `created_by_user_id` | Admin user who imported the experiment, if applicable. |
| `created_at` | Creation timestamp. |

Required experiment types:

| Type | Meaning |
|---|---|
| `model_comparison` | YOLO26n vs YOLO26s, or YOLO11 fallback equivalents. |
| `threshold_analysis` | Confidence threshold comparison. |
| `tracker_comparison` | ByteTrack vs BoT-SORT behavior comparison. |
| `false_positive_analysis` | Bird-vs-drone false-positive analysis. |

Rules:

- Regular users may view only published experiment runs.
- Admins may view all imported experiment runs.
- Training must not be launched from the web UI.

## `experiment_metrics`

Required fields:

| Field | Notes |
|---|---|
| `id` | Primary key. |
| `experiment_run_id` | Parent experiment run. |
| `metric_name` | Metric name. |
| `metric_value` | Numeric value; may be `null` for incomplete imports. |
| `metric_unit` | Unit, when applicable. |
| `metadata_json` | Additional metric metadata. |
| `created_at` | Creation timestamp. |

Rules:

- `metric_value` may be `null`.
- Frontend must not display raw `null` values.
- Missing metrics must produce a Ukrainian-language empty state.

## Relationships

Required relationships:

| Relationship | Rule |
|---|---|
| `media_files.user_id -> users.id` | Each uploaded media file belongs to a user. |
| `processing_jobs.user_id -> users.id` | Each processing job belongs to a user. |
| `processing_jobs.media_file_id -> media_files.id` | Each job processes one media file. |
| `processing_jobs.model_version_id -> model_versions.id` | Each job may reference the selected model. |
| `detections.job_id -> processing_jobs.id` | Detections belong to a job. |
| `detections.media_file_id -> media_files.id` | Detections also reference media for filtering. |
| `tracks.job_id -> processing_jobs.id` | Track summaries belong to a job. |
| `experiment_runs.model_version_id -> model_versions.id` | Experiments may reference a model version. |
| `experiment_metrics.experiment_run_id -> experiment_runs.id` | Metrics belong to an experiment run. |

## Required Constraints

The database must enforce:

- unique `users.email`;
- valid `users.role` values: `user`, `admin`;
- valid `media_files.media_type` values: `image`, `video`;
- valid `processing_jobs.status` values: `queued`, `processing`, `completed`, `failed`, `cancelled`;
- valid `experiment_runs.experiment_type` values;
- unique `(job_id, track_id)` in `tracks`;
- only one active `model_versions` row at a time;
- foreign-key integrity for all required relationships.

## Required Indexes

Required indexes:

| Index | Purpose |
|---|---|
| `processing_jobs(status, created_at)` | Efficient queue polling. |
| `processing_jobs(user_id, created_at)` | User job history. |
| `processing_jobs(media_file_id, created_at)` | Jobs for a media file. |
| `media_files(user_id, created_at)` | User media list. |
| `detections(job_id, frame_index)` | Job detection table and export. |
| `detections(media_file_id, frame_index)` | Media-level detection filtering. |
| `tracks(job_id, track_id)` | Track summary lookup. |
| `experiment_runs(experiment_type, created_at)` | Experiment page filtering. |
| `experiment_metrics(experiment_run_id)` | Metrics lookup by experiment. |

## Soft Deletion

Soft deletion is required for:

- `media_files`;
- `processing_jobs`.

Soft-deleted records:

- are hidden from normal user lists;
- remain available for referential integrity;
- may remain visible to admins for audit/history;
- do not immediately remove physical files.

Physical file deletion may happen only through safe admin storage cleanup and must not remove active model weights, recent user results, or files still referenced by non-deleted records.

## Path Field Rules

The following fields must store relative paths only:

| Table | Field |
|---|---|
| `media_files` | `stored_path` |
| `processing_jobs` | `result_media_path` |
| `processing_jobs` | `csv_path` |
| `processing_jobs` | `json_path` |
| `model_versions` | `weights_path` |
| `experiment_runs` | `artifacts_path` |

Relative paths are interpreted under `STORAGE_ROOT` or a documented sub-root such as `MODELS_ROOT`.

Absolute host paths and absolute container paths must not be stored in the database.

## Derived Values

The database stores bounding box corner coordinates:

- `bbox_x1`;
- `bbox_y1`;
- `bbox_x2`;
- `bbox_y2`.

The API and exports must include derived center-size values:

- `center_x`;
- `center_y`;
- `bbox_width`;
- `bbox_height`.

These derived values may be calculated in API/export logic instead of stored as separate database columns.

Summary metrics may be stored in `processing_jobs.summary_json`, while detection-level records remain normalized in `detections`.

## No-Detection Data Rules

No-detection cases are successful processing results.

For no-detection jobs:

- job status must be `completed`;
- `detections` may have zero rows for the job;
- `tracks` may have zero rows for the job;
- summary should record zero detections and zero frames with detections;
- average and maximum confidence should be `null`;
- CSV export must still exist with headers only;
- JSON export must contain an empty `detections` array.

## Model Selection Data Rules

Model selection priority is defined in `CV_PIPELINE.md`, but the data model must support it through:

- `processing_jobs.model_version_id` for job-specific model selection;
- `model_versions.is_active` for active default selection;
- environment fallback handled outside the data model when no active model exists.

`ACTIVE_MODEL_ID` must not override a job-specific model or the active model selected in the database.
