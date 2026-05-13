# Design - Phase 12 Experiment Import Backend API

## Phase goal

Implement backend experiment import and visibility API for Phase 12 only:

- `GET /api/experiments`
- `GET /api/experiments/{experiment_id}`
- `POST /api/experiments/import`

No source implementation happens in this planning phase.

## Intended behavior from docs

Confirmed:

- All experiment routes are protected by JWT auth.
- Regular users can list and read only `is_published=true` experiment runs.
- Admins can list and read all imported experiment runs.
- Only admins can import experiment runs and metrics.
- Import creates structured `experiment_runs` and `experiment_metrics` records from existing artifacts under storage.
- Supported experiment types are:
  - `model_comparison`
  - `threshold_analysis`
  - `tracker_comparison`
  - `false_positive_analysis`
- `metric_value` may be `null`.
- Artifact paths must be relative, safe, and must not expose absolute filesystem paths.
- API and UI-facing data must use tracker behavior wording, not absolute tracking accuracy.
- API must not launch training.
- Tracker comparison imports must not expose absolute tracking-accuracy metric wording. For `tracker_comparison`, reject forbidden metric names/metadata labels such as `tracking_accuracy`, `MOTA`, `IDF1`, and `HOTA`; use documented behavior indicators such as processing FPS, unique track IDs, frames with detections, average confidence, track fragmentation proxy, qualitative visual stability, and observed ID switches.

Assumptions:

- Import request uses only documented experiment run fields and documented metric fields.
- List response follows existing backend collection shape: `items`, `total`, `limit`, `offset`.
- List supports pagination plus `experiment_type` filter for all authenticated users and published-status filter for admins. Visibility is enforced before rows are returned.
- Detail response includes run data and metric rows for runs visible to caller.
- `artifacts_path` is constrained to `reports/` because docs describe experiment reports/artifacts under storage reports.
- Existing file or directory under `STORAGE_ROOT` satisfies artifact existence.

## Architecture decisions

- Add a new experiments router and include it in `backend/app/api/router.py`.
- Keep route handlers thin; route layer handles FastAPI dependencies and response model conversion.
- Put visibility, import, validation, and persistence logic in `backend/app/services/experiments.py`.
- Put request/response schemas in `backend/app/schemas/experiments.py`.
- Reuse existing ORM models; do not add tables, migrations, or schema fields.
- Reuse `get_current_active_user` and `get_current_admin_user`.
- Reuse storage path helpers for path normalization and traversal prevention.
- Do not read metric JSON contents from disk in this phase unless docs already define exact artifact schema; import accepts structured metrics in request body and validates the referenced artifact path exists.

## Backend impact

- Add experiment list/detail/import routes under `/api/experiments`.
- Register router with `/api` root router.
- Add service helpers for:
  - list visible experiments;
  - get visible experiment detail;
  - import experiment run with metric rows;
  - validate experiment type;
  - validate artifact path.
- Return safe 404 for unpublished or missing run when regular user requests it.
- Return 403 for non-admin import.
- Return validation error for unsupported experiment type, unsafe artifact path, missing artifact path target, invalid model reference, and forbidden tracker accuracy metric wording.

## Frontend impact

- No frontend source changes in this phase.
- Backend response must support later `/experiments` page:
  - published-only visibility for regular users;
  - null metric values preserved as JSON null;
  - no raw absolute filesystem paths;
  - tracker behavior wording available through documented type/value names.

## DB impact

- No migration planned.
- Use existing `experiment_runs` fields:
  - `name`
  - `experiment_type`
  - `description`
  - `model_version_id`
  - `dataset_name`
  - `config_json`
  - `artifacts_path`
  - `is_published`
  - `created_by_user_id`
- Use existing `experiment_metrics` fields:
  - `experiment_run_id`
  - `metric_name`
  - `metric_value`
  - `metric_unit`
  - `metadata_json`

## API impact

- Implement documented endpoints only.
- Do not add routes outside `/api/experiments`.
- Do not add training-launch endpoints, file upload endpoints, or frontend-only flows.
- Do not expose absolute host/container paths.
- Keep API output inside CV-only boundary: model, dataset, config, artifacts reference, experiment metrics, and performance/detection analysis metadata only.

## Security/privacy impact

- Import route requires admin role.
- List/detail require active authenticated user.
- Regular users cannot see unpublished runs.
- Path validation rejects absolute paths, traversal, empty paths, and paths outside reports storage.
- API responses must not include secrets, tokens, passwords, stack traces, or absolute storage roots, including echoed metric metadata.
- No training execution, shell execution, notebook launch, or user-uploaded file execution.

## Test strategy

Backend tests only, scoped to Phase 12:

- Guest cannot list/read/import experiments.
- Active regular user lists only published runs.
- Active admin lists published and unpublished runs.
- List pagination returns `items`, `total`, `limit`, and `offset`.
- List filtering supports `experiment_type`; admin-only published-status filtering supports published and unpublished views without bypassing visibility rules.
- Regular user gets safe not-found behavior for unpublished detail.
- Admin can import each documented experiment type.
- Admin import with nonexistent `model_version_id` returns safe 400/404 without stack traces, DB internals, or storage roots.
- Regular user cannot import.
- Inactive admin token cannot import.
- Import accepts `metric_value = null` and response preserves it.
- Import rejects unsupported experiment type such as `tracking_accuracy`.
- Import rejects `tracker_comparison` metrics/metadata using absolute tracking-accuracy wording such as `tracking_accuracy`, `MOTA`, `IDF1`, or `HOTA`.
- Import rejects absolute, traversal, outside-category, and missing artifact paths.
- Responses do not include absolute `STORAGE_ROOT`, including nested metric metadata when metadata is echoed.
- Import does not create processing jobs, worker work, or training side effects.
- Existing admin stats remain compatible with imported runs.

Planned quality gates:

- `cd backend; python -m ruff check app/api/experiments.py app/services/experiments.py app/schemas/experiments.py tests/test_experiments_api.py`
- `cd backend; python -m pytest tests/test_experiments_api.py tests/test_admin_api.py::test_admin_stats_users_and_jobs_are_global_and_safe tests/test_data_model.py::test_detections_tracks_and_metrics_relationship_constraints`

## Ambiguities or conflicts

- WARNING: CONFLICT: `docs/index.md` current implementation state says backend is still placeholder-only, while current repository and `backend/index.md` show implemented backend APIs through Phase 11. This affects implementation-state research only, not Phase 12 experiment API behavior.
- No confirmed doc conflict found between `docs/phase.md` and `docs/ROADMAP.md` for Phase 12.
- Ambiguity: exact import request body is not specified. Use only documented database fields and metric fields; do not add product concepts.
- Ambiguity: docs mention artifact paths from existing files, while cleanup logic supports file or directory protection. Use existing path helper behavior and accept existing file or directory under `reports/`.
- Ambiguity: `FRONTEND_UX.md` gives exact Ukrainian empty text for frontend, but Phase 12 is backend only. Do not implement frontend empty states here.
