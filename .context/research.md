# Phase 32 Research

## Current phase

Confirmed current phase from `docs/phase.md`:

- `Phase 32 - Final Docker runtime, GPU override, README, and first-launch flow`
- Direction: DevOps / Documentation
- Goal: make complete application launchable and understandable from clean local setup.

Risk level:

- Assumption: HIGH. User left risk placeholder unfilled; Phase 32 touches full Docker runtime, env, startup, health, and launch docs.

## Docs consulted

Required first-read docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase 32 relevant docs:

- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`

Implementation docs consulted under phase field `all implementation docs`:

- `README.md`
- `backend/index.md`
- `frontend/index.md`
- `cv/index.md`
- `training/index.md`
- `training/README.md`
- `prototype/index.md`

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before writing context files showed modified existing context files, modified review/status context files, and modified `docs/phase.md`.
- `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/status.md`, and several review context files existed and were zero bytes.
- Repository root contains `backend/`, `frontend/`, `cv/`, `training/`, `prototype/`, `scripts/`, `storage/`, `docs/`, `docker-compose.yml`, `docker-compose.gpu.yml`, `Makefile`, `.env.example`, `README.md`.
- `storage/` contains required folders: `uploads/`, `results/`, `reports/`, `models/`, `temp/`, `datasets/`.
- `.gitignore` excludes `.env`, generated storage subtrees, Node/Python build artifacts, and large model/video artifact patterns.
- `.env.example` contains safe placeholder values for database, auth, storage, backend, CV, worker, and local ports.
- `docker compose --env-file .env.example config` succeeded.
- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config` succeeded.
- Base Compose defines services `postgres`, `backend`, `cv-worker`, and `frontend`.
- Base Compose mounts `./storage:/app/storage` for both `backend` and `cv-worker`.
- Base Compose has a PostgreSQL healthcheck.
- Base Compose does not publish a frontend port.
- Base Compose passes `VITE_API_BASE_URL` to the frontend service as runtime environment, but current frontend Dockerfile is still a placeholder and does not run the Vite app.
- GPU Compose override sets `CV_DEVICE=cuda` and requests GPU devices only for `cv-worker`.
- `Makefile` currently has only `storage-bootstrap`, `compose-config`, and `compose-config-gpu`.

## Existing implementation state

Backend:

- `backend/Dockerfile` builds Python backend image and runs `backend/startup.sh`.
- `backend/startup.sh` optionally runs `alembic upgrade head` and `python -m app.setup` before Uvicorn.
- Backend has `/api/health` and `/api/health/db`.
- Backend settings include `RUN_MIGRATIONS_ON_START`, `RUN_SEED_ON_START`, CORS validation, upload limits, storage roots, and auth env.

CV worker:

- `cv/Dockerfile` builds worker image and runs `python -m aerovision_worker.main`.
- Worker startup logs safe settings payload and selected device.
- Worker uses `wait_for_database(... attempts=30, delay_seconds=1)` during startup.
- Worker has `--check-once` startup smoke mode.

Frontend:

- `frontend/` contains Vite React TypeScript app files, tests, Tailwind/shadcn config, and API client.
- `frontend/package.json` has `dev`, `build`, `lint`, `test`, and `test:watch`; no `preview` script.
- `frontend/src/api/client.ts` defaults API base URL to `http://localhost:8000/api` and reads `VITE_API_BASE_URL`.
- `frontend/Dockerfile` is still a Phase 1 placeholder that prints a message and tails forever.

Training:

- Training docs and utilities define offline model artifacts under `storage/models/<model>/` and report artifacts under `storage/reports/<model>/`.
- Artifact registration helper expects relative model/report paths and admin JWT supplied outside command history when possible.

WARNING: CONFLICT

- `README.md` says React/Vite frontend UI and frontend tests/build are not available yet.
- `README.md` says CV model loading, worker queue polling/claiming, inference, tracking, and exports are not available yet.
- `cv/index.md` says worker queue claiming, model runtime, image/video processing, tracking, exports, summaries, and no-detection completion are implemented.
- `frontend/index.md` says Phase 31 frontend app, routes, tests, and build commands exist.
- `docs/index.md` current implementation state says frontend contains Phase 24 scaffold and placeholder routes, while `frontend/index.md` says Phase 31 feature pages exist.
- Implementation should resolve all current implementation-doc state conflicts found in `README.md`, component indexes, and `docs/index.md` during Phase 32 docs updates without changing canonical product behavior.

## Unknowns and assumptions

Unknowns:

- Whether local Docker daemon will successfully build and start all images on target machine.
- Whether required model weights exist under `storage/models/` for real processing demos.
- Whether GPU host has NVIDIA container runtime configured.
- Whether Make is expected to run through GNU Make on Windows, Git Bash, WSL, or another shell.
- Whether frontend should be served by Vite preview or another static server inside the existing `frontend` service.

Assumptions:

- `all implementation docs` means README plus component index/readme files, not canonical product docs beyond phase-listed sources.
- Phase 32 may update README and implementation index docs when commands/runtime status change.
- No new runtime service should be added; optional reverse proxy remains unnecessary.
- Frontend Docker runtime should use existing Vite app and existing `frontend` service.
- CPU launch is mandatory; GPU launch is optional and must affect only `cv-worker`.

## Files likely relevant for implementation

Runtime and env:

- `docker-compose.yml`
- `docker-compose.gpu.yml`
- `.env.example`
- `Makefile`
- `scripts/bootstrap-storage.ps1`

Backend runtime:

- `backend/Dockerfile`
- `backend/startup.sh`
- `backend/app/api/health.py`
- `backend/app/core/config.py`

Worker runtime:

- `cv/Dockerfile`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/settings.py`

Frontend runtime:

- `frontend/Dockerfile`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/vite.config.ts`
- `frontend/src/api/client.ts`

Implementation docs likely needing update in implementation phase:

- `README.md`
- `frontend/index.md`
- `backend/index.md` only if backend commands/runtime change.
- `cv/index.md` only if worker commands/runtime change.
- `training/index.md` or `training/README.md` only if artifact commands change.
- `docs/index.md` only if current-state/index entries become inaccurate under project workflow rules.
