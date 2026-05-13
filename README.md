# AeroVision

AeroVision is documented as a Dockerized full-stack drone computer-vision subsystem for uploaded images and videos. Current repository state includes the repository/runtime scaffold and backend implementation through the Phase 13 API contract audit.

## Current State

This checkout provides:

- repository layout placeholders;
- safe `.env.example`;
- Docker Compose baseline with `postgres`, `backend`, `cv-worker`, and `frontend`;
- shared storage mount for backend and CV worker at `/app/storage`;
- optional GPU Compose override for `cv-worker` only;
- storage directory bootstrap helper;
- FastAPI backend scaffold with `/api/health` and `/api/health/db`;
- backend settings, explicit CORS configuration, safe logging baseline, and database connectivity skeleton;
- SQLAlchemy models and Alembic initial migration;
- backend startup switches for local/demo migrations and seed/setup;
- idempotent backend seed/setup command that creates storage folders and seeds the admin account from environment variables;
- backend JWT authentication, public registration toggle, current-user endpoint, admin role checks, ownership helpers, CORS validation, and path-safety utilities;
- backend media upload/list/detail/soft-delete API with validation and generated relative storage paths;
- backend model registry API with admin registration and activation;
- backend queued job creation, job history/detail/result metadata, detections/tracks list endpoints, and concrete documented result download routes;
- backend admin stats/jobs/users/storage-cleanup API;
- backend experiment import/list/detail API;
- backend OpenAPI contract checks for documented paths, paginated list schemas, safe FastAPI `detail` errors, and API output boundary scanning.

Not available yet:

- CV model loading, worker queue polling, inference, tracking, exports;
- React/Vite frontend UI.

## Initial Setup

1. Install Docker and Docker Compose.
2. Copy `.env.example` to `.env`.
3. Replace placeholder secret values in `.env` before any real use.
   Demo admin credentials come from `ADMIN_EMAIL` and `ADMIN_PASSWORD`. `ADMIN_PASSWORD` must be at least 8 characters. Use these credentials only for local/demo setup and replace the placeholder password before real use.
4. Create local storage folders:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1
```

5. Validate Compose:

```powershell
docker compose --env-file .env.example config
```

6. Start the placeholder baseline using your `.env`:

```powershell
docker compose up --build
```

By default, backend startup runs `alembic upgrade head` and then `python -m app.setup` before Uvicorn. Disable this local/demo behavior only when you plan to run those steps manually:

```env
RUN_MIGRATIONS_ON_START=false
RUN_SEED_ON_START=false
```

Manual backend setup commands:

```powershell
cd backend
alembic upgrade head
python -m app.setup
```

## CPU And GPU

CPU mode is the default. GPU mode is optional and isolated to `cv-worker`:

```powershell
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config
```

Use GPU mode only on hosts with NVIDIA container runtime configured.

## Storage Policy

Local generated files belong under `storage/`:

- `uploads/`
- `results/`
- `reports/`
- `models/`
- `temp/`
- `datasets/`

Do not commit uploads, generated results, reports, datasets, model weights, or temporary files.

## Commands

| Command | Status |
|---|---|
| `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1` | available |
| `docker compose --env-file .env.example config` | available |
| `docker compose up --build` | starts scaffold services; backend exposes implemented `/api` endpoints when `.env` is configured |
| `python -m pip install -e ".[dev]"` from `backend/` | installs backend dependencies |
| `python -m pytest` from `backend/` | runs backend tests |
| `python -m ruff check .` from `backend/` | runs backend lint checks |
| `alembic upgrade head` from `backend/` | applies backend database migrations |
| `python -m app.setup` from `backend/` | creates required storage folders and idempotently seeds configured admin |
| CV worker tests | not available yet |
| Frontend tests/build | not available yet |

## Backend API Notes

Implemented backend endpoint groups use the `/api` prefix:

- health: `/api/health`, `/api/health/db`;
- auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/me`;
- media: `/api/media`, `/api/media/{media_id}`;
- jobs/results: `/api/jobs`, `/api/jobs/{job_id}`, `/api/jobs/{job_id}/summary`, `/api/jobs/{job_id}/detections`, `/api/jobs/{job_id}/tracks`, `/api/jobs/{job_id}/result`;
- downloads: `/api/jobs/{job_id}/download/media`, `/api/jobs/{job_id}/download/csv`, `/api/jobs/{job_id}/download/json`;
- models: `/api/models`, `/api/models/{model_id}`, `/api/models/{model_id}/activate`;
- experiments: `/api/experiments`, `/api/experiments/import`, `/api/experiments/{experiment_id}`;
- admin: `/api/admin/stats`, `/api/admin/jobs`, `/api/admin/users`, `/api/admin/storage/cleanup`.
