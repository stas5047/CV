# Plan - Phase 16 CV model loading, device selection, and model cache

## Scope

Phase only: CV worker model selection, model loading, device selection, model cache, and safe failure behavior.

Do not add inference, tracking, exports, result writes, frontend UI, backend API routes, database migrations, training launch, Celery, Redis, RTSP/live camera, or any CV output beyond model preflight state.

## Ordered Atomic Steps

1. `@role/developer-cv-worker` Re-read Phase 16 docs before source edits.
   - Verify `docs/phase.md` still names Phase 16.
   - Verify `Relevant docs:` still match this contract.
   - Verifiable: notes match `.context/research.md`.

2. `@role/developer-cv-worker` Inspect current worker model/device implementation.
   - Read `cv/aerovision_worker/device.py`, `settings.py`, `model_runtime.py`, `main.py`, `queue.py`, and `storage_paths.py`.
   - Verifiable: list confirmed implemented behaviors and any missing Phase 16 requirements before editing.

3. `@role/developer-cv-worker` Confirm no backend/API/schema work is required.
   - Read only `backend/app/services/jobs.py`, `backend/app/services/models.py`, and `backend/app/db/models.py` if model resolution or path validation looks inconsistent.
   - Verifiable: either "no backend change" or exact doc-backed mismatch.

4. `@role/developer-cv-worker` If model priority is missing or regressed, fix worker metadata resolution only.
   - Required priority: job `model_version_id`, active DB model, then `ACTIVE_MODEL_ID` only when no active DB model exists.
   - Verifiable: `cv/tests/test_model_runtime.py` has passing tests for all three priority levels and override prevention.

5. `@role/developer-cv-worker` If weights path handling is missing or regressed, fix path resolution only.
   - Documented `models/...` paths resolve under `STORAGE_ROOT`.
   - Bare compatibility paths resolve under `MODELS_ROOT`.
   - Unsafe, absolute, drive, traversal, or missing paths fail with safe `ModelLoadingError`.
   - Verifiable: tests cover no `models/models/...`, unsafe path rejection, and missing file safe message.
   - Verifiable: test names clearly separate documented `models/...` under `STORAGE_ROOT` from bare compatibility paths under `MODELS_ROOT`.

6. `@role/developer-cv-worker` If device handling is missing or regressed, fix device selection only.
   - `auto`: CUDA if available else CPU.
   - `cpu`: CPU.
   - `cuda`: clear failure if CUDA unavailable.
   - Verifiable: `cv/tests/test_device.py` passes.

7. `@role/developer-cv-worker` If model loading/cache is missing or regressed, fix `ModelRuntime` only.
   - Lazy-load Ultralytics `YOLO`.
   - Apply selected device with model `.to(device)` when supported.
   - Cache by `(model_id, selected_device)`.
   - Preserve `model_family` metadata without silent YOLO11 substitution.
   - Verifiable: cache/device/metadata tests pass.

8. `@role/developer-cv-worker` If poll integration is missing or regressed, fix worker polling only.
   - After claim, run model preflight.
   - On model-load error, mark job `failed` with safe error.
   - After successful preflight, keep existing later-phase placeholder failure.
   - Verifiable: startup/poll tests prove load-before-placeholder and missing-model failure behavior.

9. `@role/developer-cv-worker` Review logs and stored errors.
   - Confirm logs include selected device and model ID/family/variant/device.
   - Confirm logs/errors omit absolute storage paths and secrets.
   - Verifiable: `caplog` tests check no storage root in model logs and startup logs.
   - Verifiable: tests/assertions cover absence of `STORAGE_ROOT`, `MODELS_ROOT`, database URLs, and env-derived secret values in model-load logs and stored job errors.

10. `@role/tester` Run targeted worker gates.
    - Command: `python -m pytest tests/test_device.py tests/test_storage_paths.py tests/test_model_runtime.py tests/test_startup.py`
    - Working directory: `cv/`
    - Expected: `PASS`.

11. `@role/tester` Run worker regression gates.
    - Command: `python -m pytest`
    - Working directory: `cv/`
    - Expected: `PASS`.
    - Command: `python -m ruff check .`
    - Working directory: `cv/`
    - Expected: `PASS`.

12. `@role/tester` Run environment-dependent checks only when prerequisites exist.
   - Command: `python -m pytest -m postgres`
   - Working directory: `cv/`
   - Expected when PostgreSQL reachable: `PASS`; otherwise report `not available yet`.
   - Command: `python -m aerovision_worker.main --check-once`
   - Working directory: `cv/`
   - Preconditions: run only against isolated disposable DB/test data, or after verifying queue is empty. Do not run against non-isolated configured DB with real queued jobs because Phase 16 placeholder can fail a successfully preflighted job.
   - Expected when safe preconditions exist: selected device logged and DB check passes; if a queued test job exists, expected mutation is claim then safe Phase 16 placeholder failure. Otherwise report `not available yet` with missing precondition.
   - Command: real Ultralytics model-load smoke using a documented local `.pt` artifact path.
   - Working directory: `cv/`
   - Expected when a documented local weights artifact exists: worker loads model from relative path and cache/device path succeeds; otherwise report `not available yet` with missing artifact reason.

13. `@role/code-reviewer` Perform Phase 16 scope review.
    - Check changed files against `docs/CV_PIPELINE.md`, `docs/TRAINING_EXPERIMENTS.md`, `docs/DATA_MODEL.md`, `docs/ARCHITECTURE.md`, and `docs/TESTING_QA.md`.
    - Verifiable: no backend API/schema/frontend/training/inference/tracking/export scope creep.

14. `@role/docs-maintainer` Update indexes only if file inventory or commands changed.
    - Candidate: `cv/index.md`.
    - Do not update product docs unless source-of-truth paths/commands changed and user authorizes doc work.
    - Verifiable: either exact index update or "skipped; no command/file inventory change".

15. `@role/tester` Final allowed-change check.
    - Command: `git status --short`
    - Expected: only Phase 16 source/tests/index/context files changed during implementation.
    - In this planning-only turn, expected changed files are only `.context/research.md`, `.context/design.md`, and `.context/plan.md`.
