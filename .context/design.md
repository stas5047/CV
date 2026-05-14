# Design - Phase 21 Training Pipeline Artifacts

## Phase goal

Create implementation contract for Phase 21: offline training workflow artifacts for dataset preparation, deterministic YOLO dataset splits, YOLO26 notebook templates, tiny local smoke training, model card/metrics schemas, artifact layout, and human handoff notes. Web UI/backend must not launch training.

## Intended behavior from docs

Confirmed facts:

- Training is outside running web application.
- Human user runs Kaggle/Colab sessions, downloads weights/metrics, places artifacts under storage, and registers models through admin tooling/UI.
- Code agents create scripts, notebooks, configs, dataset split helpers, model-card schemas, metrics schemas, import utilities where needed, and instructions.
- Training task is single-class object detection with class `drone`.
- YOLO26 is primary; YOLO11 is fallback only after YOLO26 unavailability is reported and documented.
- Training starts from pretrained weights, not scratch.
- Default training parameters: image size `640`, epochs `50`, seed `42`, task `detect`, class count `1`, class name `drone`.
- Primary dataset is Seraphim Drone Detection Dataset, planned subset 20,000 images with 16,000 train, 2,000 validation, 2,000 test.
- Split priority: group/source/sequence/video split first when metadata exists; deterministic random per-image split only when grouping metadata is unavailable.
- `split_manifest.csv` must include `image_path`, `label_path`, `source_group_id`, and `split`.
- Canonical dataset structure is `storage/datasets/seraphim_subset/images/{train,val,test}`, `labels/{train,val,test}`, `data.yaml`, `split_manifest.csv`.
- `data.yaml` must define exactly one class, class `0`: `drone`.
- Model artifact layout under model storage should contain model directory, `weights.pt`, `model_card.json`, and `metrics.json`.
- Model card fields must include name, model family, variant, task, classes, dataset, split manifest, split counts, image size, epochs, and metrics.
- Metric values may be `null` before real training results exist.
- Required metrics include precision, recall, mAP@0.5, mAP@0.5:0.95, confusion matrix, model size, latency, FPS, processing time, and average video FPS.
- Experiments supported by artifacts/import: model comparison, confidence threshold analysis, tracker behavior comparison, false-positive analysis.
- Phase 21 artifact schemas/templates must explicitly cover all four experiment families: model comparison, confidence threshold analysis, tracker behavior comparison, and false-positive analysis.
- Bird vs Drone is false-positive analysis only, not second training class.
- Local smoke training is allowed only on tiny subset to verify pipeline and must not be final model/evaluation evidence.
- Large datasets, weights, generated media, and generated results must not be committed.

Assumptions:

- New training files should live under `training/` because repository already reserves that folder for this surface.
- Generated dataset/model artifacts should be written under ignored `storage/` paths, not committed.
- Implementation may create a small fixture under `training/` for tests if it contains tiny synthetic metadata/labels only and no real dataset/weights.

## Architecture decisions

- Keep training tooling offline and file-based. No backend route, frontend page, worker queue behavior, or database schema change belongs in this phase.
- Keep all generated data/model outputs in shared storage layout documented by architecture/training docs.
- Use deterministic split behavior with seed `42`; prefer group-aware splitting when a group column or source metadata is present.
- Keep notebook templates human-runnable in Kaggle/Colab. Do not require local long training.
- Keep YOLO26 as primary in configs/notebooks. If fallback instructions are present, label them as fallback only and require model card/experiment metadata to record actual family.
- Keep schemas permissive for placeholder `null` metrics but strict for required keys and single-class `drone` invariant.
- Keep dependency setup reproducible. If Phase 21 scripts require non-stdlib packages, add a training-local dependency manifest or exact install command and list it in `training/index.md`.
- Keep import support in this phase offline and artifact-focused only: validation/import-readiness for model cards and metrics is allowed; backend routes, database import execution, frontend flows, and runtime training launch are out of scope.
- Use `opencv-python-headless` only if image/video inspection is needed in training utilities; avoid GUI OpenCV calls.

## Backend impact

- Not touched in Phase 21 contract.
- No new API endpoints, auth flows, migrations, or route handlers.
- Future model registration/import behavior remains in existing backend/admin APIs, outside this training artifact phase unless docs phase is expanded.

## Frontend impact

- Not touched in Phase 21 contract.
- No UI changes, no route changes, no Ukrainian copy changes.

## DB impact

- Not touched in Phase 21 contract.
- No schema changes.
- Training artifacts may later be registered/imported into existing model/experiment tables by admin flows, but this phase creates offline artifacts only.

## API impact

- Not touched in Phase 21 contract.
- No API contract changes.

## Security/privacy impact

- Keep cloud credentials, notebook tokens, dataset credentials, admin credentials, and API tokens out of files/logs.
- Keep datasets, model weights, generated reports, and generated media out of Git.
- Validate artifact paths as relative when scripts emit references intended for model cards/import.
- Avoid absolute host paths in model cards and metrics artifacts where app-visible metadata could consume them later.
- Do not execute user-uploaded files.

## Test strategy

- Add narrow training tests only for created training utilities/schemas.
- Required checks when available:
  - Dataset split script runs on a small fixture.
  - Split manifest has `image_path`, `label_path`, `source_group_id`, `split`.
  - Split is deterministic with seed `42`.
  - Group IDs do not cross `train`, `val`, and `test` when group metadata exists.
  - `data.yaml` defines one class: `drone`.
  - Model card schema accepts placeholder `null` metrics and rejects missing required keys.
  - Metrics schema accepts required experiment metric families with incomplete/null values.
  - Schema fixtures validate all four documented experiment families: model comparison, confidence threshold analysis, tracker behavior comparison, and false-positive analysis.
  - Notebook-template check confirms templates start from pretrained YOLO weights and do not train from scratch.
  - Dependency install or command strategy is documented when scripts/tests need non-stdlib packages.
  - Local smoke training command exists only as tiny-subset verification or is reported `not available yet` until implemented.
  - Git ignore check confirms generated dataset/model artifacts remain untracked.
- Do not add backend, frontend, Docker, auth, upload, or worker queue gates unless implementation touches those surfaces.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found in consulted docs.
- Ambiguity: exact names and internal structure for training scripts/notebooks/schemas are not specified.
- Ambiguity: exact Seraphim source metadata format is not specified.
- Resolved scope: Phase 21 may include a minimal offline artifact validation/import-readiness utility for model cards and metrics because `TRAINING_EXPERIMENTS.md` lists import utilities as code-agent responsibility. It must not add backend/database/frontend import execution unless a later phase or user instruction expands scope.
- Ambiguity: user request contains placeholders for phase title and risk. Current phase comes from `docs/phase.md`; risk is assumed medium.
