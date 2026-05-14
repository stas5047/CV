# Plan - Phase 17 Image Processing Pipeline

## Scope lock

Phase: **Phase 17 - Image processing pipeline**.

In scope:

- CV worker image-job processing.
- Image decode/read from shared storage.
- YOLO inference through existing loaded model runtime.
- Detection DB rows for image jobs.
- Annotated image output.
- CSV/JSON exports for image jobs.
- Summary metrics and final job status/progress.
- Missing/corrupted/unreadable image failure handling.
- No-detection image success handling.
- Worker tests for this behavior.

Out of scope:

- Video processing.
- ByteTrack/BoT-SORT tracking implementation.
- Frontend UI.
- Backend API contract changes.
- Database schema changes/migrations.
- Training utilities.
- New runtime service, Celery, Redis, RTSP/live camera, Flask, Streamlit.

## Ordered atomic steps

1. `@role/developer-cv-worker` Re-read `docs/CV_PIPELINE.md`, `docs/DATA_MODEL.md`, `docs/API.md`, and `docs/TESTING_QA.md` before coding.
   - Verify: implementation notes match Phase 17 only.

2. `@role/developer-cv-worker` Inspect current worker entry path in `cv/aerovision_worker/main.py`, queue helpers in `cv/aerovision_worker/queue.py`, model runtime in `cv/aerovision_worker/model_runtime.py`, and storage path helpers in `cv/aerovision_worker/storage_paths.py`.
   - Verify: current placeholder failure path and available helper contracts are understood.

3. `@role/developer-cv-worker` Add failing worker test for successful image job using a tiny image fixture and mocked model output.
   - Required assertions:
     - job becomes `completed`;
     - `progress_percent = 100`;
     - annotated image file exists;
     - CSV file exists;
     - JSON file exists;
     - result/export DB paths are relative;
     - one or more `detections` rows inserted.
   - Verify: targeted pytest fails before implementation for missing image processing behavior.

4. `@role/developer-cv-worker` Add failing worker test for image detection row invariants.
   - Required assertions:
     - `frame_index = 0`;
     - `timestamp_ms = 0`;
     - `track_id is None`;
     - `class_name = "drone"`;
     - bbox coordinates are original image pixel coordinates;
     - `frame_width` and `frame_height` match decoded image dimensions.
   - Verify: targeted pytest fails before implementation.

5. `@role/developer-cv-worker` Add failing worker test for no-detection image job.
   - Required assertions:
     - job becomes `completed`;
     - zero detection rows;
     - `summary_json.total_detections = 0`;
     - `summary_json.frames_with_detections = 0`;
     - `summary_json.average_confidence is None`;
     - `summary_json.maximum_confidence is None`;
     - CSV has headers only;
     - JSON has empty `detections`.
   - Verify: targeted pytest fails before implementation.

6. `@role/developer-cv-worker` Add failing worker tests for missing/corrupted image input and artifact creation failures.
   - Required failure cases:
     - missing source file;
     - corrupted/unreadable image;
     - annotated output media write failure;
     - CSV export write failure;
     - JSON export write failure.
   - Required assertions:
     - job becomes `failed`;
     - `error_message` is clear and safe;
     - error text does not include absolute host/container paths;
     - no partial success is reported when required completed-job artifacts cannot be created.
   - If a specific artifact failure cannot be simulated cleanly, document exact reason before implementation continues.
   - Verify: targeted pytest fails before implementation.

7. `@role/developer-cv-worker` Add failing export contract test for image CSV/JSON.
   - CSV required columns:
     - `job_id`
     - `media_id`
     - `frame_index`
     - `timestamp_ms`
     - `class_id`
     - `class_name`
     - `confidence`
     - `bbox_x1`
     - `bbox_y1`
     - `bbox_x2`
     - `bbox_y2`
     - `center_x`
     - `center_y`
     - `bbox_width`
     - `bbox_height`
     - `frame_width`
     - `frame_height`
     - `track_id`
     - `model_version`
     - `tracker_type`
   - JSON required top-level keys:
     - `job`
     - `media`
     - `model`
     - `parameters`
     - `summary`
     - `detections`
     - `tracks`
   - Verify: targeted pytest fails before implementation.

8. `@role/developer-cv-worker` Implement image-job metadata load from existing database tables.
   - Must read only needed fields from `processing_jobs`, `media_files`, and resolved model metadata.
   - Must not mark valid video/non-image jobs failed only because Phase 17 is image-only.
   - Prefer image-only queue claiming/filtering so video jobs remain queued for the later video-processing phase.
   - If existing queue shape cannot cleanly filter by image media in this phase, use explicit non-failing deferral and document it before implementation continues.
   - Verify: metadata tests pass and no schema changes are needed.

9. `@role/developer-cv-worker` Implement safe source image path resolution.
   - Use existing relative path validation/safe join behavior.
   - Missing files fail job safely.
   - Absolute paths are never read from DB or written back.
   - Verify: missing-file test passes.

10. `@role/developer-cv-worker` Implement image decode validation with `opencv-python-headless`.
    - Decode must fail safely for unreadable/corrupted image.
    - Width/height must come from decoded image or existing media metadata only when trustworthy.
    - Verify: corrupted-image test passes.

