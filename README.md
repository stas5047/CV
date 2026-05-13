# AeroVision

AeroVision is documented as a Dockerized full-stack drone computer-vision subsystem for uploaded images and videos. Current repository state includes the Phase 1 scaffold and Phase 2 backend FastAPI foundation.

## Current State

This phase provides:

- repository layout placeholders;
- safe `.env.example`;
- Docker Compose baseline with `postgres`, `backend`, `cv-worker`, and `frontend`;
- shared storage mount for backend and CV worker at `/app/storage`;
- optional GPU Compose override for `cv-worker` only;
- storage directory bootstrap helper;
- FastAPI backend scaffold with `/api/health` and `/api/health/db`;
- backend settings, explicit CORS configuration, safe logging baseline, and database connectivity skeleton.

Not available yet:

- database schema and migrations;
- authentication, uploads, jobs, downloads, or admin APIs;
- CV model loading, worker queue polling, inference, tracking, exports;
- React/Vite frontend UI.

## Initial Setup

1. Install Docker and Docker Compose.
2. Copy `.env.example` to `.env`.
3. Replace placeholder secret values in `.env` before any real use.
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
| CV worker tests | not available yet |
| Frontend tests/build | not available yet |
