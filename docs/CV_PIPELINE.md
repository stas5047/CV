# CV_PIPELINE.md

## Purpose

This document defines the runtime computer vision processing pipeline for the Drone Computer Vision Subsystem.

This document is canonical for:

- runtime image processing;
- runtime video processing;
- model family and fallback behavior at inference time;
- model selection priority;
- tracking behavior;
- detection output format;
- no-detection handling;
- export generation from the worker perspective;
- CV runtime metrics;
- CV worker error handling.

This document is not canonical for training procedure, dataset splitting, experiment artifacts, upload validation, API route definitions, or UI layout. Training and experiment workflows are defined in `TRAINING_EXPERIMENTS.md`. Upload validation is defined in `AUTH_SECURITY.md`.

## CV Scope

The CV pipeline performs image-space object detection and video tracking only.

Allowed CV outputs:

- bounding boxes;
- confidence scores;
- class labels;
- frame indices;
- timestamps;
- image-space center points;
- track IDs;
- FPS and latency measurements;
- processing summaries.

The CV pipeline must not produce:

- physical interception calculations;
- trajectory planning;
- real-world coordinate conversion;
- navigation commands;
- hardware-control commands;
- targeting, aiming, payload, or engagement instructions.

All coordinates remain image-space pixel coordinates.

## Input Assumptions

The CV worker assumes the backend has already validated:

- file extension;
- MIME type;
- upload size;
- filename safety;
- generated internal path;
- user ownership;
- processing parameters.

The worker must still handle corrupted media, unreadable files, missing files, and decode failures as processing errors.

## Supported Runtime Inputs

Supported input categories:

| Media type | Required formats |
|---|---|
| Image | `.jpg`, `.jpeg`, `.png`, `.webp` |
| Video | `.mp4`, `.avi`, `.mov`, `.mkv` |

The MVP does not support webcam, RTSP, or live camera streams.

## Detection Task

The runtime detection task is single-class object detection.

Required class:

- `drone`

Birds are not a second detection class. Bird images may be used only for false-positive analysis in experiments.

## Model Family

Primary model family:

- Ultralytics YOLO26.

Runtime main model after final training:

- fine-tuned YOLO26s.

Baseline/comparison model:

- fine-tuned YOLO26n.

## YOLO11 Fallback Policy

YOLO11 is a documented fallback model family, not an alternative primary plan.

Fallback may be used only when YOLO26 weights or package support are unavailable in the implementation environment.

When fallback is required, the issue must be reported and documented before switching.

Fallback equivalents:

| Primary | Fallback |
|---|---|
| YOLO26n | YOLO11n |
| YOLO26s | YOLO11s |

Any fallback must be recorded in:

- model metadata;
- experiment metadata;
- UI model registry through `model_versions.model_family`.

The application must reflect the actual model family used.

## Model Selection Priority

Runtime model selection must follow this priority:

1. Use `processing_jobs.model_version_id` if the job was created with a specific model version.
2. If the job has no explicit model version, use the active model from `model_versions` where `is_active = true`.
3. Use `ACTIVE_MODEL_ID` only as an initial/default fallback when the database has no active model yet.

`ACTIVE_MODEL_ID` must not override:

- a job-specific model selection;
- the active model selected in the database.

The backend is responsible for resolving and storing the intended model version when a job is created. The worker must process the job using the resolved model version.

## Runtime Defaults

Default processing parameters:

| Parameter | Default |
|---|---|
| Model | Active main fine-tuned model. |
| Confidence threshold | `0.25` |
| IoU threshold | `0.45` |
| Image size | `640` |
| Tracker | ByteTrack |
| Frame stride | `1` |

User-facing configurable parameters:

- model version;
- confidence threshold;
- IoU threshold;
- tracker type for video.

`frame_stride` is an internal advanced parameter and must not appear in the standard user UI.

## Device Selection

The worker selects its runtime device through `CV_DEVICE`.

Allowed values:

| Value | Behavior |
|---|---|
| `auto` | Use CUDA when available; otherwise CPU. |
| `cpu` | Force CPU. |
| `cuda` | Force CUDA. |

The worker must log the selected device on startup.

CPU inference must work for images and short videos. GPU is recommended for longer videos and demonstrations, but the system must not require GPU for base operation.

## Model Loading and Caching

The worker should:

- load the selected model only when needed;
- cache the active model in memory when practical;
- avoid loading multiple heavy models unnecessarily;
- reload or switch models when a job requires a different model version;
- fail safely when the selected weights file is missing.

Model loading events must be logged.

## Image Processing Flow

Image job flow:

1. Worker reads the uploaded image from shared storage.
2. Worker loads the resolved model version.
3. Worker runs YOLO inference on the image.
4. Worker converts detections to original-resolution pixel coordinates.
5. Worker writes annotated image output.
6. Worker creates detection rows.
7. Worker creates CSV and JSON exports.
8. Worker writes summary metrics.
9. Worker marks the job as `completed` or `failed`.

Image detections must have:

- `frame_index = 0`;
- `timestamp_ms = 0`;
- `track_id = null`.

## Video Processing Flow

Video job flow:

1. Worker reads the uploaded video from shared storage.
2. Worker reads media metadata such as frame count, FPS, width, and height when available.
3. Worker loads the resolved model version.
4. Worker processes video frames in order.
5. Worker runs YOLO detection frame by frame.
6. Worker applies tracking with ByteTrack by default.
7. Worker writes annotated frames to output video.
8. Worker writes progress and heartbeat updates during processing.
9. Worker stores detection rows and track summaries.
10. Worker creates CSV and JSON exports.
11. Worker writes summary metrics.
12. Worker marks the job as `completed` or `failed`.

