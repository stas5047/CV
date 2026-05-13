# Phase 2 Research - Backend FastAPI Scaffold, Settings, Logging, And Health

## Current Phase

- Confirmed current phase: Phase 2 - Backend FastAPI scaffold, settings, logging, and health.
- Source: `docs/phase.md`.
- Risk: not provided by user as concrete value. Assumption: MEDIUM, because this phase creates backend foundation, environment parsing, logging safety, CORS, DB connectivity, Docker startup, and public health endpoints.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- Existing `.context/research.md`, `.context/design.md`, `.context/plan.md` were empty.

## Confirmed Repository Facts

- Checkout is Git repository.
- `git status --short` shows modified context/review/status files and `docs/phase.md`.
- Target files `.context/research.md`, `.context/design.md`, and `.context/plan.md` existed and were empty before this contract.
- Root contains `docker-compose.yml`, `docker-compose.gpu.yml`, `Makefile`, `.env.example`, `README.md`, `AGENTS.md`, `CLAUDE.md`.
- Existing top-level implementation folders: `backend/`, `frontend/`, `cv/`, `training/`, `scripts/`, `storage/`, `docs/`.
- `backend/` contains only `Dockerfile` and `index.md`.
- `backend/index.md` confirms no backend scaffold, dependency manifest, application package, migrations, or tests exist yet.
- `backend/Dockerfile` is Phase 1 placeholder and does not start FastAPI.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- `docker-compose.yml` mounts `./storage:/app/storage` into `backend` and `cv-worker`.
- `.env.example` includes safe placeholder values for database, auth, storage, backend, CV, worker, and local port variables.
- README states Phase 1 scaffold only; `/api/health` and backend product routes are not available yet.

## Existing Implementation State

- Backend application: not implemented.
- Backend dependency manifest: not implemented.
- Backend settings loader: not implemented.
- Backend structured logging: not implemented.
- Backend API routes: not implemented.
- `GET /api/health`: not implemented.
- `GET /api/health/db`: not implemented.
- Backend database connectivity layer: not implemented.
- Backend CORS configuration: not implemented.
- Backend tests: not implemented.
- Alembic configuration: not implemented in current checkout, but Phase 2 requires dependency and connectivity skeleton only. Concrete schema/migrations belong to Phase 3.
- Auth endpoints, JWT flow, user schema, upload APIs, jobs, worker queue, models, experiments, frontend UI: later phases, out of scope for Phase 2.

## Confirmed Product Facts

- All API routes must use `/api` prefix.
- Health endpoints are public: `GET /api/health` and `GET /api/health/db`.
- Health endpoints must not expose secrets, internal configuration, database passwords, JWT secrets, or raw environment values.
- Backend is FastAPI with Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL driver, JWT auth helpers later, and test/lint tooling.
- Backend must configure CORS from explicit `BACKEND_CORS_ORIGINS`; wildcard must not be used in non-local configurations.
- Phase 2 implementation contract will reject wildcard CORS origins entirely, including local mode. This is stricter than docs, still doc-consistent, and avoids adding a new environment flag to define local/non-local mode.
- Backend logs must not contain passwords, password hashes, JWT tokens, JWT secrets, DB passwords, admin password, or sensitive environment values.
- PostgreSQL stores structured records only; no binary media storage.
- Backend and CV worker communicate through PostgreSQL and shared storage, not HTTP job-loop calls.
- Long media processing must not run inside backend requests.
- Phase 2 validation expects backend lint/format checks, backend tests, safe health responses, DB health without secret leakage, and backend container startup in Docker Compose.

## Unknowns And Assumptions

- User did not replace `<PHASE NUMBER AND TITLE>` or `<LOW | MEDIUM | HIGH>` placeholders. Assumption: use `docs/phase.md` for phase and treat risk as MEDIUM.
- Exact Python packaging tool is not prescribed. Assumption: choose one standard backend-local manifest during implementation, such as `pyproject.toml`, without adding unrelated repo tooling.
- Exact health response JSON shape is not prescribed. Assumption: implement minimal stable safe JSON sufficient for frontend/service health, without exposing config values.
- Exact lint/format tools are not prescribed. Assumption: use backend-local tools chosen in dependency manifest and document exact commands in `backend/index.md` if commands change.
- Exact PostgreSQL driver is not prescribed beyond PostgreSQL driver. Assumption: use a SQLAlchemy 2-compatible driver and keep one consistent `DATABASE_URL` format.
- Existing `docker-compose.yml` does not publish backend port. Phase 2 requires backend container startup and health endpoint verification; implementation may need to add backend port mapping using existing `BACKEND_PORT`.
- Existing target context files were empty, so replacing them does not remove substantive content.
- `.env.example` already uses explicit local frontend origins for `BACKEND_CORS_ORIGINS`, so rejecting wildcard values does not break documented local setup.

## Files Likely Relevant For Implementation

- `backend/Dockerfile`
- `backend/index.md`
- `backend/pyproject.toml`
- `backend/alembic.ini`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/core/cors.py`
- `backend/app/db/session.py`
- `backend/app/api/__init__.py`
- `backend/app/api/health.py`
- `backend/app/api/router.py`
- `backend/tests/conftest.py`
- `backend/tests/test_settings.py`
- `backend/tests/test_health.py`
- `docker-compose.yml`
- `.env.example`
- `README.md`

## Conflict Check

- No `WARNING: CONFLICT` found between consulted docs for Phase 2 scope.
- Potential implementation caution: `docker-compose.yml` currently has no backend published port, while Phase 2 validation needs direct health checks. This is not a docs conflict; it is an implementation gap.
