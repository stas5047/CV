# Design - Phase 17 Image Processing Pipeline

## Phase goal

Implement end-to-end CV worker processing for image jobs only.

Confirmed from docs: worker must read uploaded image from shared storage, validate decode, run YOLO inference, convert detections to original-resolution pixel coordinates, write annotated image output, store detection rows, create CSV/JSON exports, calculate summary metrics, update job result paths/progress/status, fail corrupted or missing media safely, and treat no-detection images as successful completed jobs.

## Intended behavior from docs

Confirmed behavior:

- Input is uploaded image already validated by backend, but worker must still handle missing/unreadable/corrupted/decode-failed files.
- Image detections must use:
  - `frame_index = 0`
  - `timestamp_ms = 0`
  - `track_id = null`
- Bounding boxes must be stored/exported as original-resolution image-space pixels.
- Detection task is single-class `drone`.
- Processing output must stay CV-only: boxes, confidence, class, frame/timestamp, image-space centers, model data, FPS/latency/summary metrics.
- No-detection is success, not failure.
- No-detection image jobs must have:
  - `status = completed`
  - `total_detections = 0`
  - `frames_with_detections = 0`
  - `average_confidence = null`
  - `maximum_confidence = null`
  - CSV with headers only
  - JSON with empty `detections`
- Completed jobs must store only relative paths for annotated media, CSV, and JSON.
- Completed image-job summaries must include sanitized original filename, source file size, and model size MB when available.
- Worker must not expose public API routes and must not call backend API for job loop.
- Worker must use resolved model version from existing model runtime priority.

## Architecture decisions

Confirmed architecture:

- Keep backend as authorization/download boundary.
- Keep worker coordination through PostgreSQL plus shared storage.
- Keep image processing outside claim transaction.
- Reuse existing worker settings, model runtime, queue helpers, and storage path utilities.
- Use `opencv-python-headless`/NumPy for image read, annotation, and write.
- Use pandas or stdlib CSV for CSV export; either is allowed by existing deps. Contract requires CSV columns, not library.
- Use short DB transactions for:
  - reading job/media/model metadata needed for processing;
  - inserting detection rows;
  - marking job completed/failed and storing paths/summary.
- Do not add video processing, ByteTrack behavior, track summaries, frontend UI, backend route changes, schema changes, or training utilities in this phase.
- Do not fail valid video jobs only because Phase 17 is image-only. Prefer image-only queue claiming/filtering so video jobs remain queued for the later video-processing phase.

Implementation shape:

- Replace placeholder failure path in `run_poll_iteration` with image processing for image jobs once model preflight succeeds.
- Preserve safe model-loading failure behavior.
- Add image-specific processing helper(s) with clear inputs: claimed job ID, worker ID, settings, session factory, loaded model.
- Ensure image processing only handles image media. Non-image/video jobs must use non-failing deferral behavior in this phase.
- Generate result files under `results/{job_id}/...` and store those relative paths.
- Insert detection rows linked to `job_id` and `media_file_id`.
- Clear stale prior result paths/detections only if retrying same job after stale recovery can otherwise duplicate rows. If implemented, cleanup must be job-scoped.

## Backend impact

No backend API changes planned.

Backend result APIs should begin returning actual worker-produced summaries, detections, result metadata, and downloads through existing routes.

## Frontend impact

No frontend changes planned.

Frontend remains placeholder and does not affect this phase.

## DB impact

No schema or migration changes planned.

Worker will write existing fields/tables:

- `processing_jobs.status`
- `processing_jobs.progress_percent`
- `processing_jobs.summary_json`
- `processing_jobs.result_media_path`
- `processing_jobs.csv_path`
- `processing_jobs.json_path`
- `processing_jobs.error_message`
- `processing_jobs.completed_at`
- `processing_jobs.last_heartbeat_at`
- `processing_jobs.updated_at`
- `detections`

No `tracks` rows for image jobs.

## API impact

No route or response schema changes planned.

Existing API/export contracts constrain generated CSV/JSON content:

- CSV required columns from `docs/API.md`.
- JSON top-level keys: `job`, `media`, `model`, `parameters`, `summary`, `detections`, `tracks`.
- No absolute storage paths in API responses or exports.

## Security/privacy impact

Touched surface: worker file paths, logs, exports, and DB path writes.

Requirements:

- Validate DB-stored media/model paths before filesystem access.
- Write only relative paths back to database.
- Prevent path traversal through all result/export paths.
- Do not log secrets, raw tokens, DB passwords, or absolute storage paths.
- Error messages stored on failed jobs must be clear but safe, without host/container absolute paths.
- Exports must not include forbidden targeting/navigation/control/geospatial fields.
- User-uploaded files are decoded/read only, never executed.

## Test strategy

Relevant tests only:

- Worker unit tests for successful image job:
  - decodes image;
  - uses mocked loaded model output;
  - inserts detections with frame/timestamp/track rules;
  - writes annotated image;
  - writes CSV and JSON exports;
  - stores relative result paths;
  - marks job completed with progress 100.
- Worker unit tests for no-detection image:
  - zero detection rows;
  - headers-only CSV;
  - JSON empty `detections`;
  - completed status and null confidence summary.
- Worker unit tests for failures:
  - missing source file;
  - corrupted/unreadable image;
  - annotated output write failure;
  - CSV export write failure;
  - JSON export write failure;
  - if a specific artifact failure cannot be simulated cleanly, document the reason in the test or implementation notes.
- Export tests:
  - CSV has all required columns;
  - JSON has required top-level keys and no forbidden fields.
- Regression tests:
  - existing queue/model/startup tests adjusted away from placeholder failure.

Relevant commands:

- `cd cv; python -m ruff check .`
- `cd cv; python -m pytest`
- `cd cv; python -m pytest tests/test_startup.py tests/test_model_runtime.py tests/test_queue.py`
- `cd cv; python -m pytest -m postgres` only if PostgreSQL integration env is reachable.

No frontend gates, backend full suite, or Docker full-stack gates required for this planning phase unless implementation touches those surfaces later.

## Ambiguities or conflicts

No `WARNING: CONFLICT` found among consulted docs for Phase 17.

Ambiguities:

- Exact annotated image file extension/name is not specified.
- Exact summary JSON key spelling is not fully specified.
- Exact Ultralytics result object shape is runtime-library-specific.
- Exact retry cleanup behavior for detection rows/result files is not specified.
- Exact queue-deferral mechanics for non-image jobs depend on existing `claim_next_job` shape, but valid video jobs must not be failed during Phase 17.

Resolution approach:

- Keep choices local and documented in implementation comments/tests where needed.
- Prefer existing API/backend test expectations where they already imply keys/paths.
- Avoid adding new public contract fields beyond docs.
