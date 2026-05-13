# Phase 12 Status

## Current state

Implemented and final review fix applied.

## Scope completed

- Added protected experiment routes:
  - `GET /api/experiments`
  - `GET /api/experiments/{experiment_id}`
  - `POST /api/experiments/import`
- Added experiment request/response schemas.
- Added experiment service logic for published visibility, admin visibility, pagination, filters, import, model reference checks, artifact path checks, and metric safety checks.
- Added tracker-comparison wording guard for forbidden absolute tracking-accuracy terms.
- Added targeted experiment API tests.
- Registered the experiments router.
- Updated `backend/index.md`.
- Final fix strengthened tracker-comparison forbidden-term validation for embedded variants such as `mota_score`, `tracking_accuracy_score`, and metadata label `IDF1 metric`.

## Quality gates

- `python -m pytest tests/test_experiments_api.py -q` from `backend/`: PASS
- `python -m ruff check app/api/experiments.py app/services/experiments.py app/schemas/experiments.py tests/test_experiments_api.py` from `backend/`: PASS
- `python -m pytest tests/test_experiments_api.py tests/test_admin_api.py::test_admin_stats_users_and_jobs_are_global_and_safe tests/test_data_model.py::test_detections_tracks_and_metrics_relationship_constraints` from `backend/`: PASS
- Direct helper probe for reviewed tracker variants from `backend/`: PASS
- `python -m ruff check .` from `backend/`: PASS
- `python -m pytest` from `backend/`: PASS, 165 passed

## Security/privacy

- Experiment list/detail require active JWT user.
- Regular users can see only published experiment runs.
- Import requires active admin user.
- Import rejects unsafe, absolute, outside-`reports/`, and missing artifact paths.
- Import rejects metric metadata containing absolute paths.
- Tracker-comparison import rejects forbidden absolute tracking-accuracy terms inside metric names and metadata text.
- API responses expose only relative artifact paths and do not expose `STORAGE_ROOT`.
- No training launch route, job creation, shell execution, or worker side effect was added.

## Deviations

- None from `.context/design.md`, `.context/plan.md`, or `.context/review-plan-resolution.md`.

## Remaining risks

- Import request shape was contract-defined because product docs do not specify exact JSON body.
- `.context/research.md` notes stale implementation-state text in `docs/index.md`; no Phase 12 product behavior conflict found.
