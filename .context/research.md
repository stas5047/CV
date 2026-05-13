# Phase 11 Research Contract

## Current phase

- Confirmed current phase: `Phase 11 - Admin backend APIs and safe storage cleanup`.
- Direction: Backend / Admin.
- Goal: Implement admin-only global statistics, global history, basic user list, and conservative storage cleanup.
- Risk level: not provided by user; assume HIGH because phase adds admin-only global data visibility and physical file cleanup risk.

## Docs consulted

Read first:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Relevant docs listed by current phase:

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- `git status --short` shows existing modified files before this planning write:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Backend project exists with FastAPI, SQLAlchemy models, Alembic, tests, auth, media, model, job, result/download code.
- API router currently includes `auth`, `health`, `media`, `models`, and `jobs`; no `admin` router is included.
- `get_current_admin_user` exists in `backend/app/core/authorization.py` and returns HTTP 403 for non-admin users.
- `UserResponse` exists and excludes `password_hash`.
- `JobListResponse` / `JobDetailResponse` exist and avoid internal result paths.
- `list_visible_jobs` already supports admin-wide job listing and owner/status/media/model/date filters when current user is admin.
- Safe storage helpers exist: `validate_relative_storage_path`, `safe_join_storage_path`, `safe_download_filename`, upload filename sanitizer.
- ORM models exist for `users`, `media_files`, `processing_jobs`, `detections`, `tracks`, `model_versions`, `experiment_runs`, and `experiment_metrics`.
- Soft deletion exists for media/jobs via `deleted_at`.

## WARNING: CONFLICT

- `docs/index.md` says current implementation contains only Phase 1 placeholders and that `backend/`, `frontend/`, and `cv/` do not yet contain product application scaffolds.
- Repository facts and `backend/index.md` show backend phases through job/result/download APIs exist.
- Product behavior docs still align with Phase 11 route goals; implementation-state text in `docs/index.md` is stale.

## Existing implementation state

- Implemented backend surfaces:
  - health endpoints;
  - settings/logging/CORS;
  - SQLAlchemy data model and initial migration;
  - setup/storage bootstrap/admin seed;
  - JWT auth, register/login/me;
  - authorization and path safety utilities;
  - media upload/list/detail/soft-delete;
  - model registry list/detail/register/activate;
  - job create/list/detail/delete/summary/detections/tracks/result/download.
- Not implemented in this checkout:
  - `GET /api/admin/stats`;
  - `GET /api/admin/jobs`;
  - `GET /api/admin/users`;
  - `POST /api/admin/storage/cleanup`;
  - admin API schemas/services/tests.
- Existing tests use SQLite-backed FastAPI `TestClient` fixtures with local temp storage.

## Unknowns and assumptions

Confirmed facts:

- Admin routes must require explicit admin role.
- Regular users must not access admin routes.
- Admin user list must not expose password hashes or sensitive fields.
- Cleanup must not delete active model weights, active model cards, files referenced by non-deleted records, recent user results accidentally, or files needed by visible completed jobs.
- Storage paths in DB and API responses must remain relative/logical; no absolute paths exposed.
- Cleanup actions must be logged safely.

Assumptions:

- Use existing admin dependency rather than adding new role system.
- Use existing response patterns with paginated lists where lists can grow.
- `GET /api/admin/jobs` can reuse existing safe job detail/list response behavior rather than exposing DB path fields.
- `GET /api/admin/users` can reuse safe user profile fields already exposed by `UserResponse`.
- Cleanup should start maximally conservative. Because docs do not define a deletion age/retention policy, Phase 11 must not physically delete from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/`; it may only report those categories. Physical deletion, if implemented, must be limited to clearly safe unreferenced files under `temp/`.
- No frontend, worker, training, schema migration, or product-doc change belongs in this phase unless admin implementation proves a documented backend command/index update is required.

Unknowns needing care during implementation:

- Exact response fields for global stats are not specified in current phase docs.
- Exact request/response contract for storage cleanup is not specified.
- Exact retention rule for "recent user results" is not specified.
- Whether admin job history must live only under `/api/admin/jobs` or may internally reuse existing `/api/jobs` logic is not specified; public route must still exist as documented.
- `model_versions` stores `weights_path` but not a model-card path, so active model-card protection must be derived from the active model directory or documented `models/{model_version_id}/model_card.json` layout.

## Files likely relevant for implementation

Likely create:

- `backend/app/api/admin.py`
- `backend/app/schemas/admin.py`
- `backend/app/services/admin.py`
- `backend/tests/test_admin_api.py`

Likely modify:

- `backend/app/api/router.py`
- `backend/index.md` only if commands/files list changes are part of workflow

Likely read/reference:

- `backend/app/core/authorization.py`
- `backend/app/core/storage_paths.py`
- `backend/app/core/logging.py`
- `backend/app/core/config.py`
- `backend/app/db/models.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/results.py`
- `backend/tests/conftest.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_models_api.py`
- `backend/tests/test_security_utils.py`
