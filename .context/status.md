# Status - Phase 21 Training Pipeline Artifacts

## Current state

- Phase 21 code review resolution fixed.
- Scope stayed offline training artifacts only.
- No backend API, database migration, frontend route, or CV worker runtime changes were made.
- YOLO26 remains primary; YOLO11 appears only as documented fallback guidance in notebook text and metrics guidance.

## Fixes applied after code review

- Metrics artifact validation now rejects absolute and traversal paths for app-facing artifact references such as `detection_metrics.confusion_matrix` and experiment `report_artifacts`.
- Dataset split preparation now rejects non-empty output directories before writing generated YOLO files.
- Dataset split preparation now rejects duplicate flattened image or label target names before copying source files.
- `docs/phase.md` trailing whitespace was removed.
- `training/README.md` and `training/index.md` now document the new dataset split safeguards.

## Files changed

- Added training package metadata: `training/pyproject.toml`.
- Added offline training package under `training/aerovision_training/`.
- Added YOLO26 notebook templates under `training/notebooks/`.
- Added model card and metrics templates under `training/templates/`.
- Added training tests under `training/tests/`.
- Added training workflow notes: `training/README.md`.
- Updated `training/index.md`, `docs/index.md`, and `.context/review-code-resolution.md`.
- Updated `docs/mistakes-codex.md` for the earlier real packaging mistake found by install gate.

## Quality gates

- `python -m pytest training/tests/test_schemas.py::test_metrics_artifact_rejects_absolute_or_traversal_report_paths` - RED before implementation, then PASS.
- `python -m pytest training/tests/test_dataset_split.py::test_prepare_yolo_dataset_rejects_non_empty_output_dir training/tests/test_dataset_split.py::test_prepare_yolo_dataset_rejects_duplicate_output_targets` - RED before implementation, then PASS.
- `python -m pytest training/tests` - PASS, 11 passed.
- `python -m ruff check training` - PASS.
- `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json` - PASS.
- `python -m pip install -e "training[dev]"` - PASS.
- Dataset split CLI smoke on generated fixture under ignored `storage/temp/phase21-final-fixture` - PASS; fixture removed.
- `git diff --check` - PASS for whitespace errors; Git reported line-ending warnings only.

## Security and privacy

- Training artifact validators reject absolute and traversal paths for app-facing model card, metrics, report artifact, and confusion-matrix references.
- No secrets, tokens, credentials, datasets, model weights, generated reports, or media artifacts were added.
- Generated CLI dataset fixture was removed after the smoke check.

## Index/docs

- `training/index.md` updated because `training/aerovision_training/dataset_split.py` behavior materially changed.
- `training/README.md` updated because dataset split command behavior changed.
- `docs/index.md` was not changed during review resolution because no source-of-truth document was created, renamed, or removed.
- Mistake logs were not updated during review resolution because no new real mistake occurred.

## Remaining risks

- Local smoke training command was not executed because it requires `ultralytics`, pretrained weights, and tiny dataset contents.
- Notebook templates were validated structurally; cloud training was not run by design.
