# Phase 9 Research

## Current phase

- Confirmed from `docs/phase.md`: Phase 9 - Job creation API and model selection resolution.
- Direction: Backend.
- Goal: implement `POST /api/jobs` for queued processing job creation with validated processing parameters and resolved model selection.
- Risk level: not supplied by user prompt; placeholder remained unfilled. Assumption: MEDIUM because phase touches authenticated backend API, ownership, job queue records, model resolution, and security-sensitive parameter validation.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase relevant docs from `docs/phase.md`:
  - `docs/API.md`
  - `docs/CV_PIPELINE.md`
  - `docs/DATA_MODEL.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/TESTING_QA.md`

Additional repo/context files consulted for implementation-state facts:

- `.context/status.md`
- prior `.context/research.md`, `.context/design.md`, `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/review-code-resolution.md`
- `backend/index.md`
- `README.md`
- `.env.example`
- selected backend source and test files listed below

## Confirmed repository facts

- `git status --short` before this contract work showed `docs/phase.md` already modified.
- `docs/phase.md` identifies current phase as Phase 9.
- Root contains expected project areas: `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, Compose files, `.env.example`, `Makefile`, and storage bootstrap script.
- Backend is an implemented FastAPI app, not placeholder-only.
- Backend router currently includes auth, health, media, and models routers.
- No `backend/app/api/jobs.py`, `backend/app/schemas/jobs.py`, `backend/app/services/jobs.py`, or `backend/tests/test_jobs_api.py` exists.
- `backend/app/db/models.py` already defines `ProcessingJob` with documented queue fields:
  - `user_id`
  - `media_file_id`
  - `model_version_id`
  - `status`
  - `input_params_json`
  - result/export path fields
  - progress, heartbeat, lock, retry, started/completed, soft-delete, timestamps
- `ProcessingJob` already has constraints for valid status, progress 0-100, relative result paths, and required queue indexes.
- `MediaFile` already has ownership, soft-deletion, media type, metadata, and relative stored path fields.
- `ModelVersion` already has `is_active`, relative `weights_path`, and active-model uniqueness.
- `backend/app/api/media.py` implements upload/list/detail/delete using active-user auth.
- `backend/app/services/media.py` hides soft-deleted media and enforces user/admin visibility for media reads.
- `backend/app/api/models.py` implements authenticated model list/detail and admin create/activate.
- `backend/app/services/models.py` validates model weights paths and active-model state.
- `backend/app/core/auth.py` provides active JWT user dependency.
- `backend/app/core/authorization.py` provides admin and ownership helpers.
- `.env.example` contains `ACTIVE_MODEL_ID=`, but `backend/app/core/config.py` does not yet expose `active_model_id`.
- Existing tests cover auth, media API, model API, schema constraints, settings, logging, setup, and security utilities.
- `backend/pyproject.toml` provides backend commands: `python -m ruff check .` and `python -m pytest`.

## Existing implementation state

Implemented before Phase 9:

- `/api/health` and `/api/health/db`.
- JWT auth, public registration, login, current-user endpoint.
- Active-account enforcement.
- Admin dependency and ownership helpers.
- Relative storage path and safe filename utilities.
- Media upload, list, detail, and soft-delete API.
- Model registry list, detail, register, and activate API.
- SQLAlchemy schema and initial Alembic migration for documented tables.
- Local/demo setup and seeded admin command.

Not implemented yet:

- `POST /api/jobs`.
- Job request/response schemas.
- Job service/domain logic.
- Model-selection resolution for job creation.
- Job creation tests.
- Job listing/detail/cancel endpoints. Those are later phases unless `docs/phase.md` changes.
- Worker queue polling/claiming and CV processing.
- Results/download APIs.
- Frontend upload/job UI.

## Unknowns and assumptions

- WARNING: CONFLICT
  - `docs/index.md` says backend/frontend/CV folders contain placeholder Dockerfiles only and no product app scaffolds/routes/tests.
  - `README.md` says authentication, uploads, jobs, downloads, and admin APIs are not available yet.
  - Actual repo and `backend/index.md` show implemented auth, media, models, schema, migrations, setup, and tests.
  - Contract uses `docs/phase.md` for current phase and actual backend files for implementation-state facts.
- User prompt left `<PHASE NUMBER AND TITLE>` and `<LOW | MEDIUM | HIGH>` placeholders unfilled. Assumption: current phase comes from `docs/phase.md`; risk treated as MEDIUM.
- `ACTIVE_MODEL_ID` exists in `.env.example` and docs, but settings code lacks it. Assumption: Phase 9 may add an optional settings field because model fallback is in phase scope.
- Docs do not define exact `POST /api/jobs` request/response schema field names beyond documented parameters and `processing_jobs` fields. Assumption: schemas mirror existing backend style and documented snake_case names.
- Docs do not state exact numeric ranges for confidence, IoU, or image size. Assumption: confidence and IoU thresholds are validated as numeric 0-1 values; image size uses documented default `640` and remains internal unless already configured.
- Docs define tracker selection as user-facing for video only. Phase 9 must reject client-supplied `tracker_type` for image media, accept/default only allowed video tracker values for video media, and keep image jobs from behaving like tracked video jobs. `input_params_json.tracker_type` may still use documented internal default `bytetrack`; image worker behavior remains no tracking and `track_id = null`.
- Docs do not require explicit `model_version_id` to be active. Phase 9 API policy: any existing registered model may be selected explicitly, including inactive registered models; `is_active` controls default model selection only. This policy must be visible in tests.
- `ACTIVE_MODEL_ID` fallback is assumed to be a UUID referencing an existing `model_versions.id`; if unset/invalid/missing and no active DB model exists, job creation must fail safely.

## Files likely relevant for implementation

Existing files likely touched:

- `backend/app/api/router.py`
- `backend/app/core/config.py`
- `backend/app/core/auth.py`
- `backend/app/core/authorization.py`
- `backend/app/db/models.py`
- `backend/app/schemas/media.py`
- `backend/app/schemas/models.py`
- `backend/app/services/media.py`
- `backend/app/services/models.py`
- `backend/tests/conftest.py`
- `backend/tests/test_data_model.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_models_api.py`
- `backend/tests/test_settings.py`
- `backend/index.md`

Likely new files:

- `backend/app/api/jobs.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/jobs.py`
- `backend/tests/test_jobs_api.py`
