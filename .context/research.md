# Research - Phase 14

## Current phase

- Confirmed from `docs/phase.md`: Phase 14 - CV worker scaffold, settings, logging, and database access.
- Direction: CV Worker.
- Goal: create separate worker service foundation without full inference.
- User-provided risk level: unspecified placeholder. Assumption for planning only: medium, because worker touches database, shared storage path safety, Docker runtime, and secret-safe logging.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase relevant docs:
  - `docs/ARCHITECTURE.md`
  - `docs/CV_PIPELINE.md`
  - `docs/DATA_MODEL.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/TESTING_QA.md`
- Existing context artifacts:
  - `.context/research.md`
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/status.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
- Existing context files above were zero-byte at read time.

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before writing showed modified files:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Root runtime files exist:
  - `docker-compose.yml`
  - `docker-compose.gpu.yml`
  - `.env.example`
  - `Makefile`
  - `README.md`
- `docker-compose.yml` already defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- `cv-worker` already receives worker env vars:
  - `DATABASE_URL`
  - `STORAGE_ROOT`
  - `MODELS_ROOT`
  - `CV_DEVICE`
  - `ACTIVE_MODEL_ID`
  - `WORKER_POLL_INTERVAL_SECONDS`
  - `WORKER_HEARTBEAT_FRAMES`
  - `WORKER_HEARTBEAT_SECONDS`
  - `WORKER_STALE_JOB_MINUTES`
  - `WORKER_MAX_RETRIES`
- Backend and worker both mount `./storage:/app/storage`.
- GPU override requests GPU only for `cv-worker`.
- `.env.example` contains safe placeholders and worker defaults:
  - `CV_DEVICE=cpu`
  - `WORKER_POLL_INTERVAL_SECONDS=2`
  - `WORKER_HEARTBEAT_FRAMES=30`
  - `WORKER_HEARTBEAT_SECONDS=2`
  - `WORKER_STALE_JOB_MINUTES=10`
  - `WORKER_MAX_RETRIES=2`
- `cv/index.md` says no CV worker scaffold, dependency manifest, application package, model-loading code, processing code, or tests exist yet.
- `cv/Dockerfile` is Phase 1 placeholder. It runs an infinite Python command and prints `CV_DEVICE`.
- Backend is implemented through Phase 13 per `README.md` and `backend/index.md`.
- Backend ORM models include documented tables needed by worker:
  - `ProcessingJob`
  - `MediaFile`
  - `Detection`
  - `Track`
  - `ModelVersion`
- Backend has storage path helpers in `backend/app/core/storage_paths.py`, but there is no shared package for worker reuse.
- Backend has safe logging helper in `backend/app/core/logging.py`, but there is no shared package for worker reuse.
- Backend dependency manifest includes `sqlalchemy`, `psycopg[binary]`, `pydantic-settings`, `opencv-python-headless`, and tests/lint tooling for backend only.

## Existing implementation state

- CV worker:
  - Placeholder Dockerfile only.
  - No `cv/pyproject.toml`.
  - No worker Python package.
  - No worker settings.
  - No worker logging module.
  - No worker database session layer.
  - No worker storage path resolver.
  - No worker startup command beyond placeholder.
  - No worker tests.
- Docker:
  - Compose env and storage mounts already mostly match Phase 14 needs.
  - Worker image build context is `./cv`.
  - Worker container currently does not install dependencies or run actual worker code.
- Database:
  - Backend migrations/schema exist.
  - Worker can target same PostgreSQL schema, but no worker-side model/session code exists.
- Current context files:
  - `.context/research.md`, `.context/design.md`, `.context/plan.md` were empty before this contract.

## Unknowns and assumptions

- Unknown: exact user-intended risk level because prompt kept placeholder.
- Unknown: whether implementation should duplicate minimal ORM mappings in `cv/` or import backend models by changing Python path. Assumption: keep worker independent; avoid importing backend app internals unless implementation verifies that is clean and does not blur service boundaries.
- Unknown: whether full PyTorch/Ultralytics install is acceptable during this phase on local machines. Phase requires placeholder dependencies, so implementation should add them in worker manifest, while tests can avoid loading real models.
- Unknown: whether worker startup should block forever after startup smoke or run a no-op loop. Assumption: Phase 14 may start a worker process that initializes settings/logging/database and idles without claiming jobs or running inference.
- Unknown: exact worker package/module names are not specified by product docs. Implementation may choose small internal file names under `cv/` as scaffold details.
- Assumption: no new REST endpoints are needed in Phase 14.
- Assumption: no backend schema changes are needed in Phase 14.
- Assumption: no frontend changes are needed in Phase 14.

## Planning review resolution research notes

- Claude planning review treated Phase 14 as medium/high risk because worker startup touches PostgreSQL connectivity, shared-storage path safety, Docker startup, and secret-safe logging. This matches the planning assumption and requires no scope expansion.
- Phase 14 implementation must not treat database connectivity as optional during startup validation. Worker startup needs bounded PostgreSQL readiness retry or equivalent startup-safe connection handling so Compose startup does not race `postgres`.
- `CV_DEVICE=cuda` must follow `docs/CV_PIPELINE.md`: force CUDA and fail clearly when CUDA is unavailable. `CV_DEVICE=auto` may fall back to CPU when CUDA is unavailable.
- PyTorch and Ultralytics dependency risk is accepted as a planning concern only. Tests and startup checks must stay import-safe and must not load real YOLO models in Phase 14.
- Worker production entrypoint may idle after successful startup, but implementation should provide deterministic smoke/test mode that exits after settings, device, and database checks.

## Files likely relevant for implementation

- `cv/Dockerfile`
- `cv/index.md`
- `docker-compose.yml`
- `.env.example`
- `Makefile`
- `README.md`
- New worker scaffold files under `cv/` for:
  - dependency manifest
  - worker settings
  - worker logging
  - database session access
  - storage path resolution
  - startup entrypoint
  - worker tests
- Reference-only backend files:
  - `backend/app/db/models.py`
  - `backend/app/db/session.py`
  - `backend/app/core/config.py`
  - `backend/app/core/storage_paths.py`
  - `backend/app/core/logging.py`
