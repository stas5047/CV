## Phase 21 - Training pipeline scripts, notebooks, dataset preparation, and model cards

**Direction:** Training / Offline CV
**Goal:** Create the offline training workflow artifacts without launching training from the web application.

### Scope

- Create training scripts for dataset preparation and YOLO-compatible structure.
- Create deterministic split script with seed `42`.
- Prefer group-based splitting when source/sequence/video grouping metadata exists.
- Generate `split_manifest.csv` with required columns.
- Create `data.yaml` for one class: `drone`.
- Create Kaggle/Colab notebooks or notebook templates for YOLO26n and YOLO26s fine-tuning.
- Add local smoke training option for tiny subset only.
- Add model card schema and metrics schema.
- Save expected artifacts layout under `storage/models/`.
- Document human responsibilities for running cloud training and placing artifacts.
- Document YOLO11 fallback procedure and required metadata if YOLO26 is unavailable.
- Ensure scripts do not commit datasets or weights.

### Relevant docs

- `docs/TRAINING_EXPERIMENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Dataset split script runs on a small fixture.
- Split manifest includes required columns.
- `data.yaml` defines exactly one class: `drone`.
- Model card schema validates placeholder/null metrics.
- Training README clearly states that web UI/API do not launch training.
- Large datasets and weights remain ignored by Git.

### Commit

`feat(training): add dataset split notebooks and model card workflow`
