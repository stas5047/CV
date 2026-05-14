# Phase 18 Status

## Implemented

- Updated CV worker queue claiming to include image and video jobs, with claimed media type returned for dispatch.
- Added worker dispatch so image jobs still use image processing and video jobs use the new video processor.
- Added video processing pipeline:
  - reads uploaded video through safe shared-storage relative paths;
  - validates missing/corrupt/unreadable video cases safely;
  - processes frames in order with job-scoped Ultralytics tracker persistence;
  - uses ByteTrack by default and passes BoT-SORT when selected;
  - fails safely when tracker runtime support is unavailable;
  - writes annotated MP4 output under `results/{job_id}/annotated.mp4`;
  - updates progress/heartbeat during processing;
  - stores video detection rows with frame index, timestamp, bbox, confidence, model, tracker, and nullable track IDs;
  - writes track summaries for non-null track IDs;
  - writes CSV/JSON exports including top-level `tracks`;
  - completes no-detection video jobs successfully.
- Split video implementation across focused worker modules to avoid a large mixed-responsibility file.
- Updated CV worker index for current video-processing capability.

## Code Review Final Fix

- Resolved `.context/review-code-openai.md` review items in `.context/review-code-resolution.md`.
- Accepted important fix: added regression coverage for intermediate video heartbeat/progress updates before final completion.
- Accepted optional fix: added no-detection video assertion that annotated MP4 result media is recorded and exists.
- No source behavior changes were needed; fixes are test-only.

## Validation

- `cd cv; python -m ruff check .` -> PASS
- `cd cv; python -m pytest` -> PASS (`81 passed`)
- `cd cv; python -m pytest -m postgres` -> PASS (`3 passed`)
- `cd cv; python -m pytest tests\test_video_processing.py` -> PASS (`8 passed`)
- `git diff --check` -> FAIL, unrelated existing trailing whitespace in `docs/phase.md:3`; left untouched because it is outside accepted review fixes.

## Security and Safety

- DB result paths remain relative.
- Video source/result paths use existing safe storage join/validation.
- Worker failure messages avoid absolute paths, tracebacks, tokens, secrets, and DB URLs.
- JSON exports remain limited to CV/image-space detections, model data, parameters, summaries, and track summaries.
- No backend API, frontend, DB migration, training, Docker, or product-doc changes were made.

## Remaining Risks

- Unit tests use generated tiny videos and fake tracker outputs; real YOLO/Ultralytics tracker behavior still needs runtime smoke with actual model artifacts in later integration/QA.
- OpenCV MP4 encoding depends on available codec support; implementation fails safely if writer cannot open.
