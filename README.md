# AeroVision

AeroVision is documented as a Dockerized full-stack drone computer-vision subsystem for uploaded images and videos. Current repository state includes the Phase 1 scaffold, Phase 2 backend FastAPI foundation, Phase 3 database schema/migration, and Phase 4 backend startup setup.

## Current State

This phase provides:

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
- idempotent backend seed/setup command that creates storage folders and seeds the admin account from environment variables.

Not available yet:

- authentication, uploads, jobs, downloads, or admin APIs;
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
| `docker compose up --build` | starts scaffold services; backend exposes health endpoints when `.env` is configured |
| `python -m pip install -e ".[dev]"` from `backend/` | installs backend dependencies |
| `python -m pytest` from `backend/` | runs backend tests |
| `python -m ruff check .` from `backend/` | runs backend lint checks |
| `alembic upgrade head` from `backend/` | applies backend database migrations |
| `python -m app.setup` from `backend/` | creates required storage folders and idempotently seeds configured admin |
| CV worker tests | not available yet |
| Frontend tests/build | not available yet |
