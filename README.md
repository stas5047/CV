# AeroVision

AeroVision is documented as a Dockerized full-stack drone computer-vision subsystem for uploaded images and videos. Current repository state includes the Docker Compose runtime, backend APIs, CV worker, React frontend, offline training utilities, and model/experiment artifact registration helpers.

## Current State

This checkout provides:

- repository layout placeholders;
- safe `.env.example`;
- Docker Compose runtime with `postgres`, `backend`, `cv-worker`, and `frontend`;
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
- CV worker with settings, secret-safe logging, startup device selection, database connectivity helpers, safe storage path resolution, PostgreSQL queue polling/claiming, stale-job recovery, image/video processing, annotated outputs, CSV/JSON exports, summaries, Docker entrypoint, and tests.
- Vite React frontend with Ukrainian auth, dashboard, upload, jobs/results, models, experiments, and admin pages.
- offline training utilities with dataset preparation, artifact validation, model-card/metrics templates, and backend API helpers for registering existing model weights paths and importing experiment metrics.

## Initial Setup

1. Install Docker and Docker Compose.
2. For optional GPU mode, install NVIDIA driver and NVIDIA Container Toolkit.
3. Copy `.env.example` to `.env`.
4. Replace placeholder secret values in `.env` before any real use.
   Demo admin credentials come from `ADMIN_EMAIL` and `ADMIN_PASSWORD`. `ADMIN_PASSWORD` must be at least 8 characters. Use these credentials only for local/demo setup and replace the placeholder password before real use.
5. Create local storage folders:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1
```

6. Place trained model artifacts under `storage/models/<model>/` when real processing is needed. Expected paths are relative to storage, for example `models/<model>/weights.pt` and `models/<model>/model_card.json`.
7. Validate Compose:

```powershell
docker compose --env-file .env.example config
```

8. Start the app using your `.env`:

```powershell
docker compose --env-file .env up --build
```

The frontend is served at `http://localhost:5173`, and the backend API is served at `http://localhost:8000/api` by default.

By default, backend startup runs `alembic upgrade head` and then `python -m app.setup` before Uvicorn. This applies migrations, creates required storage folders, and idempotently seeds the configured admin account. Disable this local/demo behavior only when you plan to run those steps manually:

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

Container equivalents:

```powershell
docker compose --env-file .env run --rm backend alembic upgrade head
docker compose --env-file .env run --rm backend python -m app.setup
```

Seeded admin policy:

- `ADMIN_EMAIL` and `ADMIN_PASSWORD` define the initial admin.
- setup hashes the password before storing it.
- public registration always creates regular `user` accounts only.
- do not commit real `.env` files or real credentials.

## Model Artifact Placement And Registration

Training is outside the running app. After a human runs the cloud notebook workflow and downloads artifacts, place them under storage:

```text
storage/models/<model>/
  weights.pt
  model_card.json
  metrics.json
```

Register model weights through the backend with an admin JWT. Prefer environment variable token input so tokens do not appear in shell history:

```powershell
$env:AEROVISION_API_TOKEN="<admin-jwt>"
python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 register-model --model-card storage/models/<model>/model_card.json --weights-path models/<model>/weights.pt
```

Import experiment metrics when available:

```powershell
$env:AEROVISION_API_TOKEN="<admin-jwt>"
python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 import-experiments --metrics storage/models/<model>/metrics.json --artifacts-path reports/<model>
```

## CPU And GPU

CPU mode is the default. GPU mode is optional and isolated to `cv-worker`:

```powershell
docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env up --build
```

Use GPU mode only on hosts with NVIDIA container runtime configured.
Do not expect fixed FPS; performance depends on hardware, media, model size, codec, and resolution.

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
| `docker compose --env-file .env up --build` | starts PostgreSQL, backend, CV worker, and frontend in CPU mode |
| `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env up --build` | starts GPU override with GPU access only for `cv-worker` |
| `make setup` | creates required storage folders |
| `make compose-config` | validates base Compose using `.env.example` by default |
| `make compose-config-gpu` | validates GPU Compose using `.env.example` by default |
| `make up ENV_FILE=.env` | starts CPU runtime |
| `make up-gpu ENV_FILE=.env` | starts optional GPU runtime |
| `make down ENV_FILE=.env` | stops runtime |
| `make logs ENV_FILE=.env` | follows Compose logs |
| `make migrate ENV_FILE=.env` | runs backend migrations in a container |
| `make seed ENV_FILE=.env` | runs backend setup/admin seed in a container |
| `make test` | runs backend, CV worker, frontend, and training tests through local toolchains |
| `python -m pip install -e ".[dev]"` from `backend/` | installs backend dependencies |
| `python -m pytest` from `backend/` | runs backend tests |
| `python -m ruff check .` from `backend/` | runs backend lint checks |
| `alembic upgrade head` from `backend/` | applies backend database migrations |
| `python -m app.setup` from `backend/` | creates required storage folders and idempotently seeds configured admin |
| `python -m pip install -e ".[dev]"` from `cv/` | installs CV worker dependencies |
| `python -m pytest` from `cv/` | runs CV worker tests |
| `python -m ruff check .` from `cv/` | runs CV worker lint checks |
| `python -m aerovision_worker.main --check-once` from `cv/` | runs CV worker startup smoke checks and exits |
| `npm install` from `frontend/` | installs frontend dependencies |
| `npm run lint` from `frontend/` | runs frontend lint checks |
| `npm test` from `frontend/` | runs frontend tests |
| `npm run build` from `frontend/` | builds the frontend |
| `python -m pip install -e "training[dev]"` | installs offline training utilities |
| `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json` | validates offline model card and metrics artifact shape |
| `python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 register-model --model-card storage/models/<model>/model_card.json --weights-path models/<model>/weights.pt` | registers an existing model weights path through the backend API with admin authorization |
| `python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 import-experiments --metrics storage/models/<model>/metrics.json --artifacts-path reports/<model>` | imports experiment metrics through the backend API with admin authorization |
| `docker compose --env-file .env.example build frontend` | builds the frontend container |

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

## Troubleshooting

- If `docker compose --env-file .env up --build` reports missing environment values, copy `.env.example` to `.env` and fill placeholders.
- If backend health is unavailable, inspect `docker compose --env-file .env logs backend`; migration or seed errors usually appear before Uvicorn starts.
- If `/api/health/db` fails, confirm `postgres` is healthy and `DATABASE_URL` matches `POSTGRES_*` values.
- If frontend loads but API calls fail, confirm `BACKEND_PORT` and `VITE_API_BASE_URL` resolve to the backend reachable from the browser.
- If worker logs model path errors, place weights under `storage/models/` and register/activate a model version.
- If GPU mode fails, verify NVIDIA Container Toolkit on host or use CPU mode.
