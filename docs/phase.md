## Phase 16 - CV model loading, device selection, and model cache

**Direction:** CV Worker / CV Runtime
**Goal:** Implement model selection, model loading, device selection, and safe fallback/error behavior.

### Scope

- Implement runtime model selection using the resolved `processing_jobs.model_version_id`.
- Load weights from relative model storage paths.
- Implement in-memory model cache when practical.
- Reload or switch models when a job requires a different model version.
- Implement `CV_DEVICE` handling:
  - `auto` uses CUDA when available, otherwise CPU;
  - `cpu` forces CPU;
  - `cuda` fails clearly when CUDA is unavailable.
- Log model loading and selected runtime device.
- Fail jobs safely when weights file is missing.
- Preserve YOLO26 as primary and YOLO11 as documented fallback only.
- Add tests for path validation, missing weights, device selection, and model priority assumptions.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Worker loads a configured model from a relative path when weights exist.
- Missing model file marks job failed with safe error message.
- `CV_DEVICE=cpu` works.
- `CV_DEVICE=auto` falls back to CPU if CUDA is unavailable.
- `CV_DEVICE=cuda` fails clearly if CUDA is unavailable.
- Model loading logs do not expose unsafe paths or secrets.

### Commit

`feat(worker-models): add model loading device selection and cache`
