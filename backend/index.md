# AeroVision - Backend Index

## General Description

The `backend/` folder contains the AeroVision FastAPI backend application.

According to `../docs/`, this backend exposes the `/api` REST API. Current implementation contains the FastAPI foundation, typed environment settings, safe logging baseline, explicit CORS configuration, database connectivity skeleton, public health endpoints, SQLAlchemy ORM models for the documented schema, Alembic configuration, the initial database migration, local/demo startup migration switches, idempotent admin seed/setup, storage bootstrap, JWT authentication, public registration, login, current-user endpoints, reusable admin/ownership authorization helpers, storage path/filename safety utilities, the authenticated media upload/list/detail/soft-delete API, the authenticated/admin model registry API, queued job creation with model selection resolution, job history/detail/result/detection/track/download APIs, and admin-only stats/jobs/users/storage-cleanup APIs. Later phases add experiments APIs, worker queue behavior, and CV processing/export generation.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | Backend container image that installs the backend package, includes Alembic files, and runs `startup.sh`. |
| `alembic.ini` | Alembic configuration for backend database migrations. |
| `pyproject.toml` | Backend Python dependencies, dev dependencies, pytest configuration, and Ruff configuration. |
| `startup.sh` | Container startup script that optionally runs migrations and setup before Uvicorn. |
| `app/` | FastAPI app package with API router, health/auth/media/model/job/admin endpoints, settings, CORS, logging, password hashing and JWT helpers, authorization helpers, storage path/filename safety utilities, media upload, model registry, job creation, job results/download services, admin stats/storage cleanup services, database connectivity, ORM models, schemas, and setup command. |
| `migrations/` | Alembic migration environment and initial schema migration. |
| `tests/` | Backend tests for settings, health endpoints, logging redaction, Phase 3 data-model constraints, Phase 4 setup behavior, Phase 5 auth behavior, Phase 6 security utilities, Phase 7 media upload/validation behavior, Phase 8 model registry behavior, Phase 9 job creation/model selection behavior, Phase 10 job result/download behavior, and Phase 11 admin API behavior. |
| `index.md` | Backend folder summary, current contents, and backend-local commands. |

No experiment product APIs, worker queue logic, CV processing, or export generation exist yet in this checkout.

## Commands

| Command | Status |
|---|---|
| `python -m pip install -e ".[dev]"` | installs backend runtime and dev dependencies from `backend/` |
| `python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000` | starts the backend app from `backend/` when required environment variables are set |
| `python -m app.setup` | creates documented storage directories under `STORAGE_ROOT` and idempotently seeds configured admin |
| `python -m ruff check .` | runs backend lint checks from `backend/` |
| `python -m pytest` | runs backend tests from `backend/` |
| `alembic upgrade head` | applies backend database migrations from `backend/` when required environment variables are set |
| Backend Docker build | available through root `docker compose --env-file .env.example build backend` |
| Database migration in backend container | available through root `docker compose --env-file .env.example run --rm backend alembic upgrade head` |
| Database seed in backend container | available through root `docker compose --env-file .env.example run --rm backend python -m app.setup` |
