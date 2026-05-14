# Phase 22 Design

## Phase goal

Create implementation path for Phase 22 only: import offline training artifacts into existing backend model registry and experiment import flows without launching training and without adding product behavior outside docs.

## Intended behavior from docs

- Human runs Kaggle/Colab training outside running app.
- Human downloads weights, metrics, model card, and report artifacts.
- Human places artifacts under storage.
- Admin or helper registers model version.
- Admin activates final model when desired.
- Admin or helper imports experiment results.
- Model cards must include required fields and nullable metrics are allowed.
- Experiment metrics may be incomplete or `null`.
- Model weights and report artifact paths stored in backend must be relative.
- YOLO26 remains primary; YOLO11 fallback must be recorded accurately when used.
- Experiments supported by docs:
  - model comparison
  - confidence threshold analysis
  - tracker behavior comparison
  - false-positive analysis
- Training must not be launched from API, UI, or helper.

## Architecture decisions

- Use existing backend REST API as write boundary for helper-driven registration/import.
- Do not add database tables, schema fields, public API routes, or frontend flows for this phase.
- Keep backend services as authority for admin authorization, path checks, active model behavior, and experiment visibility.
- Keep training package responsible for reading and validating offline artifact JSON files and converting them to existing backend request payloads.
- Resolve existing experiment-type mismatch before import by making current training schemas, templates, and backend-facing helper payloads use the documented backend/API identifiers:
  - `threshold_analysis`
  - `tracker_comparison`
- Do not support legacy aliases `confidence_threshold_analysis` or `tracker_behavior_comparison` in Phase 22 unless the user explicitly approves compatibility behavior later.
- Do not add idempotency unless implementation can prove an existing documented unique key; current docs/schema do not require one.
- Do not upload large `.pt` files through helper. Helper registers existing relative storage paths only.

## Backend impact

- Backend API routes should not change unless tests reveal existing documented behavior gap.
- Backend service behavior should remain unchanged unless needed to accept Phase 22 artifact-derived payloads that already match docs.
- Backend tests may need targeted additions for artifact-derived model/experiment payloads, relative path rejection, nullable metrics, and no training side effects.

## Frontend impact

- None for Phase 22.
- Frontend commands, routes, Ukrainian UI, and pages are later phases.

## DB impact

- No migration expected.
- Existing tables are sufficient:
  - `model_versions`
  - `experiment_runs`
  - `experiment_metrics`
- Existing relative path constraints remain active.

## API impact

- No new API route expected.
- Existing endpoints used by helper:
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
  - `POST /api/experiments/import`
  - optionally `POST /api/auth/login` only if helper implements token retrieval
- API responses must not expose absolute filesystem paths, secrets, tokens, or password hashes.

## Security/privacy impact

- Helper must not log admin password, JWT token, database URL, storage root absolute paths, or sensitive environment values.
- Helper must accept only relative artifact references for backend insertion.
- Helper must validate path-like metadata inside model cards and metrics artifacts before backend mutation, including `split_manifest`, report/plot/confusion-matrix references, and nested metadata/config values that look like paths.
- Helper must reject absolute paths, traversal, drive-qualified paths, container host paths, and cloud/local absolute path leaks in imported artifact metadata.
- Backend must remain admin authority for mutations.
- Regular users must still be unable to register models, activate models, or import experiments.
- Training artifacts and report metadata must not carry absolute local/cloud paths into API responses or database records.

## Test strategy

- Training tests:
  - validate model card still accepts nullable metrics;
  - validate metrics artifact experiment identifiers use backend/API import types;
  - validate legacy experiment aliases reject unless user later approves compatibility;
  - validate absolute/traversal paths reject in top-level fields and path-like metadata;
  - validate helper payload conversion without contacting real backend.
- Backend tests:
  - existing model registration path tests remain relevant;
  - existing experiment import path tests remain relevant;
  - targeted model registration, activation, experiment import, and API contract tests must run for Phase 22 even if backend source code is unchanged.
- Command gates when implementation happens:
  - `python -m pytest training/tests`
  - mocked CLI smoke using placeholder model card and metrics template to verify route, method, safe authorization/header handling, redacted output, and exact JSON payload shape
  - `python -m pytest backend/tests/test_models_api.py backend/tests/test_experiments_api.py backend/tests/test_api_contract.py`
  - `python -m ruff check .` from `backend/` if backend code touched
  - training lint is `not available yet` unless a training lint command is added

## Ambiguities or conflicts

- WARNING: CONFLICT: training artifact experiment type slugs currently differ from backend/API/data-model slugs. Phase 22 implementation must resolve this by changing current training schema/templates to canonical doc slugs, not by keeping legacy slugs as canonical. Exact files:
  - `training/aerovision_training/schemas.py`
  - `training/templates/metrics.placeholder.json`
  - `docs/DATA_MODEL.md`
  - `docs/API.md`
- Ambiguity: docs allow "script or CLI helper" but do not mandate helper location or auth/token mechanism.
- Ambiguity: docs mention idempotent imports only conditionally; no existing idempotency contract found.
