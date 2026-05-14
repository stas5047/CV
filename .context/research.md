# Research - Phase 16 CV model loading, device selection, and model cache

## Current Phase

- Current phase from `docs/phase.md`: `Phase 16 - CV model loading, device selection, and model cache`.
- Direction: CV Worker / CV Runtime.
- Prompt risk value: not provided; literal placeholder received.
- Assumption: risk is `MEDIUM` because phase touches worker model loading, model artifact paths, job failure behavior, and runtime device selection.

## Docs Consulted

Required first reads:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase `Relevant docs:` reads:

- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

Relevant context reads:

- `.context/status.md`
- `.context/review-code-resolution.md`
- `.context/review-plan-resolution.md`

## Confirmed Repository Facts

- `git status --short` returned no output before this contract rewrite.
- `cv/` exists and contains worker package, tests, Dockerfile, `pyproject.toml`, and `index.md`.
- `backend/` exists and contains implemented FastAPI backend, schema, model registry, job creation, and result APIs through prior phases.
- `frontend/` contains placeholder Dockerfile and index only; frontend app is not part of Phase 16.
- `training/` contains `index.md` only; training utilities are not part of Phase 16.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- `backend` and `cv-worker` both mount `./storage:/app/storage`.
- `.env.example` contains `CV_DEVICE`, `ACTIVE_MODEL_ID`, `STORAGE_ROOT`, and `MODELS_ROOT`.
- `cv/pyproject.toml` includes `torch`, `ultralytics`, `opencv-python-headless`, `pandas`, `numpy`, SQLAlchemy, psycopg, Pydantic, pytest, and Ruff.

## Existing Implementation State

Confirmed existing Phase 16 surface:

- `cv/aerovision_worker/device.py` implements `CV_DEVICE` handling for `auto`, `cpu`, and `cuda`; forced CUDA raises `DeviceUnavailableError` when unavailable.
- `cv/aerovision_worker/settings.py` exposes worker settings for `DATABASE_URL`, `STORAGE_ROOT`, `MODELS_ROOT`, `CV_DEVICE`, `ACTIVE_MODEL_ID`, polling, heartbeat, stale timeout, and retry count.
- `cv/aerovision_worker/model_runtime.py` resolves model metadata by documented priority: job `model_version_id`, then active DB model, then `ACTIVE_MODEL_ID` fallback.
- `cv/aerovision_worker/model_runtime.py` resolves relative weights paths safely and fails with stable safe errors for unsafe or missing paths.
- `cv/aerovision_worker/model_runtime.py` lazy-loads Ultralytics `YOLO`, applies selected device through `.to(device)` when supported, and caches loaded models by model ID plus device.
- `cv/aerovision_worker/main.py` logs selected device on startup, loads model after job claim, fails job safely on model-loading errors, and then keeps later-phase processing as placeholder failure.
- `cv/aerovision_worker/queue.py` already supports PostgreSQL queue claiming, heartbeat, stale recovery, and job failure helper.
- `cv/tests/test_device.py`, `cv/tests/test_model_runtime.py`, and `cv/tests/test_startup.py` cover Phase 16 behavior including device selection, model priority, path safety, missing weights, cache behavior, YOLO family metadata pass-through, and safe logs.
- `.context/status.md` says Phase 16 implementation and code-review final fix are complete, with CV worker gates passed.

Confirmed later-phase gaps:

- Inference, tracking, annotated media, detection rows, track summaries, CSV/JSON exports, and successful job completion are not implemented in this phase.
- `run_poll_iteration` still fails a claimed job with `Processing not implemented in this phase` after successful model preflight.

## Unknowns and Assumptions

Confirmed unknowns:

- Actual local YOLO26 weights are not confirmed present under `storage/models/`.
- Actual Ultralytics package support for YOLO26 in this environment is not confirmed by this research pass.
- CUDA availability on current machine/container is not confirmed.
- Real model loading with real `.pt` artifacts has not been verified in this planning-only turn.
- PostgreSQL-backed model loading against full migrated schema was not re-run in this planning-only turn.
- `python -m aerovision_worker.main --check-once` can mutate queued jobs; it was not run in this planning-only turn and must be limited to isolated/disposable state or an empty queue.

Assumptions:

- Phase 16 remains current because `docs/phase.md` names it, even though existing `.context/status.md` marks implementation complete.
- Any future implementation pass should be verification-first and only patch documented Phase 16 gaps if checks reveal drift.
- `MODELS_ROOT` support for bare model paths remains compatibility behavior; documented `models/...` paths resolve under `STORAGE_ROOT`.
- If a documented local `.pt` artifact exists, implementation verification should include real Ultralytics model-load smoke; otherwise report `not available yet` with missing artifact reason.

## Files Likely Relevant for Implementation

Worker source:

- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/device.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/logging.py`

Worker tests:

- `cv/tests/test_device.py`
- `cv/tests/test_model_runtime.py`
- `cv/tests/test_startup.py`
- `cv/tests/test_storage_paths.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_queue_postgres.py`

Backend references, read-only unless a verified Phase 16 contract mismatch is found:

- `backend/app/services/jobs.py`
- `backend/app/services/models.py`
- `backend/app/db/models.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_models_api.py`

Docs/index references, update only if commands or file inventory change:

- `cv/index.md`
- `docs/index.md`
