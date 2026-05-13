# Phase 10 Research

## Current phase

- Confirmed from `docs/phase.md`: Phase 10 - Jobs, results, detections, tracks, and safe downloads API.
- Direction: Backend.
- Goal: implement job history, job details, result metadata, detections, tracks, summary, and download endpoints.
- Risk level: not supplied by user prompt; placeholder remained unfilled. Assumption: HIGH because phase touches protected result/download APIs, ownership, soft deletion, storage path safety, and CV-only output boundaries.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase relevant docs from `docs/phase.md`:
  - `docs/API.md`
  - `docs/ARCHITECTURE.md` (consulted during planning-review resolution for concrete result artifact layout)
  - `docs/DATA_MODEL.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/CV_PIPELINE.md`
  - `docs/TESTING_QA.md`

Additional repo/context files consulted for implementation-state facts:

- `.context/status.md`
- prior `.context/research.md`, `.context/design.md`, `.context/plan.md`
- `backend/index.md`
- selected backend source and test files listed below

## Confirmed repository facts

- `git status --short` before this contract work showed `docs/phase.md` already modified.
- `.context/status.md` records Phase 9 complete: queued job creation and model selection resolution implemented.
- Backend is an implemented FastAPI app with auth, media, models, and job creation routers.
- `backend/app/api/router.py` already registers `auth`, `health`, `media`, `models`, and `jobs`.
- `backend/app/api/jobs.py` currently implements only `POST /api/jobs`.
- `backend/app/services/jobs.py` currently implements only job creation, own-media validation, parameter defaults, and model resolution.
- `backend/app/schemas/jobs.py` currently contains `JobCreateRequest` and `JobResponse`.
- `backend/tests/test_jobs_api.py` currently covers Phase 9 job creation/model-selection behavior only.
- `backend/app/db/models.py` already defines:
  - `ProcessingJob` with status, params, summary, result/export relative paths, progress, heartbeat, lock, retry, timestamps, and `deleted_at`;
  - `Detection` with bbox, confidence, frame/timestamp, media/job links, and optional `track_id`;
  - `Track` with per-job track summary fields and unique `(job_id, track_id)`;
  - `MediaFile` with owner, soft deletion, media metadata, and relative stored path;
  - `ModelVersion` with model metadata and active state.
- `backend/app/core/storage_paths.py` provides relative path validation, safe storage join, upload filename sanitization, and safe download filename handling.
- `backend/app/core/auth.py` provides active JWT user dependency.
- `backend/app/core/authorization.py` provides admin and ownership helpers.
- `backend/app/services/media.py` already shows list/detail/soft-delete patterns with user/admin visibility.
- `backend/app/services/models.py` already shows paginated list and safe not-found patterns.
- `backend/app/core/config.py` exposes `storage_root` and `active_model_id`.
- Existing backend test suite uses `pytest`, `TestClient`, SQLite test databases, and helper fixtures in individual test modules.

## Existing implementation state

Implemented before Phase 10:

- `/api/health` and `/api/health/db`.
- JWT auth, public registration, login, current-user endpoint.
- Active-account enforcement.
- Admin dependency and ownership helpers.
- Relative storage path and safe filename utilities.
- Media upload, list, detail, and soft-delete API.
- Model registry list, detail, register, and activate API.
- SQLAlchemy schema and initial Alembic migration for documented tables.
- Local/demo setup and seeded admin command.
- `POST /api/jobs` for queued job creation with validated params and model selection priority.

Not implemented yet:

- `GET /api/jobs`.
- `GET /api/jobs/{job_id}`.
- `DELETE /api/jobs/{job_id}`.
- `GET /api/jobs/{job_id}/summary`.
- `GET /api/jobs/{job_id}/detections`.
- `GET /api/jobs/{job_id}/tracks`.
- `GET /api/jobs/{job_id}/result`.
- `GET /api/jobs/{job_id}/download/media`.
- `GET /api/jobs/{job_id}/download/csv`.
- `GET /api/jobs/{job_id}/download/json`.
- Result/download schemas and service helpers.
- Job list filters and pagination.
- Download file association checks.
- Tests for ownership, downloads, missing files, no-detection completed jobs, soft deletion, and cancellation behavior.
- CV worker processing, export generation, and frontend job/result pages.

## Unknowns and assumptions

- WARNING: CONFLICT
  - `docs/index.md` says backend/frontend/CV folders contain placeholder Dockerfiles only and no product app scaffolds/routes/tests.
  - Actual repo and `backend/index.md` show implemented backend auth, media, models, schema, migrations, setup, and Phase 9 job creation.
  - Contract uses `docs/phase.md` for current phase and actual backend files for implementation-state facts.
- User prompt left `<PHASE NUMBER AND TITLE>` and `<LOW | MEDIUM | HIGH>` placeholders unfilled. Assumption: current phase comes from `docs/phase.md`; risk treated as HIGH.
- Docs do not define exact response schemas for Phase 10 endpoints. Assumption: use documented fields from `processing_jobs`, `detections`, `tracks`, media/model metadata, derived bbox values, summary JSON, and safe download URLs/references only.
- Docs do not define exact job list filter query names. Assumption: use documented filters already named in `docs/API.md`: status, media type, date, model version, owner for admins, with existing backend pagination style.
- Docs do not define exact DELETE semantics for processing jobs. Assumption: queued jobs may become `cancelled` and/or soft-deleted; processing jobs should not be physically interrupted; all normal lists hide `deleted_at`.
- Docs require file belongs to requested job before download. Phase 10 contract uses the documented `docs/ARCHITECTURE.md` artifact layout as the concrete association rule: result/download paths must be under `results/{job_id}/` for the requested job, be selected from that authorized job row, pass relative-path validation, resolve under `STORAGE_ROOT`, and exist as a file at serving time.
- Result metadata availability means the corresponding job path is present, passes the same `results/{job_id}/` association rule, resolves safely under `STORAGE_ROOT`, and the file exists on disk. Missing files should render unavailable metadata or safe 404 download errors without exposing internal paths.
- Phase 10 tests must include inactive-user rejection for at least one representative result route and one download route, because `docs/AUTH_SECURITY.md` requires inactive users be blocked from all protected result/download access.
- Docs require no-detection completed jobs to remain successful and keep CSV/JSON downloads when files exist. Assumption: zero detections/tracks returns empty lists and summary may contain null confidence values without treating job as failed.
- CV worker/export generation is not in scope; tests may create database rows and fixture files directly to exercise result/download API behavior.

## Files likely relevant for implementation

Existing files likely touched:

- `backend/app/api/jobs.py`
- `backend/app/services/jobs.py`
- `backend/app/schemas/jobs.py`
- `backend/app/db/models.py`
- `backend/app/core/auth.py`
- `backend/app/core/authorization.py`
- `backend/app/core/storage_paths.py`
- `backend/app/core/config.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/conftest.py`
- `backend/index.md`

Potential new files, if splitting keeps responsibilities clearer:

- `backend/app/services/results.py`
- `backend/app/schemas/results.py`
- `backend/tests/test_job_results_api.py`

Files not expected to change in this phase:

- Product docs under `docs/`.
- Frontend source.
- CV worker source.
- Training source.
- Alembic migration, unless implementation discovers verified schema mismatch.
