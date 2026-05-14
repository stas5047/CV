# Phase 23 Research

## Current Phase

- Phase: `Phase 23 - Backend-worker end-to-end integration smoke`
- Direction: Backend / CV Worker / QA
- Goal from `docs/phase.md`: verify backend-created jobs are processed by worker and returned through API.
- User-provided risk level: not specified; assume high integration risk because phase spans backend API, database queue, shared storage, worker processing, downloads, ownership, and model artifact availability.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase relevant docs only:
  - `docs/ARCHITECTURE.md`
  - `docs/API.md`
  - `docs/CV_PIPELINE.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/TESTING_QA.md`

## Confirmed Repository Facts

- Git checkout has modified `.context/*` files and `docs/phase.md` before this planning work.
- `docker compose --env-file .env.example config` passes.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- Backend and CV worker both mount `./storage` to `/app/storage`.
- `.env.example` uses safe placeholder secrets and CPU worker mode.
- `.gitignore` excludes generated storage content and large model/video artifacts.
- Backend project exists under `backend/` with FastAPI app, API routes, SQLAlchemy models, Alembic migration, auth, media, jobs/results/downloads, models, admin, experiments, and tests.
- CV worker project exists under `cv/` with settings, DB helpers, queue claiming, stale recovery, model runtime, image processing, video processing, exports, and tests.
- Frontend remains placeholder Dockerfile only and is not touched by this phase.
- `cv/pyproject.toml` has a `postgres` pytest marker for worker queue integration tests.
- No `cv/tests/conftest.py` exists.

## Existing Implementation State

Confirmed from code:

- Backend job creation stores queued jobs with resolved `model_version_id`, defaults for confidence, IoU, tracker, image size, and internal `frame_stride = 1`.
- Backend result endpoints expose:
  - `GET /api/jobs/{job_id}`
  - `GET /api/jobs/{job_id}/summary`
  - `GET /api/jobs/{job_id}/detections`
  - `GET /api/jobs/{job_id}/tracks`
  - `GET /api/jobs/{job_id}/result`
  - `GET /api/jobs/{job_id}/download/media`
  - `GET /api/jobs/{job_id}/download/csv`
  - `GET /api/jobs/{job_id}/download/json`
- Backend download service requires ownership/admin visibility and requires result files under `results/{job_id}/`.
- Worker `run_poll_iteration()` runs stale recovery, claims one queued job, loads model, and dispatches image or video processor.
- Worker queue claim uses `FOR UPDATE SKIP LOCKED` only for PostgreSQL dialect and does not hold transaction open during processing.
- Worker image processing writes annotated image, CSV, JSON, detection rows, summary, relative result paths, and completed status.
- Worker video processing writes annotated MP4, CSV, JSON, detection rows, track summaries, progress/heartbeat, summary, relative result paths, and completed status.
- Worker missing model load path marks claimed job failed with safe error.
- Existing backend and worker unit tests cover pieces independently; phase lacks a documented backend API -> worker -> backend API integration smoke.

## WARNING: CONFLICT

- `docs/index.md` says current CV worker state does not yet contain queue claiming, inference, tracking, exports, or result writes.
- `README.md` says CV model loading, worker queue polling/claiming, inference, tracking, and exports are not available yet.
- `cv/index.md` and files under `cv/aerovision_worker/` show queue claiming, model runtime, image/video processing, tracking/export behavior, and tests exist.
- Planning assumption: trust code and `cv/index.md` for implementation state, but record this documentation-state conflict in design/plan. Do not edit product docs in this phase.

## Unknowns And Assumptions

Confirmed unknowns:

- User did not replace `<PHASE NUMBER AND TITLE>` or `<LOW | MEDIUM | HIGH>` placeholders.
- No valid local YOLO model artifact is confirmed under `storage/models/`.
- Full Docker E2E success with real inference depends on valid model weights and may be blocked if weights are missing.
- Video fixture feasibility depends on OpenCV codec support in local/container environment.
- Whether phase implementation should add a PowerShell smoke script, pytest integration test, or both is not yet specified by docs.

Assumptions for implementation:

- Phase contract should prefer deterministic test/smoke coverage over product changes.
- Synthetic image/video fixtures are acceptable for tests if they use documented upload formats.
- Fake model objects may be used in automated tests to make backend-worker API integration deterministic without committing weights.
- Real Docker/manual smoke should require an external valid model artifact and must document blocker if absent.
- No frontend work belongs in Phase 23.

## Files Likely Relevant For Implementation

- `docs/phase.md`
- `docker-compose.yml`
- `.env.example`
- `Makefile`
- `scripts/bootstrap-storage.ps1`
- `backend/app/api/media.py`
- `backend/app/api/jobs.py`
- `backend/app/services/media.py`
- `backend/app/services/jobs.py`
- `backend/app/services/results.py`
- `backend/app/db/models.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_api_contract.py`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/image_processing.py`
- `cv/aerovision_worker/video_processing.py`
- `cv/tests/test_startup.py`
- `cv/tests/test_queue_postgres.py`
- `cv/tests/test_image_processing.py`
- `cv/tests/test_video_processing.py`
