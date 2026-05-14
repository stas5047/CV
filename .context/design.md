# Design - Phase 16 CV model loading, device selection, and model cache

## Phase Goal

Implement and verify CV worker model selection, model loading, runtime device selection, in-memory model cache, and safe fallback/error behavior for `Phase 16 - CV model loading, device selection, and model cache`.

## Intended Behavior from Docs

Confirmed doc requirements:

- Worker uses resolved `processing_jobs.model_version_id` when present.
- If job has no model version, worker uses active `model_versions.is_active = true`.
- `ACTIVE_MODEL_ID` is only fallback when no active DB model exists.
- `ACTIVE_MODEL_ID` must not override job-specific or database-active model selection.
- Model weights paths are relative storage paths; absolute host/container paths must not be stored or logged.
- Documented model path examples are under `models/...` relative to `STORAGE_ROOT`.
- YOLO26 is primary model family.
- YOLO11 is fallback only after YOLO26 unavailability is reported and documented; runtime must preserve actual `model_family` metadata.
- `CV_DEVICE=auto` uses CUDA when available and CPU otherwise.
- `CV_DEVICE=cpu` forces CPU.
- `CV_DEVICE=cuda` fails clearly when CUDA is unavailable.
- Worker logs selected runtime device.
- Worker logs model loading events without secrets or unsafe paths.
- Missing model weights fail the claimed job safely with a clear error message.
- CPU inference must remain possible.
- Phase 16 must not implement image/video inference, tracking, exports, result writes, frontend behavior, backend API changes, schema changes, or training launch.

## Architecture Decisions

- Keep model-runtime logic inside `cv/aerovision_worker/model_runtime.py`; worker owns loading/cache, backend owns job creation and model registry APIs.
- Keep device selection isolated in `cv/aerovision_worker/device.py`; startup selects once and passes selected device into `ModelRuntime`.
- Keep model cache in memory per worker process, keyed by `(model_id, selected_device)`.
- Resolve documented `models/...` paths from `STORAGE_ROOT`; support bare paths relative to `MODELS_ROOT` only as compatibility.
- Keep errors stable and safe: user/API-visible job error strings must not include absolute paths, DB URLs, tokens, passwords, or stack traces.
- Preserve later-phase placeholder after model preflight until media processing phases implement inference/tracking/export/result writes.

## Backend Impact

- No backend source change intended for Phase 16 if existing job creation/model registry behavior matches docs.
- Backend remains source of truth for resolving and storing `processing_jobs.model_version_id` during job creation.
- Backend model registry still validates relative model weights paths before registration/activation.

## Frontend Impact

- None for this phase.

## DB Impact

- No schema or migration change intended.
- Worker reads existing `processing_jobs.model_version_id`, `model_versions.is_active`, and `model_versions.weights_path`.
- Worker writes only safe failure state if model loading fails.

## API Impact

- No API route or response contract change intended.
- Any failed job error from missing/unloadable model must remain safe for later backend result display.

## Security/Privacy Impact

- Must reject unsafe model weights paths including absolute paths, drive paths, traversal, and escaped storage roots.
- Must not log absolute storage paths, DB passwords, JWT secrets, tokens, admin password, raw environment values, or model file contents.
- Must preserve CV-only boundary: model metadata and runtime device only; no targeting, navigation, geospatial, hardware-control, or engagement output.

## Test Strategy

Relevant automated checks:

- `python -m pytest tests/test_device.py` from `cv/`: device selection contract.
- `python -m pytest tests/test_storage_paths.py` from `cv/`: relative path safety helper.
- `python -m pytest tests/test_model_runtime.py` from `cv/`: model priority, path resolution, missing weights, cache, metadata, and log safety.
- `python -m pytest tests/test_startup.py` from `cv/`: startup device logging and poll integration with model preflight.
- `python -m pytest` from `cv/`: worker regression suite because model loading is wired into queue polling.
- `python -m ruff check .` from `cv/`: worker lint gate.

Optional environment-dependent checks:

- `python -m pytest -m postgres` from `cv/` when PostgreSQL is reachable.
- `python -m aerovision_worker.main --check-once` from `cv/` only against an isolated disposable database/test queue, or after verifying the queue is empty. Do not run it against a non-isolated configured database with real queued jobs because a successfully preflighted job still reaches the Phase 16 placeholder failure.
- Real Ultralytics model-load smoke with a documented local `.pt` artifact when present; otherwise report `not available yet` with the missing artifact reason.

Additional validation expectations:

- Tests should assert model-loading logs and stored job errors omit `STORAGE_ROOT`, `MODELS_ROOT`, database URLs, and env-derived secret values.
- Test names should distinguish documented `models/...` paths under `STORAGE_ROOT` from bare compatibility paths under `MODELS_ROOT`.

## Ambiguities or Conflicts

- No `WARNING: CONFLICT` found between Phase 16 docs and existing code during this research pass.
- Prompt phase title and risk were placeholders; current phase taken from `docs/phase.md`, risk assumed `MEDIUM`.
- Existing `.context/status.md` reports Phase 16 already implemented and reviewed. This is state information, not a product-doc conflict.
- Actual YOLO26 availability and actual weights presence remain environment unknowns; plan must not silently switch to YOLO11.
- `--check-once` is mutation-capable when queued jobs exist; run it only with isolated/disposable state or empty queue preconditions.
