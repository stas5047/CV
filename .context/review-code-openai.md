# OpenAI Code Review - Phase 22 Model Artifact Registration and Experiment Import

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 22 stays in documented scope: training-local helper code, artifact schema/template alignment, training tests, and command docs. No backend source, database migration, frontend, or CV worker change found.

Two fixes needed before approval: model-card metric metadata can still carry absolute path strings into the backend model payload, and full diff whitespace check reports a touched docs line.

## Critical issues

None.

## Important issues

1. Model registration helper can leak absolute paths through `metrics_json`.
   - Evidence: `.context/review-plan-resolution.md` requires helper validation of path-like metadata inside imported artifacts before backend mutation, and `.context/design.md` says training artifacts/report metadata must not carry absolute local/cloud paths into API responses or database records.
   - Evidence: `training/aerovision_training/schemas.py` validates path references only when key names look path-like. Extra model metric keys are allowed. Probe: adding `card["metrics"]["source"] = "/app/storage/reports/leak.png"` then calling `build_model_registration_payload(..., weights_path="models/yolo26s/weights.pt")` printed `ACCEPTED /app/storage/reports/leak.png`.
   - Evidence: `training/aerovision_training/artifact_import.py` copies full `model_card["metrics"]` into `metrics_json`. `backend/app/schemas/models.py` returns `metrics_json` in `ModelResponse`, and existing model service does not scan `metrics_json` for absolute paths.
   - Impact: a real model card can register successfully and expose a container/host-looking path through model API responses, violating `docs/API.md` and `docs/AUTH_SECURITY.md` absolute-path exposure rules.
   - Test gap: existing tests cover `plot_path` / `report_path` keys, but not absolute path strings under non-path metadata keys that are still persisted.

2. Full diff whitespace gate reports a touched docs line.
   - Evidence: `rtk git diff --check` output: `docs/phase.md:3: trailing whitespace. +**Direction:** Backend / Training Integration`.
   - Impact: `.context/status.md` reports a targeted diff-check PASS while excluding `docs/phase.md`, but `docs/phase.md` is part of this phase diff. Release hygiene gate is not clean.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short` - PASS for inspection; shows Phase 22 source/docs/context changes plus untracked helper/test files.
- `rtk git diff --stat` - PASS for inspection; note untracked files are not included by Git diff stat.
- `rtk git diff` - PASS for inspection; rtk output was truncated, so untracked helper/test files were read directly.
- `python -m pytest training/tests` - PASS, 26 passed.
- `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json` - PASS.
- `python -m ruff check .` from `backend/` - PASS.
- `python -m pytest tests/test_models_api.py tests/test_experiments_api.py tests/test_api_contract.py` from `backend/` - PASS, 46 passed.
- `rtk git diff --check` - FAIL output present for `docs/phase.md:3` trailing whitespace.
- `rtk git diff --check -- README.md .context/status.md training/README.md training/index.md training/aerovision_training/schemas.py training/templates/metrics.placeholder.json training/tests/test_schemas.py` - PASS.

## Security/privacy assessment

Backend authorization remains authority for model registration, activation, and experiment import. Helper output did not print tokens in tests. Remaining privacy issue: model-card metric payload can carry absolute filesystem path text into `metrics_json` and model API responses.

## Positive findings

- Training experiment slugs now match documented backend/API slugs: `model_comparison`, `threshold_analysis`, `tracker_comparison`, `false_positive_analysis`.
- Helper uses existing backend REST endpoints instead of bypassing auth or writing the database directly.
- Helper registers existing storage paths only; no `.pt` upload or training launch added.
- Backend model/experiment API tests still pass without backend source changes.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `README.md`
- `training/README.md`
- `training/index.md`
- `training/pyproject.toml`
- `training/aerovision_training/artifact_import.py`
- `training/aerovision_training/register_artifacts.py`
- `training/aerovision_training/schemas.py`
- `training/templates/model_card.placeholder.json`
- `training/templates/metrics.placeholder.json`
- `training/tests/test_artifact_import.py`
- `training/tests/test_schemas.py`
- `backend/app/api/models.py`
- `backend/app/api/experiments.py`
- `backend/app/schemas/models.py`
- `backend/app/schemas/experiments.py`
- `backend/app/services/models.py`
- `backend/app/services/experiments.py`