For video jobs, the annotated result should be saved as MP4 whenever possible, regardless of original input extension.

If browser preview is not supported for the generated video, the frontend must still provide a download button and show a Ukrainian-language notice.

## Tracking Rules

Default tracker:

- ByteTrack.

ByteTrack is the default tracker for video jobs.

BoT-SORT is available as an alternative user-selectable tracker for video jobs when supported by the runtime environment. Experiment 3 compares ByteTrack and BoT-SORT as a tracker behavior comparison, not as an absolute tracking accuracy benchmark.

Tracking output rules:

- video detections include `track_id` when the tracker provides it;
- image detections always have `track_id = null`;
- video detections may have `track_id = null` when the tracker does not associate an ID;
- track IDs are for visualization and analysis only;
- track IDs must not be used for control, targeting, navigation, or interception calculations.

## Track Summary Rules

For video jobs, the worker should create track summaries with:

- job ID;
- track ID;
- class name;
- first frame index;
- last frame index;
- frames count;
- average confidence;
- maximum confidence.

The `tracks` table summarizes video tracking output only. It must not represent physical trajectories.

## Detection Output Format

Each detection must include:

- job ID;
- media ID;
- frame index;
- timestamp in milliseconds;
- class ID;
- class name;
- confidence;
- bounding box corner coordinates;
- frame width;
- frame height;
- track ID when available;
- model version;
- tracker type.

Primary stored bounding box format:

- `x1`, `y1`, `x2`, `y2` in original media pixel coordinates.

Derived export/API values:

- `center_x`;
- `center_y`;
- `bbox_width`;
- `bbox_height`.

Normalized YOLO-style coordinates may be included in exports when useful, but original-resolution pixel coordinates remain primary.

## No-Detection Handling

No detections found is a successful processing result, not a failure.

For no-detection jobs:

- job status must be `completed`;
- `total_detections = 0`;
- `frames_with_detections = 0`;
- `average_confidence = null`;
- `maximum_confidence = null`;
- CSV export must exist with headers only;
- JSON export must contain an empty `detections` array;
- UI must show a Ukrainian-language empty state.

The worker must still create annotated output media when possible, even when there are no detections.

## Processing Summary Metrics

Each completed processing job must calculate summary metrics:

| Metric | Notes |
|---|---|
| Media type | Image or video. |
| Original filename | Sanitized display filename. |
| File size | Source media file size. |
| Processing status | Final job status. |
| Total frames processed | `1` for image jobs. |
| Total detections | Count of detection rows. |
| Frames with detections | Video frame count with at least one detection; `0` or `1` for images. |
| Unique track IDs | Video jobs only; `0` for images/no tracks. |
| Average confidence | `null` when no detections exist. |
| Maximum confidence | `null` when no detections exist. |
| Average FPS | End-to-end video processing average when applicable. |
| Inference latency per frame | Average model inference latency per processed frame in milliseconds, when available. |
| Total processing time | Worker processing duration. |
| Model size MB | File size of the selected model weights, sourced from the model card or measured from the weights file when available. |
| Selected model version | Resolved model version. |
| Confidence threshold | Actual threshold used. |
| IoU threshold | Actual threshold used. |
| Tracker type | ByteTrack by default for video. |

The worker should store runtime performance values such as inference latency per frame and model size in `processing_jobs.summary_json` when available so the frontend can display required per-job performance metrics.

## Export Generation

The worker is responsible for generating:

- CSV export;
- JSON export;
- job summary file when implemented as stored artifact;
- annotated media output.

CSV export must contain one row per detection. For no-detection jobs, it must contain headers only.

JSON export must include:

- job metadata;
- media metadata;
- model metadata;
- parameters;
- summary;
- detections array;
- tracks array.

Exports must contain only CV data and must obey the external boundary defined in `API.md`.

## CV Runtime Error Handling

The worker must handle:

- missing uploaded file;
- corrupted image;
- corrupted video;
- unsupported decode result;
- model file missing;
- CUDA unavailable when `CV_DEVICE=auto` by falling back to CPU;
- CUDA unavailable when `CV_DEVICE=cuda` by failing clearly;
- failed output media creation;
- failed CSV or JSON export creation;
- database write failures;
- worker crash with stale job recovery handled by architecture rules.

Failed jobs must store a clear `error_message`.

Detailed stack traces may be logged in worker logs but must not be exposed through unsafe API responses.

## Progress and Heartbeat

For video jobs, the worker must update progress and heartbeat during processing.

Default update rule:

- every 30 frames or every 2 seconds, whichever comes first.

For image jobs, progress may update to 100 when processing completes.

Worker queue reliability is defined in `ARCHITECTURE.md`.

## Runtime Integration with Data Model

The worker writes:

- processing job status and progress;
- detection rows;
- track summaries;
- summary metrics;
- result media relative path;
- CSV relative path;
- JSON relative path;
- error message for failed jobs.

The worker must store relative paths only and must not write absolute host or container paths into the database.

## Runtime Invariants

The CV pipeline must always preserve these rules:

- The task is single-class `drone` detection.
- The primary model family is YOLO26.
- YOLO11 is fallback only after documented YOLO26 unavailability.
- Model selection priority follows job-specific model, then database active model, then environment fallback.
- ByteTrack is the default tracker for video.
- Image detections have `track_id = null`.
- Bounding boxes are original-resolution pixel coordinates.
- No-detection cases complete successfully.
- CSV and JSON exports are produced for completed jobs.
- Processing outputs remain CV-only and image-space only.
- The worker does not implement trajectory, control, targeting, or hardware behavior.
