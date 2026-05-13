# Phase 3 Research - Database schema and initial Alembic migration

## Current phase

- Phase: `Phase 3 - Database schema and initial Alembic migration`
- Direction: Backend / Database
- Goal: implement PostgreSQL schema and initial migration.
- Risk: not provided by user; assumption: `MEDIUM` because phase changes persistent schema and migration path.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
- Relevant existing `.context/` files: present but empty for `research.md`, `design.md`, `plan.md`, `status.md`, and `review-plan-resolution.md`.

## Confirmed repository facts

- Git checkout exists.
- `git status --short` showed existing modified files before this contract update:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Root contains `docker-compose.yml`, `docker-compose.gpu.yml`, `.env.example`, `Makefile`, `README.md`, `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, and `scripts/`.
- Backend scaffold exists from Phase 2:
  - `backend/pyproject.toml`
  - `backend/app/main.py`
  - `backend/app/api/router.py`
  - `backend/app/api/health.py`
  - `backend/app/core/config.py`
  - `backend/app/core/cors.py`
  - `backend/app/core/logging.py`
  - `backend/app/db/session.py`
  - `backend/app/db/health.py`
  - `backend/tests/`
- Backend dependencies already include SQLAlchemy 2.x, Alembic, and psycopg.
- `backend/app/db/session.py` creates SQLAlchemy engine from `DATABASE_URL` and exposes session factory.
- `backend/index.md` says no ORM models, Alembic migration scripts, auth endpoints, product APIs, or worker queue logic exist yet.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`; backend and worker mount `./storage:/app/storage`.
- `.env.example` contains database, auth, storage, backend, CV, worker, and port variables with safe placeholder values.

## Existing implementation state

- Phase 1 scaffold appears present.
- Phase 2 backend foundation appears present:
  - settings
  - logging redaction baseline
  - CORS validation
  - database connectivity skeleton
  - `/api/health`
  - `/api/health/db`
  - backend tests for health, settings, and logging
- Phase 3 implementation not present:
  - no SQLAlchemy declarative models found
  - no Alembic configuration found
  - no migration versions found
  - no database constraint/index tests found

## Confirmed database requirements

- Required tables:
  - `users`
  - `media_files`
  - `processing_jobs`
  - `detections`
  - `tracks`
  - `model_versions`
  - `experiment_runs`
  - `experiment_metrics`
- PostgreSQL stores structured records and metadata only.
- Media, result media, CSV, JSON exports, model weights, datasets, and report artifacts stay in filesystem storage.
- Database path fields must store relative paths only.
- Soft deletion is required for `media_files` and `processing_jobs`.
- Required queue fields on `processing_jobs` include status, progress, heartbeat, lock fields, retry count, start/complete timestamps, and result/export paths.
- No-detection jobs complete with `status = completed`; zero detection rows are valid.
- `model_versions.is_active` must support only one active default model.
- `tracks` needs unique `(job_id, track_id)`.
- Required indexes are listed in `docs/DATA_MODEL.md`.

## Unknowns and assumptions

- User did not replace `<PHASE NUMBER AND TITLE>` or `<LOW | MEDIUM | HIGH>` placeholders. Assumption: current phase comes from `docs/phase.md`; risk treated as `MEDIUM`.
- Exact internal module split for models is not specified. Assumption: implementation may choose cohesive modules under existing `backend/app/db/` or nearby backend package paths.
- Exact SQL type choices are not specified for JSON fields. Assumption: use PostgreSQL-compatible JSON type through SQLAlchemy, with migration output matching docs.
- Exact UUID generation strategy is not specified. Assumption: use application-side UUID defaults unless migration policy chooses PostgreSQL UUID generation.
- Exact timestamp timezone policy is not stated. Assumption: use timezone-aware UTC timestamps consistently.
- Cross-table invariants may not all fit cleanly into database constraints. Docs allow documenting limitations where service validation must cover them.
- Auth/user seed is later phase. Phase 3 should create schema only, not implement registration/login/seed behavior.

## Files likely relevant for implementation

- `backend/pyproject.toml`
- `backend/app/db/session.py`
- `backend/app/db/__init__.py`
- Backend ORM model modules under `backend/app/db/` or equivalent backend package path.
- Alembic config and migration files under backend migration structure.
- `backend/tests/` database/model smoke tests.
- `docker-compose.yml` only for running PostgreSQL during migration validation, not for product behavior changes.
- `backend/index.md` only if implementation changes backend-local commands or current contents in implementation phase.
