# Phase 16 Research

## Current Phase

- Confirmed: `docs/phase.md` sets current phase to `Phase 16 - CV model loading, device selection, and model cache`.
- Confirmed phase direction: CV Worker / CV Runtime.
- Confirmed phase goal: implement model selection, model loading, device selection, cache, and safe fallback/error behavior.
- Assumption: user-supplied phase/risk placeholders are unresolved. Treat phase risk as `MEDIUM` because worker runtime will load external model artifacts and mark jobs failed on missing/unusable weights.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

## Confirmed Repository Facts

- `git status --short` reports existing modified files:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Existing `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/status.md`, `.context/review-plan-claude.md`, `.context/review-plan-resolution.md`, and `.context/review-code-resolution.md` were empty when read.
- `cv/pyproject.toml` already includes `torch`, `ultralytics`, `opencv-python-headless`, `numpy`, `pandas`, SQLAlchemy, psycopg, Pydantic, pytest, and Ruff.
- `cv/aerovision_worker/settings.py` defines `DATABASE_URL`, `STORAGE_ROOT`, `MODELS_ROOT`, `CV_DEVICE`, `ACTIVE_MODEL_ID`, worker polling, heartbeat, stale-job, and retry settings.
- `cv/aerovision_worker/device.py` already implements `CV_DEVICE` behavior for `auto`, `cpu`, and `cuda`, including clear failure for forced CUDA when unavailable.
- `cv/aerovision_worker/storage_paths.py` already validates relative storage paths and safe joins under a configured root.
- `cv/aerovision_worker/database.py` already creates SQLAlchemy engines/session factories and database readiness checks.
- `cv/aerovision_worker/queue.py` already claims queued jobs, updates heartbeat, recovers stale jobs, and fails claimed jobs with a Phase 15 placeholder message.
- `cv/aerovision_worker/main.py` already logs selected device during startup and fails claimed jobs with placeholder processing.
- `backend/app/db/models.py` already contains `processing_jobs.model_version_id`, `model_versions.weights_path`, `model_versions.model_family`, and relative-path checks.
- `backend/app/services/jobs.py` already resolves job model priority during job creation: explicit model, active DB model, then `ACTIVE_MODEL_ID` fallback.

## Existing Implementation State

- Worker foundation exists.
- Queue claiming exists with PostgreSQL `FOR UPDATE SKIP LOCKED` when using PostgreSQL.
- Device selection exists and has tests.
- Storage path safety exists and has tests.
- Worker startup logging redacts database URLs, secrets, tokens, and absolute paths.
- Model loading does not exist yet.
- Model cache does not exist yet.
- Worker does not yet read the claimed job's resolved `model_version_id`.
- Worker does not yet load `model_versions.weights_path`.
- Worker does not yet check missing model weights and fail jobs with model-specific safe errors.
- Worker still fails every claimed job with `Processing not implemented in this phase`.
- Inference, tracking, exports, detection writes, and result writes remain later-phase work.

## Unknowns And Assumptions

- Unknown: no actual model artifact is present or guaranteed under `storage/models/`.
- Unknown: exact Ultralytics package support for YOLO26 in the local runtime is not proven in this phase.
- Assumption: Phase 16 should not run inference; it should only prove model resolution/loading/cache behavior and safe failure.
- Assumption: worker should use the `processing_jobs.model_version_id` already resolved by backend job creation and should not re-apply backend model priority unless a legacy/unexpected job has no model version.
- Assumption: a missing `processing_jobs.model_version_id` can be handled by querying active DB model, then `ACTIVE_MODEL_ID`, to keep worker robust and consistent with documented priority.
- Assumption: model loading logs may include model IDs/family/variant but must not expose absolute storage paths.
- Assumption: YOLO11 fallback may be loaded only if DB metadata says `model_family = YOLO11`; worker must not silently relabel or substitute YOLO11 for YOLO26.
- Assumption: tests should mock Ultralytics model construction rather than require real model weights.
- Resolved after planning review: documented `model_versions.weights_path` values like `models/{model_version_id}/weights.pt` are primary and resolve relative to `STORAGE_ROOT`; bare values under `MODELS_ROOT` are compatibility behavior only.
- Resolved after planning review: phase risk is `MEDIUM`; no user decision needed.

## Files Likely Relevant For Implementation

- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/device.py`
- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/database.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/logging.py`
- `cv/aerovision_worker/` internal model-loading/cache module to add during implementation
- `cv/tests/test_device.py`
- `cv/tests/test_storage_paths.py`
- `cv/tests/test_startup.py`
- `cv/tests/` model-loading/cache tests to add during implementation
- `backend/app/db/models.py` for schema shape reference only
- `backend/app/services/jobs.py` for confirmed model-priority behavior reference only

## Conflict Check

- No `WARNING: CONFLICT` found between phase docs and inspected implementation.
- Existing code default `cv_device = "cpu"` differs from docs describing `auto` behavior, but docs do not require the default value for `CV_DEVICE`; no conflict recorded.
