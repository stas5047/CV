# OpenAI Code Review - Phase 21 Training Pipeline Artifacts

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 21 stays in offline training scope: training package, dataset splitter, schemas/templates, notebook templates, tests, README, and index updates. No backend API, DB migration, frontend route, or CV worker runtime change found.

Three changes needed before approval: metrics artifact validation lets absolute report paths through, dataset output can silently corrupt with duplicate filenames or stale files, and `rtk git diff --check` fails.

## Critical issues

None.

## Important issues

1. Metrics validator accepts absolute app-facing artifact paths.
   - Evidence: `.context/plan.md:49` and `.context/plan.md:79` require model card/metrics artifact references to be relative. `.context/design.md:77-78` says avoid absolute host paths in model cards and metrics artifacts. `docs/TRAINING_EXPERIMENTS.md:402-408` says experiment import includes report artifact paths.
   - Evidence: `training/aerovision_training/schemas.py:69-114` validates metric structure and experiment types, but never calls `_validate_relative_path` for `detection_metrics.confusion_matrix` or any metrics/report artifact reference. `_validate_relative_path` is only used by model-card validation at `training/aerovision_training/schemas.py:58-66`.
   - Evidence: reviewer probe accepted an absolute path: setting `metrics["detection_metrics"]["confusion_matrix"] = "/app/storage/reports/cm.png"` then calling `validate_metrics_artifact(metrics)` printed `accepted absolute confusion_matrix`.
   - Impact: offline import-readiness can approve metrics artifacts that later expose container/host paths through admin import/display flows.

2. Dataset writer can produce inconsistent YOLO output with duplicate basenames or stale files.
   - Evidence: `docs/TRAINING_EXPERIMENTS.md:190` says Seraphim is compiled multi-source data, where duplicate image basenames are plausible. `training/aerovision_training/dataset_split.py:40-43` writes targets using only `item.image_path.name` and `item.label_path.name`, with no collision check before `shutil.copy2`.
   - Evidence: `training/aerovision_training/dataset_split.py:37` and `training/aerovision_training/dataset_split.py:154-157` create output folders with `exist_ok=True`, but do not clean or reject a non-empty output directory.
   - Impact: two source files with same basename can overwrite each other silently, and reruns into `storage/datasets/seraphim_subset` can leave stale files not represented by `split_manifest.csv`. Training may consume wrong data while manifest appears valid.
   - Test gap: `training/tests/test_dataset_split.py` covers determinism and group leakage, but not basename collisions or stale output reuse.

3. Diff whitespace gate fails.
   - Evidence: `rtk git diff --check` reports `docs/phase.md:3: trailing whitespace` on `**Direction:** Training / Offline CV  `.
   - Impact: quality gate is not clean.

## Optional issues

None.

## Quality gate assessment

- `python -m pytest training/tests` - PASS, 8 tests passed.
- `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json` - PASS.
- `python -m ruff check training` - PASS.
- `rtk git diff --check` - FAIL, `docs/phase.md:3: trailing whitespace`.
- `python -m pip install -e "training[dev]"` - not rerun by reviewer; `.context/status.md:27` reports PASS.
- Dataset split CLI smoke under `storage/temp/phase21-cli-fixture` - not rerun by reviewer; `.context/status.md:26` reports PASS.
- Local smoke training - not run by design; `.context/status.md:37` says it needs `ultralytics`, pretrained weights, and tiny dataset contents.

## Security/privacy assessment

Applicable because Phase 21 added artifact validators for files later consumed by model/experiment import workflows. No secrets, credentials, real datasets, model weights, generated reports, or media artifacts found in changed files. Main privacy risk is Important issue 1: metrics validation does not reject absolute artifact paths.

## Positive findings

- Training remains offline-only; no web UI/API training launch added.
- YOLO26 remains primary, YOLO11 appears only as fallback guidance.
- Single-class `drone` invariant is enforced in model-card validation and dataset `data.yaml`.
- Metrics template covers all four documented experiment families.
- Notebook checks enforce pretrained YOLO weights, image size `640`, and seed `42`.
- Training README and `training/index.md` document commands and human handoff clearly.

## Files consulted

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
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
- `rtk git diff --check`
- `training/README.md`
- `training/index.md`
- `training/pyproject.toml`
- `training/aerovision_training/__init__.py`
- `training/aerovision_training/dataset_split.py`
- `training/aerovision_training/schemas.py`
- `training/aerovision_training/validate_artifacts.py`
- `training/aerovision_training/notebook_checks.py`
- `training/aerovision_training/smoke_train.py`
- `training/templates/model_card.placeholder.json`
- `training/templates/metrics.placeholder.json`
- `training/notebooks/yolo26n_finetune_template.ipynb`
- `training/notebooks/yolo26s_finetune_template.ipynb`
- `training/tests/conftest.py`
- `training/tests/test_dataset_split.py`
- `training/tests/test_schemas.py`
- `training/tests/test_notebooks.py`
- `docs/mistakes-codex.md`
