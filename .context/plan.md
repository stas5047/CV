# Phase 16 Implementation Plan

## Scope

Only CV worker model selection/loading/cache behavior for `Phase 16 - CV model loading, device selection, and model cache`.

No source implementation done in this planning phase.

## Ordered Atomic Plan

1. `@role/developer-cv-worker` Add focused tests for model metadata resolution.
   - Verify job-specific `processing_jobs.model_version_id` selects that `model_versions` row.
   - Verify absent job model uses active DB model.
   - Verify absent job model and absent active DB model uses `ACTIVE_MODEL_ID`.
   - Verify absent/malformed fallback fails with safe worker error.
   - Verification: new model-runtime test fails before implementation.

2. `@role/developer-cv-worker` Add focused tests for model weights path safety.
   - Verify documented `models/{model_version_id}/weights.pt` resolves under `STORAGE_ROOT`.
   - Verify documented `models/{model_version_id}/weights.pt` is not resolved as `models/models/{model_version_id}/weights.pt`.
   - Verify bare model-storage compatibility paths such as `{model_version_id}/weights.pt` or `weights.pt` resolve under `MODELS_ROOT` only when supported by existing settings.
   - Verify absolute path is rejected.
   - Verify traversal path is rejected.
   - Verify missing weights file raises a safe model-loading error without absolute path in message.
   - Verification: new path tests fail before implementation.

3. `@role/developer-cv-worker` Add focused tests for model metadata and cache behavior.
   - Mock Ultralytics `YOLO`.
   - Verify `model_family = YOLO11` metadata can be loaded only when the database row says YOLO11.
   - Verify `model_family = YOLO26` metadata is not silently relabeled or substituted as YOLO11.
   - Verify same model version and device reuses cached loaded model.
   - Verify different model version loads a separate model.
   - Verify selected device is applied/passed consistently.
   - Verification: new cache tests fail before implementation.

4. `@role/developer-cv-worker` Implement internal model metadata resolution.
   - Read existing `processing_jobs.model_version_id`.
   - Query existing `model_versions` fields: `id`, `name`, `model_family`, `variant`, `weights_path`, `is_active`.
   - Apply documented priority only when job model is absent: active DB model, then `ACTIVE_MODEL_ID`.
   - Do not add schema fields.
   - Verification: model-priority tests pass.

5. `@role/developer-cv-worker` Implement model weights path resolution.
   - Reuse existing relative-path validation from `cv/aerovision_worker/storage_paths.py`.
   - Treat documented `models/{model_version_id}/weights.pt` values as relative to `STORAGE_ROOT`.
   - Do not prepend `MODELS_ROOT` to values that already start with `models/`.
   - Treat bare paths under `MODELS_ROOT` as compatibility behavior only.
   - Reject unsafe paths and missing files with safe error text.
   - Do not store or log absolute paths.
   - Verification: path-safety and missing-weight tests pass.

6. `@role/developer-cv-worker` Implement Ultralytics model loading wrapper.
   - Construct `YOLO` only after path validation and existence check.
   - Preserve model metadata family exactly as stored; no silent YOLO11 substitution.
   - Apply selected device from existing `select_device`.
   - Keep CPU path valid.
   - Verification: mocked YOLO loader tests pass.

7. `@role/developer-cv-worker` Implement in-memory model cache.
   - Cache by model version ID and selected device.
   - Reuse loaded model for repeated jobs with same key.
   - Load a new model when a job requires a different model version or selected device.
   - Verification: cache tests pass.

8. `@role/developer-cv-worker` Wire model preflight into worker poll iteration.
   - After claiming job, resolve and load required model.
   - If model load fails, mark claimed job failed with safe model error.
   - If model load succeeds, keep later-phase placeholder failure for actual media processing.
   - Preserve stale-job recovery and claim behavior.
   - Verification: startup/poll iteration tests pass.

9. `@role/developer-cv-worker` Add/adjust logging.
   - Log selected device as already implemented.
   - Log model loading events with model ID/family/variant only.
   - Add assertions that missing-weight errors and model-loading logs do not include absolute storage paths.
   - Ensure logs do not expose absolute paths, database URLs, tokens, secrets, or env secrets.
   - Verification: logging assertions pass.

10. `@role/tester` Run focused CV worker quality gates from `cv/`.
    - `python -m pytest tests/test_device.py tests/test_storage_paths.py tests/test_startup.py tests/test_model_runtime.py`
    - Expected: `PASS`.

11. `@role/tester` Run full CV worker unit suite from `cv/`.
    - `python -m pytest`
    - Expected: `PASS` or documented blocker with exact failure.

12. `@role/tester` Run CV worker lint from `cv/`.
    - `python -m ruff check .`
    - Expected: `PASS`.

13. `@role/code-reviewer` Review implementation against phase docs.
    - Check no backend API route changes.
    - Check no DB schema changes.
    - Check no frontend changes.
    - Check model selection priority matches docs.
    - Check relative path rule and safe logging.
    - Check documented `models/...` paths resolve under `STORAGE_ROOT` without double-prefixing.
    - Check YOLO26/YOLO11 metadata behavior.
    - Check no inference/tracking/export/later-phase work added.

14. `@role/docs-maintainer` Update only component index if implementation changes worker commands or current-state wording.
    - Expected: usually no product docs update.
    - If `cv/index.md` current implementation summary becomes inaccurate, update only that index.

## Relevant Checks Only

- `python -m pytest tests/test_device.py tests/test_storage_paths.py tests/test_startup.py tests/test_model_runtime.py`
- `python -m pytest`
- `python -m ruff check .`

## Explicit Non-Goals

- No image inference.
- No video inference.
- No tracking.
- No CSV/JSON export generation.
- No result media writing.
- No database migrations.
- No backend API changes.
- No frontend work.
- No training scripts or notebooks.
- No YOLO11 fallback switch unless already documented by model metadata.
