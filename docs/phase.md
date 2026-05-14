## Phase 22 - Model artifact registration and experiment artifact import utilities

**Direction:** Backend / Training Integration
**Goal:** Bridge offline training artifacts into backend model registry and experiment import flows.

### Scope

- Add script or CLI helper to register a model version from `model_card.json` and relative weights path.
- Add script or CLI helper to import experiment metrics/artifacts from structured files.
- Validate model cards and metrics schemas before insertion.
- Ensure imported model paths and report artifact paths are relative.
- Support placeholder/null metric values for pre-training or incomplete imports.
- Ensure YOLO11 fallback is recorded accurately when used.
- Add documentation for the artifact registration workflow:
  1. human trains in Kaggle/Colab;
  2. human downloads weights/metrics/model card;
  3. human places artifacts under storage;
  4. admin or helper registers model;
  5. admin activates model;
  6. admin imports experiments.
- Add tests for CLI/helper validation and idempotent imports if supported.

### Relevant docs

- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Valid model card registers a model version.
- Invalid or absolute weights paths are rejected.
- Valid experiment artifact imports run and metrics are queryable.
- Re-running idempotent import does not create unintended duplicates when idempotency is documented.
- README/training docs clearly describe the offline-to-app workflow.

### Commit

`feat(training-import): add model and experiment artifact registration helpers`
