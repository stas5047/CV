# Research - Phase 13 Backend Contract Audit

## Current Phase

- Current phase: `Phase 13 - Backend contract, pagination, OpenAPI, and security test audit`.
- Source: `docs/phase.md`.
- Risk input: unspecified placeholder. Assumption: `HIGH`, because phase audits auth, ownership, API contract, OpenAPI, errors, pagination, downloads, and security tests before worker/frontend depend on backend.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`

## Confirmed Repository Facts

- Git checkout exists.
- `git status --short` shows modified files before this contract work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Existing `.context/research.md`, `.context/design.md`, `.context/plan.md` were zero bytes before writing.
- Backend project exists with `backend/pyproject.toml`, FastAPI app, API route modules, SQLAlchemy models, Alembic migration, service modules, schemas, and tests.
- Backend dev commands are available from `backend/index.md` and `backend/pyproject.toml`:
  - `python -m ruff check .`
  - `python -m pytest`
- Backend route registration uses `api_router = APIRouter(prefix="/api")` in `backend/app/api/router.py`.
- App factory includes API router in `backend/app/main.py`.
- Implemented route groups found:
  - health: `/api/health`, `/api/health/db`
  - auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`
  - media: `/api/media`, `/api/media/{media_id}`
  - jobs/results: `/api/jobs`, `/api/jobs/{job_id}`, `/api/jobs/{job_id}/summary`, `/api/jobs/{job_id}/detections`, `/api/jobs/{job_id}/tracks`, `/api/jobs/{job_id}/result`, `/api/jobs/{job_id}/download/{kind}`
  - models: `/api/models`, `/api/models/{model_id}`, `/api/models/{model_id}/activate`
  - experiments: `/api/experiments`, `/api/experiments/import`, `/api/experiments/{experiment_id}`
  - admin: `/api/admin/stats`, `/api/admin/jobs`, `/api/admin/users`, `/api/admin/storage/cleanup`
- List schemas use `items`, `total`, `limit`, `offset` in media, jobs, detections, tracks, models, experiments, admin jobs, and admin users.
- Tests exist for auth, security utilities, media validation/API, jobs/results/downloads, models, experiments, admin API, logging, settings, setup, health, and data model.
- No custom global error response schema or FastAPI exception handlers were found by search.
- No explicit OpenAPI audit test was found by search.

## Existing Implementation State

- Backend has product API surface implemented through Phase 12-like endpoints, including admin and experiments.
- `/api` prefix appears centralized and consistent in route registration.
- Pagination is already present on growable list endpoints, but phase must audit consistency against `API.md`.
- Tests cover many authorization, ownership, upload validation, path safety, and download cases.
- Existing download implementation exposes one dynamic OpenAPI path: `/api/jobs/{job_id}/download/{kind}`.
- `API.md` documents three concrete download endpoints:
  - `/api/jobs/{job_id}/download/media`
  - `/api/jobs/{job_id}/download/csv`
  - `/api/jobs/{job_id}/download/json`
- Existing tests call concrete download URLs, but OpenAPI likely presents the dynamic `{kind}` route. This is an implementation contract issue to audit in Phase 13, not a docs conflict.
- Error responses currently appear to rely on FastAPI default `{"detail": ...}` behavior and Pydantic validation errors.
- Response models are present for route success responses, but route-level `responses=` metadata was not found.
- `README.md` current-state wording appears older than backend implementation state, while `backend/index.md` is more current. Phase 13 scope includes updating README/API notes during implementation.

## Unknowns And Assumptions

- Unknown: actual backend test status was not run in this planning phase.
- Unknown: generated OpenAPI schema contents were not inspected by running the app.
- Unknown: whether frontend wants a formal error envelope beyond FastAPI default `detail`; docs require clear errors suitable for Ukrainian localization but do not define a strict envelope.
- Assumption: Phase 13 may add tests and small backend contract fixes, but must not add new product behavior beyond documented endpoints, pagination, OpenAPI usability, security coverage, and README/API notes.
- Assumption: Dynamic download route may need explicit concrete routes or OpenAPI metadata so frontend sees documented download operations.
- Assumption: "API notes" means existing README/backend index or existing code comments/metadata, not new product docs, unless implementation reveals current docs/commands changed.
- Accepted planning-review fact: README/API notes audit and update is required in Phase 13 because `README.md` is already stale against implemented backend endpoint groups.
- Accepted planning-review decision: Phase 13 will not introduce a new shared error envelope unless audit proves current behavior violates docs. Minimal accepted MVP standard is safe, predictable FastAPI-compatible `detail` responses where string and list validation details are tested as frontend-consumable and do not expose secrets, stack traces, absolute paths, or forbidden fields.
- Accepted planning-review fact: OpenAPI tests must assert the documented concrete download paths `/api/jobs/{job_id}/download/media`, `/api/jobs/{job_id}/download/csv`, and `/api/jobs/{job_id}/download/json`.
- Accepted planning-review fact: API response/output boundary audit should use a reusable scan fixture or helper for representative JSON responses to catch absolute paths and forbidden CV-boundary field names.

## Files Likely Relevant For Implementation

- `backend/app/main.py`
- `backend/app/api/router.py`
- `backend/app/api/auth.py`
- `backend/app/api/health.py`
- `backend/app/api/media.py`
- `backend/app/api/jobs.py`
- `backend/app/api/models.py`
- `backend/app/api/experiments.py`
- `backend/app/api/admin.py`
- `backend/app/api/deps.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/media.py`
- `backend/app/schemas/jobs.py`
- `backend/app/schemas/models.py`
- `backend/app/schemas/experiments.py`
- `backend/app/schemas/admin.py`
- `backend/app/services/media.py`
- `backend/app/services/jobs.py`
- `backend/app/services/results.py`
- `backend/app/services/models.py`
- `backend/app/services/experiments.py`
- `backend/app/services/admin.py`
- `backend/app/core/auth.py`
- `backend/app/core/authorization.py`
- `backend/app/core/storage_paths.py`
- `backend/app/core/cors.py`
- `backend/app/core/logging.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_security_utils.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_media_validation.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_models_api.py`
- `backend/tests/test_experiments_api.py`
- `backend/tests/test_admin_api.py`
- `backend/tests/test_health.py`
- `backend/tests/test_logging.py`
- `backend/tests/conftest.py`
- `README.md`
- `backend/index.md`
