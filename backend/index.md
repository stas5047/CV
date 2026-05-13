# AeroVision - Backend Index

## General Description

The `backend/` folder contains the AeroVision FastAPI backend application.

According to `../docs/`, this backend exposes the `/api` REST API. Current implementation contains the FastAPI foundation, typed environment settings, safe logging baseline, explicit CORS configuration, database connectivity skeleton, public health endpoints, SQLAlchemy ORM models for the documented schema, Alembic configuration, the initial database migration, local/demo startup migration switches, idempotent admin seed/setup, storage bootstrap, JWT authentication, public registration, login, current-user endpoints, reusable admin/ownership authorization helpers, storage path/filename safety utilities, and the authenticated media upload/list/detail/soft-delete API. Later phases add jobs/results/models/experiments/admin APIs, worker queue behavior, and safe downloads.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | Backend container image that installs the backend package, includes Alembic files, and runs `startup.sh`. |
| `alembic.ini` | Alembic configuration for backend database migrations. |
| `pyproject.toml` | Backend Python dependencies, dev dependencies, pytest configuration, and Ruff configuration. |
| `startup.sh` | Container startup script that optionally runs migrations and setup before Uvicorn. |
| `app/` | FastAPI app package with API router, health/auth/media endpoints, settings, CORS, logging, password hashing and JWT helpers, authorization helpers, storage path/filename safety utilities, media upload service, database connectivity, ORM models, schemas, and setup command. |
| `migrations/` | Alembic migration environment and initial schema migration. |
| `tests/` | Backend tests for settings, health endpoints, logging redaction, Phase 3 data-model constraints, Phase 4 setup behavior, Phase 5 auth behavior, Phase 6 security utilities, and Phase 7 media upload/validation behavior. |
| `index.md` | Backend folder summary, current contents, and backend-local commands. |

No job/result/model/experiment/admin product APIs or worker queue logic exist yet in this checkout.

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