11. `@role/developer-cv-worker` Implement YOLO image inference adapter using existing `LoadedModel.model`.
    - Must pass documented confidence, IoU, and image-size parameters from `processing_jobs.input_params_json`.
    - Must keep model-selection behavior in `model_runtime.py`.
    - Tests should mock output shape so real model weights are not required.
    - Verify: mocked successful image test reaches detection conversion.

12. `@role/developer-cv-worker` Implement conversion from model output to internal detection rows.
    - Must preserve original image pixel coordinates.
    - Must clamp or validate boxes to image bounds where needed.
    - Must use `class_name = "drone"` for accepted detections.
    - Must use `frame_index = 0`, `timestamp_ms = 0`, `track_id = null`.
    - Verify: detection invariant test passes.

13. `@role/developer-cv-worker` Implement annotated image output.
    - Output path must be under `results/{job_id}/`.
    - DB path must be relative.
    - Use CV-only overlay: boxes/class/confidence only.
    - No targeting/navigation/control wording or data.
    - Verify: annotated output exists for detection and no-detection cases when decode succeeds.

14. `@role/developer-cv-worker` Implement CSV export for image jobs.
    - One row per detection.
    - Headers-only for no-detection.
    - Include derived `center_x`, `center_y`, `bbox_width`, and `bbox_height`.
    - Verify: CSV export contract tests pass.

15. `@role/developer-cv-worker` Implement JSON export for image jobs.
    - Include required top-level keys only.
    - Use empty `tracks` array for image jobs.
    - Use empty `detections` array for no-detection.
    - Do not include forbidden external output fields.
    - Do not include absolute filesystem paths.
    - Verify: JSON export contract and no-forbidden-fields tests pass.

16. `@role/developer-cv-worker` Implement summary metric calculation for image jobs.
    - Required values:
      - media type;
      - sanitized original filename;
      - source file size;
      - processing status;
      - total frames processed = `1`;
      - total detections;
      - frames with detections = `0` or `1`;
      - unique track IDs = `0`;
      - average confidence or `null`;
      - maximum confidence or `null`;
      - inference latency per frame when available;
      - total processing time;
      - model size MB when available from model card/metadata or measured weights file;
      - selected model version;
      - confidence threshold;
      - IoU threshold;
      - tracker type from params/default where stored, without creating image track IDs.
    - Verify: summary assertions pass for detection and no-detection tests.

17. `@role/developer-cv-worker` Implement DB finalization for completed image jobs.
    - Insert detection rows.
    - Store result/export relative paths.
    - Store summary JSON.
    - Set `status = completed`, `progress_percent = 100`, `completed_at`, `last_heartbeat_at`, and clear lock fields if current worker still owns job.
    - Ensure `updated_at` changes through existing DB behavior or explicit update; assert where practical.
    - Ensure job-scoped retry cleanup prevents duplicate detections/result refs on reprocessed stale jobs.
    - Verify: successful image/no-detection tests pass.

18. `@role/developer-cv-worker` Wire image processing into `run_poll_iteration`.
    - Preserve stale recovery and model-loading failure behavior.
    - Replace Phase 14 placeholder failure for image jobs.
    - Keep processing outside claim transaction.
    - Verify: existing startup test updated to expect image processor call instead of placeholder failure.

19. `@role/tester` Run targeted worker tests during implementation.
    - Command: `cd cv; python -m pytest tests/test_startup.py tests/test_model_runtime.py tests/test_queue.py`
    - Expected: `PASS`.

20. `@role/tester` Run new image-processing tests.
    - Command: `cd cv; python -m pytest tests`
    - Expected: `PASS`.

21. `@role/tester` Run lint.
    - Command: `cd cv; python -m ruff check .`
    - Expected: `PASS`.

22. `@role/tester` Run PostgreSQL queue integration only when PostgreSQL test environment is reachable.
    - Command: `cd cv; python -m pytest -m postgres`
    - Expected: `PASS` or `not available yet` with exact environment reason.

23. `@role/code-reviewer` Review changed worker files against consulted docs.
    - Check:
      - image-only scope;
      - valid video jobs are not failed because this phase is image-only;
      - no video/tracking implementation;
      - no backend/frontend/schema changes unless directly justified;
      - relative DB paths only;
      - no absolute paths in logs/errors/exports/API-facing values;
      - no secrets in logs;
      - no CV output beyond image-space data;
      - no no-detection-as-failure behavior;
      - tests cover successful, no-detection, export, and failure paths.
    - Verify: no `WARNING: CONFLICT`; otherwise stop for user decision.

24. `@role/docs-maintainer` Update component index only if implementation changes current worker state or commands.
    - Candidate: `cv/index.md`.
    - Do not modify product docs.
    - Verify: index remains a folder summary, not duplicated product spec.

25. `@role/tester` Final relevant gates for Phase 17.
    - `cd cv; python -m ruff check .` -> expected `PASS`.
    - `cd cv; python -m pytest` -> expected `PASS`.
    - `cd cv; python -m pytest -m postgres` -> expected `PASS` if PostgreSQL available, otherwise `not available yet`.

## Stop conditions

Stop and report `WARNING: CONFLICT` if implementation finds docs or existing code requiring:

- schema changes for Phase 17;
- backend API contract changes;
- video processing/tracking work;
- valid video jobs being marked failed only because Phase 17 is image-only;
- frontend UI work;
- absolute path exposure;
- no-detection image failure behavior;
- YOLO11 primary usage without documented fallback reason;
- physical targeting/navigation/control/geospatial output.
