# Plan - Phase 12 Experiment Import Backend API

## Ordered implementation steps

1. [ ] `@role/developer-backend` Add failing tests in `backend/tests/test_experiments_api.py` for guest rejection on `GET /api/experiments`, `GET /api/experiments/{experiment_id}`, and `POST /api/experiments/import`.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`
   - Expected before implementation: tests fail because routes are missing.

2. [ ] `@role/developer-backend` Add failing tests in `backend/tests/test_experiments_api.py` for published visibility.
   - Regular user sees only published runs in list.
   - Regular user can read published detail.
   - Regular user gets safe not-found behavior for unpublished detail.
   - Admin sees published and unpublished runs.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

3. [ ] `@role/developer-backend` Add failing tests in `backend/tests/test_experiments_api.py` for list pagination and filters.
   - List response uses existing collection shape: `items`, `total`, `limit`, `offset`.
   - `limit` and `offset` page results deterministically.
   - `experiment_type` filter returns only that documented type.
   - Admin published-status filter supports published and unpublished views.
   - Regular-user visibility still hides unpublished rows even when filters are present.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

4. [ ] `@role/developer-auth-security` Add failing tests in `backend/tests/test_experiments_api.py` for role access.
   - Regular user cannot import.
   - Inactive admin token cannot import.
   - Admin can import.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

5. [ ] `@role/developer-backend` Add failing tests in `backend/tests/test_experiments_api.py` for import data behavior.
   - Admin can import `model_comparison`.
   - Admin can import `threshold_analysis`.
   - Admin can import `tracker_comparison`.
   - Admin can import `false_positive_analysis`.
   - Imported metrics are returned with `metric_value = null` preserved.
   - Unsupported `tracking_accuracy` is rejected.
   - Nonexistent `model_version_id` is rejected with a safe 400/404 response that does not expose stack traces, DB internals, or storage roots.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

6. [ ] `@role/developer-auth-security` Add failing tests in `backend/tests/test_experiments_api.py` for tracker behavior wording.
   - Valid `tracker_comparison` metric names use documented behavior indicators, such as `video_processing_fps`, `unique_track_ids`, `frames_with_detections`, `average_confidence`, `track_fragmentation_proxy`, `qualitative_visual_stability`, and `observed_id_switches`.
   - Reject case-insensitive forbidden tracker accuracy metric names or metadata labels: `tracking_accuracy`, `MOTA`, `IDF1`, `HOTA`.
   - Do not add aliases such as `tracker_behavior_comparison`; documented experiment type remains `tracker_comparison`.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

7. [ ] `@role/developer-auth-security` Add failing tests in `backend/tests/test_experiments_api.py` for artifact path and response safety.
   - Reject `/app/storage/reports/exp/metrics.json`.
   - Reject `C:/storage/reports/exp/metrics.json`.
   - Reject `../reports/exp/metrics.json`.
   - Reject `reports/../secret/metrics.json`.
   - Reject `temp/experiment/metrics.json`.
   - Reject missing `reports/...` target.
   - Reject or sanitize echoed metric metadata that would expose absolute `STORAGE_ROOT` or unsafe absolute paths.
   - Do not leak `STORAGE_ROOT` in response text, including nested metric metadata.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

8. [ ] `@role/developer-backend` Create `backend/app/schemas/experiments.py`.
   - Define request schemas using only documented `experiment_runs` and `experiment_metrics` fields.
   - Define response schemas using existing ORM fields and nested metric rows.
   - Preserve nullable `metric_value`.
   - Forbid extra request fields.
   - Verify with: `cd backend; python -m ruff check app/schemas/experiments.py`

9. [ ] `@role/developer-backend` Create `backend/app/services/experiments.py`.
   - Implement list-visible query with user/admin visibility rules.
   - Implement pagination with `limit`/`offset`.
   - Implement `experiment_type` filter and admin-only published-status filter.
   - Implement detail lookup with safe not-found behavior for invisible runs.
   - Implement admin import that inserts one `ExperimentRun` and its `ExperimentMetric` rows in one transaction.
   - Validate optional `model_version_id` exists before commit.
   - Validate experiment type against documented types.
   - Validate tracker comparison metric wording against documented behavior-comparison boundary.
   - Verify with: `cd backend; python -m ruff check app/services/experiments.py`

10. [ ] `@role/developer-auth-security` Implement artifact path and response safety validation in `backend/app/services/experiments.py`.
   - Normalize with `validate_relative_storage_path`.
   - Resolve with `safe_join_storage_path`.
   - Require `reports/` prefix.
   - Require resolved target to exist as file or directory under `STORAGE_ROOT`.
   - Prevent echoed metric metadata from exposing absolute storage roots or unsafe absolute paths.
   - Convert validation failures into safe `400` responses.
   - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

11. [ ] `@role/developer-backend` Create `backend/app/api/experiments.py`.
   - Add `GET /experiments` using active-user dependency.
   - Add `GET /experiments/{experiment_id}` using active-user dependency.
   - Add `POST /experiments/import` using admin dependency.
   - Keep handlers thin and delegate to service functions.
   - Verify with: `cd backend; python -m ruff check app/api/experiments.py`

12. [ ] `@role/developer-backend` Register experiments router in `backend/app/api/router.py`.
    - Include router under existing `/api` prefix.
    - Do not modify unrelated routers.
    - Verify with: `cd backend; python -m pytest tests/test_experiments_api.py -q`

13. [ ] `@role/tester` Run scoped Phase 12 backend checks.
    - `cd backend; python -m ruff check app/api/experiments.py app/services/experiments.py app/schemas/experiments.py tests/test_experiments_api.py`
    - `cd backend; python -m pytest tests/test_experiments_api.py tests/test_admin_api.py::test_admin_stats_users_and_jobs_are_global_and_safe tests/test_data_model.py::test_detections_tracks_and_metrics_relationship_constraints`
    - Expected: PASS.

14. [ ] `@role/code-reviewer` Review Phase 12 diff against docs.
    - Confirm no training launch endpoint or side effect exists.
    - Confirm only documented experiment types are accepted.
    - Confirm no experiment type aliases are added.
    - Confirm `tracker_comparison` is behavior comparison, not tracking accuracy.
    - Confirm tracker comparison metrics/metadata do not expose `tracking_accuracy`, `MOTA`, `IDF1`, `HOTA`, or manually annotated identity metrics as required API-facing metrics.
    - Confirm regular users cannot see unpublished runs.
    - Confirm list pagination and documented filters enforce visibility before returning rows.
    - Confirm import is admin-only.
    - Confirm invalid `model_version_id` returns safe 400/404.
    - Confirm `metric_value = null` survives API response.
    - Confirm no absolute storage paths are returned, including in nested metric metadata.
    - Confirm no unrelated frontend, worker, migration, or docs changes.

15. [ ] `@role/docs-maintainer` Decide docs/index updates.
    - If implementation creates new backend files only, update `backend/index.md` if current-file inventory or commands become inaccurate.
    - Do not modify product docs for Phase 12 behavior unless implementation changes documented commands or structure.

## Phase boundary

- No frontend implementation.
- No CV worker implementation.
- No training utilities.
- No migrations unless existing schema is proven insufficient.
- No new top-level folders.
- No routes beyond documented experiment endpoints.
- No training launch from API or UI.
