# Phase Contract Design

## Phase Goal

Create repository scaffold, safe environment example, minimal Docker Compose baseline, shared storage bootstrap, and honest README setup notes for Phase 1 only.

Do not implement product business logic, API contracts, database schema, CV processing, frontend UI, auth endpoints, migrations, worker polling, or training utilities in this phase.

## Intended Behavior From Docs

- Runtime service names must be:
  - `postgres`
  - `backend`
  - `cv-worker`
  - `frontend`
- Backend and CV worker must mount same shared storage path at `/app/storage`.
- Base CPU launch must be possible after setup; GPU acceleration is optional and isolated to `cv-worker`.
- `.env.example` must use safe placeholders only and cover documented variable groups:
  - database
  - auth
  - storage
  - backend
  - worker
  - CV
- Required storage folders are:
  - `uploads/`
  - `results/`
  - `reports/`
  - `models/`
  - `temp/`
  - `datasets/`
- Git ignore rules must prevent real `.env`, uploads, generated results, datasets, model weights, reports, temp files, Python caches, Node artifacts, and build outputs from being committed.
- README must describe current state honestly and not imply finished product features.
- Compose baseline may use placeholders, but must not introduce unsupported services like Celery, Redis, Flask, Streamlit, or RTSP/live-camera services.

## Architecture Decisions

- Keep service boundaries explicit in Compose:
  - frontend depends on backend only as frontend client target, not DB/storage.
  - backend connects to PostgreSQL and mounts storage.
  - cv-worker connects to PostgreSQL and mounts storage.
  - postgres owns structured data only.
- Use root `storage/` as default host path and `/app/storage` as backend/worker container path.
- Use buildable placeholder containers for `backend`, `cv-worker`, and `frontend` when Compose defines them with `build:`.
  - Placeholder Dockerfiles/commands must be enough for `docker compose up --build` to start a minimal baseline.
  - Placeholders must not add product routes, UI, database schema, worker queue behavior, CV processing, auth, migrations, or training logic.
- Use optional `docker-compose.gpu.yml` for GPU configuration or equivalent GPU-only override for `cv-worker` only.
- Use helper script and/or `Makefile` target for storage directory creation; helper must create only empty required directories.
- Keep Dockerfiles and entrypoints minimal placeholders if needed for `docker compose config` and basic container buildability; no product logic.

## Backend Impact

- Backend touched only for placeholder runtime/build files if needed by Compose.
- No `/api` routes, auth, upload, health, database model, migration, seed, or application logic in Phase 1.

## Frontend Impact

- Frontend touched only for placeholder runtime/build files if needed by Compose.
- No React UI, routes, Ukrainian UI text, API client, auth state, or dashboard logic in Phase 1.

## DB Impact

- PostgreSQL service appears in Compose.
- No SQLAlchemy models, Alembic config, migrations, seed data, or schema changes in Phase 1.

## API Impact

- No API contract implementation in Phase 1.
- README may say API is not implemented yet.

## Security/Privacy Impact

- `.env.example` must contain no real secrets.
- `.gitignore` must exclude real `.env` and generated/large storage artifacts.
- Compose and README must not expose real credentials.
- Logs/config examples must not include tokens, JWT secrets, admin password, database password, or sensitive env values beyond placeholders.
- No uploaded file execution or path safety implementation occurs yet; only storage layout and ignore rules are prepared.

## Test Strategy

- Run `docker compose --env-file .env.example config` after Compose exists, or document copying `.env.example` to `.env` before using plain `docker compose config`.
- Run `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config` when GPU override exists.
- Inspect rendered GPU config and verify only `cv-worker` requests GPU access.
- Inspect `.env.example` for placeholder-only secret values.
- Run storage bootstrap helper or `Makefile` target and verify required folders exist.
- Run `git status --short` and verify generated storage contents are not tracked.
- Confirm README describes current scaffold state and unavailable features honestly.
- Commands for backend/frontend/CV tests remain `not available yet` unless scaffolds add real test commands, which Phase 1 should avoid.

## Ambiguities Or Conflicts

- Prompt risk and phase title were placeholders, not concrete values. Design uses `docs/phase.md` as current phase source.
- Docs allow storage bootstrap script or Makefile target; implementation may choose either or both.
- No `WARNING: CONFLICT` found.
