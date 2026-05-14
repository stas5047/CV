# Phase 16 Design

## Phase Goal

Implement CV worker model selection, model loading, selected-device use, in-memory cache, and safe missing-weight/device errors for the current phase only.

## Intended Behavior From Docs

Confirmed facts:

- Worker processes the resolved model version stored on `processing_jobs.model_version_id`.
- Model selection priority is job-specific model, then active DB model, then `ACTIVE_MODEL_ID` only when no DB active model exists.
- Model weights paths are relative storage paths only.
- Worker loads YOLO models only when needed.
- Worker caches the active/selected model when practical and switches/reloads when a different job requires a different model.
- `CV_DEVICE=auto` uses CUDA when available, otherwise CPU.
- `CV_DEVICE=cpu` forces CPU.
- `CV_DEVICE=cuda` fails clearly when CUDA is unavailable.
- CPU inference must remain possible.
- Missing weights should fail the job safely with a clear `error_message`.
- YOLO26 remains primary. YOLO11 is allowed only when fallback is documented and reflected in model metadata.
- Logs may report selected runtime device and model loading events, but must not leak secrets or unsafe absolute paths.

Assumptions:

- Phase 16 should load a model but not run image/video inference, tracking, export generation, or result writes.
- Phase 16 can replace the placeholder job failure with a model-loading preflight path: claim job, resolve/load model, then fail with the existing processing-placeholder message until processing phases exist.
- Tests should mock Ultralytics `YOLO` and use temporary files for weights-path behavior.

## Architecture Decisions

- Add a CV-worker-only model runtime component responsible for:
  - reading the claimed job's `model_version_id`;
  - resolving fallback model metadata only when the job lacks a resolved model;
  - validating relative `weights_path`;
  - resolving documented `models/{model_version_id}/weights.pt` paths relative to `STORAGE_ROOT`;
  - supporting bare model-storage paths such as `{model_version_id}/weights.pt` or `weights.pt` under `MODELS_ROOT` only as compatibility behavior;
  - avoiding double-prefixing paths that already start with `models/`;
  - checking file existence before constructing YOLO;
  - constructing Ultralytics `YOLO` with selected weights;
  - moving/using the selected device when supported by the Ultralytics API;
  - caching loaded model by model version ID plus selected device.
- Keep route/API/backend behavior unchanged.
- Keep DB schema unchanged.
- Keep long processing out of backend requests.
- Keep backend-worker communication through PostgreSQL/shared storage only.
- Keep all model artifacts in filesystem storage, never PostgreSQL.

## Backend Impact

- No backend source changes planned.
- Backend remains source that resolves `processing_jobs.model_version_id` when creating jobs.
- Backend DB model definitions are reference only for worker SQL queries.

## Frontend Impact

- No frontend changes planned.

## DB Impact

- No migration/schema changes planned.
- Worker will read existing `processing_jobs` and `model_versions` fields.
- Worker will update existing `processing_jobs.status`, `error_message`, heartbeat/lock fields through existing queue helpers.

## API Impact

- No API contract changes planned.

## Security/Privacy Impact

- Validate all model weight paths as relative paths.
- Reject missing/unsafe weight paths before model construction.
- Do not log absolute filesystem paths, database URLs, secrets, tokens, or environment values.
- Store only safe job `error_message` text.
- Preserve CV-only boundary: no targeting, navigation, geospatial, or hardware-control output.

## Test Strategy

- Unit-test model path validation with safe relative paths, absolute paths, traversal paths, and missing files.
- Unit-test documented model path behavior:
  - `models/{model_version_id}/weights.pt` resolves under `STORAGE_ROOT`;
  - this documented path must not become `models/models/...`;
  - bare model-storage paths under `MODELS_ROOT` are compatibility behavior only.
- Unit-test model selection priority for:
  - job-specific model ID;
  - DB active model when job model is absent;
  - `ACTIVE_MODEL_ID` only when no active DB model exists;
  - missing fallback model failure.
- Unit-test cache behavior:
  - same model ID and device reuses cached object;
  - different model ID loads a different object;
  - different device loads or applies device selection separately.
- Unit-test `CV_DEVICE` behavior through existing `test_device.py`.
- Unit-test worker poll iteration behavior:
  - claimed job with existing weights attempts model load before placeholder processing failure;
  - missing weights marks job failed with safe error;
  - forced CUDA unavailable still fails clearly before database processing.
- Unit-test safe logging:
  - missing-weight error messages do not include absolute storage paths;
  - model-loading log records do not include absolute storage paths.
- Unit-test YOLO family metadata pass-through:
  - a row with `model_family = YOLO11` can be loaded as metadata states;
  - a row with `model_family = YOLO26` is not silently substituted or relabeled as YOLO11.
- Run focused CV worker tests and Ruff:
  - `python -m pytest tests/test_device.py tests/test_storage_paths.py tests/test_startup.py tests/test_model_runtime.py`
  - `python -m ruff check .`
  - `python -m pytest`

## Ambiguities Or Conflicts

- No `WARNING: CONFLICT` found.
- Resolved path rule: documented `model_versions.weights_path` values such as `models/{model_version_id}/weights.pt` are relative to `STORAGE_ROOT` and are primary. `MODELS_ROOT` may support bare compatibility values, but must not replace or double-prefix documented `models/...` records.
- Ambiguity: YOLO26 availability in Ultralytics is environment-dependent. This phase must not switch to YOLO11 unless DB metadata already says `YOLO11` and prior documentation records fallback.
