# AeroVision - Backend Index

## General Description

The `backend/` folder is reserved for the AeroVision FastAPI backend application.

According to `../docs/`, this backend exposes the `/api` REST API. Current implementation contains the Phase 2 FastAPI foundation: typed environment settings, safe logging baseline, explicit CORS configuration, database connectivity skeleton, and public health endpoints. Later phases add JWT authentication, role/ownership rules, upload validation, media/jobs/results/models/experiments/admin APIs, and safe downloads.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | Backend container image that installs the backend package and starts Uvicorn with the FastAPI app factory. |
| `pyproject.toml` | Backend Python dependencies, dev dependencies, pytest configuration, and Ruff configuration. |
| `app/` | FastAPI app package with API router, health endpoints, settings, CORS, logging, and database connectivity skeleton. |
| `tests/` | Phase 2 tests for settings, health endpoints, and logging redaction. |
| `index.md` | Backend folder summary, current contents, and backend-local commands. |

No auth endpoints, ORM models, Alembic migration scripts, upload/media/job/result/model/experiment/admin APIs, or worker queue logic exist yet in this checkout.

## Commands

| Command | Status |
|---|---|
| `python -m pip install -e ".[dev]"` | installs backend runtime and dev dependencies from `backend/` |
| `python -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000` | starts the backend app from `backend/` when required environment variables are set |
| `python -m ruff check .` | runs backend lint checks from `backend/` |
| `python -m pytest` | runs backend tests from `backend/` |
| Backend Docker build | available through root `docker compose --env-file .env.example build backend` |
| Database migration and seed | not available yet |
