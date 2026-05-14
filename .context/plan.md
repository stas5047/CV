# Phase 22 Implementation Plan

## Scope

- Phase only: model artifact registration and experiment artifact import utilities.
- No frontend work.
- No CV worker work.
- No database migration unless implementation discovers existing schema cannot store documented fields.
- No new public API routes unless existing documented routes cannot support Phase 22 after evidence.

## Ordered atomic tasks

1. `@role/developer-training` Re-read `training/aerovision_training/schemas.py`, `training/templates/model_card.placeholder.json`, `training/templates/metrics.placeholder.json`, and tests. Verify current artifact contract against `docs/TRAINING_EXPERIMENTS.md`, `docs/DATA_MODEL.md`, and `docs/API.md`.
   - Verifiable: written notes identify exact mismatched experiment type slugs and required mapping/alignment.

2. `@role/developer-training` Add failing tests for artifact-to-backend payload conversion.
   - Cover model card -> `POST /api/models` payload.
   - Cover metrics artifact -> one or more `POST /api/experiments/import` payloads.
   - Cover nullable metric values.
   - Cover relative path preservation.
   - Cover rejection of absolute/traversal paths.
   - Verifiable: targeted tests fail before conversion/helper exists.

3. `@role/developer-training` Resolve `WARNING: CONFLICT` in training artifact experiment identifiers.
   - Make current training template/schema identifiers match backend/API/data-model identifiers.
   - Required canonical slugs: `model_comparison`, `threshold_analysis`, `tracker_comparison`, `false_positive_analysis`.
   - Reject legacy slugs `confidence_threshold_analysis` and `tracker_behavior_comparison` unless user explicitly approves compatibility aliases later.
   - Do not change product docs.
   - Verifiable: tests prove artifact import payloads use `threshold_analysis` and `tracker_comparison` for backend requests.

4. `@role/developer-training` Implement helper logic in existing training package boundaries.
   - Read model card JSON.
   - Read metrics JSON.
   - Validate both using existing schema validation rules.
   - Build backend model registration payload from model card plus caller-provided relative `weights_path`.
   - Build backend experiment import payloads from metrics artifact plus caller-provided relative `artifacts_path` when needed.
   - Validate path-like metadata inside artifacts before backend mutation, including `split_manifest`, report/plot/confusion-matrix references, and nested config/metadata values that look like paths.
   - Reject absolute paths, traversal paths, drive-qualified paths, container/host paths, and cloud/local absolute path leaks.
   - Do not start training.
   - Do not read or write model weights content.
   - Verifiable: unit tests pass without network or database.

5. `@role/developer-auth-security` Add helper secret-handling tests.
   - Ensure token/password values are not printed in normal or error output.
   - Ensure absolute storage paths are not printed.
   - Ensure path-like metadata leaks fail validation before any backend mutation call.
   - Ensure failed validation exits before backend mutation call.
   - Verifiable: tests inspect captured output/error text.

6. `@role/developer-training` Add CLI entry point or module command for helper.
   - Register model from model card and existing relative weights path through existing backend API.
   - Import experiments from metrics artifact through existing backend API.
   - Optionally activate model through existing `PATCH /api/models/{model_id}/activate` only when explicit flag is supplied.
   - Require admin authorization through backend API; do not bypass backend auth for public mutations.
   - Add CLI smoke test using placeholder model card and metrics template through fake HTTP transport or monkeypatched client.
   - Verifiable: CLI tests assert requested routes, methods, payloads, safe authorization/header handling, and redacted output.

7. `@role/developer-backend` Inspect existing backend model/experiment services against generated helper payloads.
   - If backend already accepts payloads, do not change backend.
   - If backend rejects documented nullable metrics or safe relative paths, add targeted backend tests and minimal fix.
   - Verifiable: backend tests show admin can register model, activate model, import experiments, and regular user cannot.

8. `@role/developer-db` Confirm no schema change needed.
   - Check fields used: `model_versions.metrics_json`, `experiment_runs.config_json`, `experiment_runs.artifacts_path`, `experiment_metrics.metric_value`, `experiment_metrics.metadata_json`.
   - Verifiable: no Alembic migration created unless a documented schema gap is proven.

9. `@role/docs-maintainer` Update non-product implementation docs only if commands or workflow changed.
   - Likely files: `training/README.md`, `training/index.md`, maybe root `README.md`.
   - Document offline-to-app workflow from docs: train in cloud, download artifacts, place under storage, validate, register, activate, import.
   - State helper registers existing files under storage; it does not upload `.pt` weights and does not start training.
   - Do not modify `docs/*.md` product docs in this phase unless user explicitly approves.
   - Verifiable: command examples match implemented helper and avoid secrets.

10. `@role/tester` Run training gates.
    - `python -m pytest training/tests`
    - If a concrete validation command exists, run artifact validator against placeholder templates.
    - Verifiable: PASS or documented FAIL with exact command output.

11. `@role/tester` Run targeted backend API gates for Phase 22, even if backend source code is unchanged.
    - From `backend/`: `python -m ruff check .`
    - From `backend/`: `python -m pytest tests/test_models_api.py tests/test_experiments_api.py tests/test_api_contract.py`
    - Verifiable: PASS or documented FAIL with exact command output.

12. `@role/code-reviewer` Review Phase 22 diff against docs and this contract.
    - Check no training launched from helper.
    - Check no new frontend/CV worker work.
    - Check no new schema/API route unless justified by docs.
    - Check relative paths only.
    - Check no secrets/tokens/passwords in logs, docs, tests, or output.
    - Check YOLO26 primary and YOLO11 fallback metadata remain accurate.
    - Verifiable: review notes list accepted issues or state none found.

## Completion criteria

- Helper validates offline artifacts before backend mutation.
- Helper registers model versions using existing relative weights paths.
- Helper imports experiment metrics/artifacts into backend-visible records.
- Backend admin authorization remains source of truth for mutations.
- Nullable metrics remain supported.
- Experiment type conflict is resolved by making training schema/templates and helper backend payloads use canonical doc slugs.
- Legacy experiment aliases are not supported in Phase 22 unless the user explicitly approves them later.
- Path-like metadata inside imported artifacts is validated before backend mutation and cannot leak absolute/traversal paths.
- No source work outside Phase 22 surfaces.
- Relevant gates pass or blockers are documented.
