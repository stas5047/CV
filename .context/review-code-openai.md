# OpenAI Code Review - Phase 18 Video Processing and Tracking Pipeline

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 18 implementation stays in CV worker scope. It adds video job claiming/dispatch, per-frame YOLO tracking with ByteTrack default and BoT-SORT selection, annotated MP4 output, detections, track summaries, CSV/JSON exports, no-detection success, and relative storage paths. Relevant CV worker gates pass.

One important gap remains: tests do not prove the documented mid-processing heartbeat/progress behavior. Current assertions would still pass if the per-frame heartbeat call were removed, because final completion overwrites progress and heartbeat.

## Critical issues

None.

## Important issues

1. Missing regression coverage for video heartbeat/progress updates during processing.
   - Evidence: `docs/phase.md:16`, `docs/CV_PIPELINE.md:217`, `docs/CV_PIPELINE.md:380`, and `docs/TESTING_QA.md:223` require progress and heartbeat updates during video processing.
   - Evidence: implementation calls `_heartbeat_if_needed(...)` inside the frame loop at `cv/aerovision_worker/video_processing.py:195`, and `_heartbeat_if_needed()` calls `update_job_heartbeat(...)` at `cv/aerovision_worker/video_processing.py:338`.
   - Evidence: `cv/tests/test_video_processing.py:290` configures `heartbeat_frames=1`, but the test only asserts final `job["progress_percent"] == 100` at `cv/tests/test_video_processing.py:305`.
   - Evidence: final completion sets `progress_percent = 100` and `last_heartbeat_at = :completed_at` at `cv/aerovision_worker/video_persistence.py:137-139`, so the current test would pass even if the frame-loop heartbeat update at `cv/aerovision_worker/video_processing.py:195` were deleted.
   - Impact: required in-progress UI/status behavior can regress without test failure.
   - Needed change: add a video test that monkeypatches `update_job_heartbeat` or otherwise captures intermediate DB updates and asserts at least one heartbeat/progress update before final completion, with a progress value below 100.

## Optional issues

1. No-detection video test does not assert annotated output media exists.
   - Evidence: `docs/CV_PIPELINE.md:306` says the worker must still create annotated output media when possible for no-detection jobs.
   - Evidence: `cv/tests/test_video_processing.py:336-362` verifies completed status, empty DB rows, and empty exports, but does not assert `result_media_path` or file existence. Positive-detection coverage does assert this at `cv/tests/test_video_processing.py:306-307`.
   - Impact: no-detection artifact regression could slip through while CSV/JSON assertions still pass.

## Quality gate assessment

- `rtk git status --short`: PASS for review input; shows Phase 18 worker/context changes plus untracked video modules/tests.
- `rtk git diff --stat`: PASS for review input; note untracked video files are not represented in that stat.
- `rtk git diff`: PASS for review input; changed tracked files reviewed. Untracked video files inspected directly.
- `cd cv; python -m ruff check .`: PASS.
- `cd cv; python -m pytest -p no:cacheprovider`: PASS, 81 passed.
- `cd cv; python -m pytest -p no:cacheprovider -m postgres`: PASS, 3 passed, 78 deselected.

## Security/privacy assessment

Applicable because Phase 18 touches shared-storage reads/writes and exports. No concrete security/privacy issue found. Source paths use relative-path validation and safe storage joins; result paths are generated under `results/{job_id}/`; exported JSON/CSV content stays within CV/image-space data; safe failure messages avoid absolute storage paths in covered cases.

## Positive findings

- Queue now claims both image and video jobs while preserving supported media filtering and PostgreSQL `FOR UPDATE SKIP LOCKED`.
- Worker dispatch keeps image and video processing separated.
- Video processing modules are split by responsibility instead of expanding the already large image module.
- Tracking uses job-scoped model calls with `persist=True`, ByteTrack default, and BoT-SORT config when selected.
- No-detection video path completes successfully with empty detections/tracks and exports.
- No backend API, frontend, database migration, training, Docker, Celery/Redis, live-camera, or out-of-scope control/navigation behavior was added.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/video_processing.py`
- `cv/aerovision_worker/video_detection.py`
- `cv/aerovision_worker/video_exports.py`
- `cv/aerovision_worker/video_io.py`
- `cv/aerovision_worker/video_persistence.py`
- `cv/aerovision_worker/video_types.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/index.md`
- `cv/tests/test_queue.py`
- `cv/tests/test_startup.py`
- `cv/tests/test_video_processing.py`
