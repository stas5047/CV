# Phase 33 Research

## Current Phase

- Phase: `Phase 33 - Final full-stack QA, security audit, and release readiness`
- Direction: QA / Release
- Goal: verify complete MVP against documented acceptance criteria.
- Risk: not explicitly supplied by user; assumed `HIGH` because phase spans Docker runtime, backend, CV worker, frontend, training artifacts, security, and manual E2E.

## Docs Consulted

Required first:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase 33 `Relevant docs`:

- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/FRONTEND_UX.md`
- `docs/DATA_MODEL.md` as implementation/data contract doc
- `docs/TRAINING_EXPERIMENTS.md` as implementation/training contract doc
- `README.md`
- `backend/index.md`
- `cv/index.md`
- `frontend/index.md`
- `training/index.md`
- `prototype/index.md`

Context artifacts checked:

- `.context/status.md`
- `.context/review-plan-resolution.md`
- `.context/review-plan-claude.md`
- `.context/review-code-resolution.md`
- `.context/review-code-claude.md`
- `.context/review-code-openai.md`

## Confirmed Repository Facts

- Git worktree exists.
- `git status --short` showed modified `.context/*.md` files and `docs/phase.md` before this contract was written.
- `.context/research.md`, `.context/design.md`, `.context/plan.md`, and other `.context` review/status files were empty at read time.
- Root contains expected main areas: `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `prototype/`, `scripts/`, `storage/`.
- Root runtime files exist: `docker-compose.yml`, `docker-compose.gpu.yml`, `.env.example`, `Makefile`, `README.md`, `.gitignore`.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- Backend and CV worker both mount `./storage:/app/storage`.
- GPU override file exists and should be checked for GPU isolation to `cv-worker`.
- `.env.example` contains safe placeholder-looking values, not real credentials by inspection.
- `.gitignore` excludes `.env`, generated storage subfolders, Python caches, Node artifacts, and model/video artifacts.
- `Makefile` exposes setup, Compose config, build/up/down/logs, migration, seed, and test targets.
- `README.md` documents current setup, Docker launch, CPU/GPU mode, storage policy, commands, model registration, experiment import, API notes, and troubleshooting.

## Existing Implementation State

Confirmed from docs/index and component indexes:

- Backend has FastAPI foundation, settings, logging, CORS, database connectivity, SQLAlchemy/Alembic schema, startup migration/seed, auth, security helpers, media/model/job/result/admin/experiment APIs, downloads, API contract checks, and tests.
- CV worker has settings, logging, device selection, database/storage helpers, queue claiming, stale recovery, model runtime, image/video processing, tracking/export/result-writing behavior, Docker entrypoint, and tests.
- Frontend has Vite React TypeScript app with Tailwind/shadcn baseline, routes `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, `/admin`, typed API clients, auth/admin guards, Ukrainian UX polish, tests, and Dockerfile.
- Training area has offline dataset preparation, notebook templates, model-card/metrics templates, validators, backend registration/import helpers, smoke training entry point, and tests.
- Prototype area is static reference only, not production runtime.

## Unknowns And Assumptions

- Unknown: whether local dependencies are installed in `.venv`, `backend`, `cv`, `frontend`, and `training`.
- Unknown: whether Docker daemon is available and whether host ports are free.
- Unknown: whether a real `.env` exists; `.env` is ignored and was not read.
- Unknown: whether required trained model weights exist under `storage/models/`; generated storage contents are ignored.
- Unknown: whether GPU runtime is configured; base CPU mode must be enough for release readiness.
- Unknown: whether manual E2E media fixtures exist. Assumption: use tiny safe local media fixtures or create temporary test media under ignored storage/temp during implementation if needed.
- Assumption: Phase 33 may update README/known limitations only if QA proves current instructions are wrong or incomplete.
- Assumption: source fixes during implementation chat are allowed only for doc-backed defects found by Phase 33 gates; ambiguous product behavior needs user decision.

## Files Likely Relevant For Implementation

QA and contract files:

- `.context/status.md`
- `.context/review-code-resolution.md`
- `README.md`
- `docs/phase.md`

Runtime/devops:

- `docker-compose.yml`
- `docker-compose.gpu.yml`
- `.env.example`
- `Makefile`
- `scripts/bootstrap-storage.ps1`

Backend:

- `backend/pyproject.toml`
- `backend/app/`
- `backend/tests/`
- `backend/migrations/`
- `backend/startup.sh`

CV worker:

- `cv/pyproject.toml`
- `cv/aerovision_worker/`
- `cv/tests/`

Frontend:

- `frontend/package.json`
- `frontend/src/`
- `frontend/src/test/`
- `frontend/Dockerfile`

Training:

- `training/pyproject.toml`
- `training/aerovision_training/`
- `training/templates/`
- `training/tests/`

## Conflicts

- No doc conflict confirmed during planning.

## Planning Review Resolution Findings

- `README.md` and `docs/ARCHITECTURE.md` require first-launch runtime smoke to use a configured `.env`, not `.env.example`. `.env.example` remains valid for config/build validation only.
- `.env` must not be read, logged, copied into committed artifacts, or summarized. If no local `.env` exists during Phase 33 implementation, runtime launch/admin-seed smoke is a blocker or `not available`, not a reason to commit a generated env file.
- Clean-volume smoke should use an isolated Compose project name so Phase 33 gets a fresh PostgreSQL named volume and can later remove only that isolated project/volume. Do not run destructive `down -v` against the default project or unknown user projects.
- Upload validation QA must cover unsupported extensions, invalid MIME types, oversized image and video files, unsafe filenames, path traversal, and user-submitted storage-path attempts.
- Frontend/manual E2E must click or otherwise verify job-detail download actions for annotated media, CSV, and JSON when completed artifacts exist.
- Dependency/setup preflight should distinguish missing local toolchains from product failures before running component gates.
