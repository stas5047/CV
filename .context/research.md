# Research - Phase 21 Training Pipeline Artifacts

## Current phase

- Current phase: Phase 21 - Training pipeline scripts, notebooks, dataset preparation, and model cards.
- Direction: Training / Offline CV.
- Goal: Create offline training workflow artifacts without launching training from the web application.
- Risk level: user supplied placeholder only; assumed medium for planning because phase creates offline pipeline artifacts, schemas, notebook templates, and Git-ignore-sensitive large-file paths, but should not alter runtime app behavior.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout exists.
- `docs/phase.md` selects Phase 21 and its relevant docs match roadmap Phase 21.
- Worktree was already dirty before this contract work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- `.context/research.md`, `.context/design.md`, and `.context/plan.md` existed and were empty at inspection time.
- Top-level project areas exist: `backend/`, `frontend/`, `cv/`, `training/`, `scripts/`, `storage/`, `docs/`.
- `training/` contains only `training/index.md`.
- `training/index.md` says no training scripts, notebooks, dependency manifests, configs, dataset helpers, artifact schemas, or tests exist yet.
- `.gitignore` ignores `storage/uploads/**`, `storage/results/**`, `storage/reports/**`, `storage/models/**`, `storage/temp/**`, `storage/datasets/**`, model weights (`*.pt`, `*.pth`, `*.onnx`, `*.engine`), and common video outputs.
- Storage directories exist for `datasets`, `models`, `reports`, `results`, `temp`, and `uploads`.
- Backend and CV worker code/tests exist by filename, but no source behavior was audited for this planning pass.
- Frontend has placeholder `Dockerfile` and `index.md` only by file listing.

## Existing implementation state

- Training surface is unimplemented except folder index.
- No dataset preparation script exists yet.
- No deterministic split script exists yet.
- No `data.yaml` generator/template exists yet.
- No Kaggle or Colab notebook template exists yet.
- No local tiny smoke training helper exists yet.
- No model card schema exists yet.
- No metrics schema exists yet.
- No training-specific tests exist yet.
- Large training artifacts are already ignored by Git through root `.gitignore`.

## Unknowns and assumptions

- Unknown: exact risk level intended by user because request kept `<LOW | MEDIUM | HIGH>` placeholder.
- Assumption: treat this as medium-risk planning due artifact/schema correctness and large-file safety, but no runtime source changes.
- Unknown: exact future filenames for new training scripts/notebooks/schemas are not specified by docs.
- Assumption: implementation should choose minimal filenames under `training/` and update `training/index.md` only if phase implementation changes training commands/files.
- Unknown: actual Seraphim source folder naming and group metadata format.
- Assumption: split tool must accept explicit inputs and support group metadata when present, then fall back to deterministic per-image split if absent.
- Unknown: whether YOLO26 is available in local Ultralytics package at implementation time.
- Assumption: notebook templates should target YOLO26 first and include a documented YOLO11 fallback path without making fallback primary.
- Unknown: whether implementation will add a separate training dependency manifest.
- Assumption: add a training-local dependency manifest or exact install command if runnable scripts/tests need non-stdlib dependencies; do not alter backend/CV dependencies for training-only utilities.
- Planning review resolution accepted explicit Phase 21 contract coverage for all four documented experiment artifact families: model comparison, confidence threshold analysis, tracker behavior comparison, and false-positive analysis.
- Planning review resolution accepted only offline artifact validation/import-readiness utility scope for model cards and metrics; backend/database/frontend import execution remains out of scope for this phase.

## Files likely relevant for implementation

- `training/` - new training scripts, notebook templates, config/schema artifacts, local smoke helpers, tests if chosen.
- `training/index.md` - update after new training files/commands exist.
- `.gitignore` - verify large datasets, weights, notebook outputs, and generated artifacts remain ignored; update only if a gap is found.
- `storage/datasets/seraphim_subset/data.yaml` - generated artifact, must not be committed if under ignored storage.
- `storage/datasets/seraphim_subset/split_manifest.csv` - generated artifact, must not be committed if under ignored storage.
- `storage/models/<model-version>/model_card.json` - generated/validated artifact layout.
- `storage/models/<model-version>/metrics.json` - generated/validated artifact layout.
- `docs/phase.md` - already identifies phase; must not be modified in this planning task.

## Conflicts

- No `WARNING: CONFLICT` found among consulted docs for Phase 21.
