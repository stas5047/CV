# Phase 18 Research Contract

## Current phase

- Confirmed: `docs/phase.md` sets current phase to `Phase 18 - Video processing and tracking pipeline`.
- Direction: CV Worker / Video Processing.
- Goal: implement end-to-end video job processing with progress updates and tracking.
- Risk level: assumption `HIGH`; user prompt left risk as placeholder, and phase touches video decode/encode, YOLO runtime, tracking, DB writes, exports, and worker queue dispatch.

## Docs consulted

Initial required docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase 18 relevant docs from `docs/phase.md`:

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

Relevant context artifacts:

- `.context/status.md` - empty.
- `.context/review-plan-resolution.md` - empty.
- `.context/review-plan-claude.md` - empty.

## Confirmed repository facts

- Git checkout is dirty before this planning work.
- `git status --short` showed existing modifications in `.context/*` files and `docs/phase.md`.
- Existing top-level areas include `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `scripts/`, Compose files, `.env.example`, and `Makefile`.
- `frontend/` remains placeholder-only per `docs/index.md` and current file list.
- `cv/pyproject.toml` already includes `opencv-python-headless`, `numpy`, `pandas`, `torch`, `ultralytics`, SQLAlchemy, psycopg, Pydantic, pytest, and Ruff.
- Backend schema already includes `detections.track_id`, `tracks`, processing job progress/heartbeat/lock fields, result paths, CSV path, JSON path, and summary JSON.
- Backend job creation accepts video jobs with `tracker_type` values `bytetrack` and `botsort`; image jobs reject client-provided tracker type.
- Backend result APIs already expose detections, tracks, result metadata, and safe downloads without exposing internal paths.
- CV worker currently has no committed video processing module.
- `cv/tests/conftest.py` is not present.

## Existing implementation state

- `cv/aerovision_worker/queue.py` claims only queued image jobs because `_select_next_queued_job_id` filters `mf.media_type = 'image'`.
- `cv/tests/test_queue.py` has an explicit test that video jobs remain queued for a later phase; Phase 18 should replace that expectation.
- `cv/aerovision_worker/main.py` always dispatches claimed jobs to `process_image_job`; no media-type dispatcher exists.
- `cv/aerovision_worker/image_processing.py` implements image source validation, OpenCV decode, YOLO inference, original pixel bbox storage, annotated image output, CSV export, JSON export, no-detection success, safe failure, and job completion.
- `cv/aerovision_worker/image_processing.py` is about 552 lines, above the AGENTS review threshold; adding video code there would increase mixed responsibility risk.
- `cv/aerovision_worker/model_runtime.py` resolves job model, active DB model, then `ACTIVE_MODEL_ID`, caches loaded models by model ID and device, and hides absolute model paths in errors/logs.
- `cv/aerovision_worker/storage_paths.py` validates relative paths and safe joins under storage root.
- `cv/aerovision_worker/settings.py` exposes configured heartbeat frame/time intervals needed by Phase 18.
- Existing worker tests use small SQLite schemas and runtime-generated temp files. PostgreSQL queue tests exist behind `pytest -m postgres`.
- Current worker index says video inference, tracking, and track summaries are not implemented yet.

## Unknowns and assumptions

Confirmed unknowns:

- No real YOLO26 weights or video fixtures are committed, and large model/media artifacts must not be committed.
- Docs do not prescribe internal Python module names for video processing or tracking helpers.
- Docs do not require exact video codec beyond "preferably MP4" for annotated output.
- Docs say BoT-SORT is supported when runtime support is available; they do not require silent fallback when unavailable.

Implementation assumptions:

- Use runtime-generated tiny video fixtures and fake model/tracker outputs in tests.
- Use OpenCV `VideoCapture` for decode and `VideoWriter` for annotated MP4 output when possible.
- Use Ultralytics tracking support for ByteTrack/BoT-SORT through the loaded model when available, while tests may use fakes with the same minimal interface.
- If the requested tracker cannot run, mark the job failed with a safe, non-path-leaking error instead of silently using a different tracker.
- Keep frame stride at the already stored internal value, default `1`; do not expose new frontend/API behavior.

## Files likely relevant for implementation

Existing files to modify:

- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/image_processing.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_queue_postgres.py`
- `cv/tests/test_startup.py`
- `cv/tests/test_image_processing.py`
- `cv/pyproject.toml`
- `cv/index.md`

Likely new implementation-owned files:

- `cv/aerovision_worker/video_processing.py`
- `cv/tests/test_video_processing.py`

Files to inspect only unless tests show integration drift:

- `backend/app/db/models.py`
- `backend/app/services/jobs.py`
- `backend/app/services/results.py`
- `backend/app/schemas/jobs.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_api_contract.py`

## Conflicts

- No `WARNING: CONFLICT` found between Phase 18 docs and current code. Current code is incomplete for Phase 18, not conflicting with the docs.
