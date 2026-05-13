# OpenAI Code Review - Phase 12

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 12 adds documented experiment list/detail/import endpoints, router registration, schemas, service logic, and targeted backend tests. Access control, published visibility, model reference validation, relative report artifact validation, nullable metrics, and no-training side effect checks are covered.

One important issue remains: tracker-comparison forbidden terms are matched only as exact strings, so metric names or metadata labels that still expose forbidden tracking-accuracy concepts can pass.

## Critical issues

None.

## Important issues

1. Tracker-comparison wording guard misses common forbidden variants.
   - Evidence: `backend/app/services/experiments.py:176-183` lowercases each text value and rejects only exact membership in `{"tracking_accuracy", "mota", "idf1", "hota"}`. Values such as `mota_score`, `tracking_accuracy_score`, or metadata label `IDF1 metric` are accepted.
   - Verification evidence: direct helper check from `backend/` returned `MOTA REJECTED 400`, but `mota_score ACCEPTED`, `tracking_accuracy_score ACCEPTED`, and `{'label': 'IDF1 metric'} ACCEPTED`.
   - Doc evidence: `docs/TRAINING_EXPERIMENTS.md:382-394` says tracker comparison is behavior comparison, not absolute tracking accuracy, and must not require MOTA, IDF1, HOTA, or manually annotated tracking-identity metrics. `.context/plan.md` also required metadata wording checks for forbidden terms.
   - Impact: Admin can import API-facing tracker metrics that violate product wording boundary while still using valid `tracker_comparison` type.
   - Required fix: reject forbidden terms as tokens/substrings in tracker metric names and metadata text, not only exact whole-string equality. Add tests for variants such as `mota_score`, `tracking_accuracy_score`, and `IDF1 metric`.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for inspection; Phase 12 source files and context/doc updates present.
- `rtk git diff --stat`: PASS for inspection; tracked diff inspected, untracked source files read directly.
- `rtk git diff`: PASS for inspection; tracked diff inspected.
- `python -m ruff check app/api/experiments.py app/services/experiments.py app/schemas/experiments.py tests/test_experiments_api.py` from `backend/`: PASS.
- `python -m pytest tests/test_experiments_api.py tests/test_admin_api.py::test_admin_stats_users_and_jobs_are_global_and_safe tests/test_data_model.py::test_detections_tracks_and_metrics_relationship_constraints` from `backend/`: PASS, 26 passed.
- Probe command using `_reject_forbidden_tracker_terms`: FAIL evidence for wording guard only, not a formal gate.

## Security/privacy assessment

Applicable. List/detail require active JWT users; import requires active admin; regular users see published runs only; artifact paths must be relative, under `reports/`, and existing; obvious absolute paths in `config_json` and metric metadata are rejected. No training launch route, shell execution, worker job, or absolute storage-root response was found in reviewed Phase 12 code.

## Positive findings

- Route handlers in `backend/app/api/experiments.py` stay thin and delegate business rules to service code.
- Experiment endpoints match documented `/api/experiments` surface only; no frontend, worker, migration, or training-launch scope creep found.
- Tests cover guest rejection, regular/admin visibility, pagination/filter shape, admin-only import, inactive admin rejection, supported experiment types, missing model reference safety, artifact path safety, nullable metric values, and no processing-job side effect.
- `backend/index.md` was updated for new experiment API files and current backend state.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/FRONTEND_UX.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `backend/app/api/router.py`
- `backend/app/api/experiments.py`
- `backend/app/schemas/experiments.py`
- `backend/app/services/experiments.py`
- `backend/tests/test_experiments_api.py`
- `backend/app/core/storage_paths.py`
- `backend/app/db/models.py`
- `backend/index.md`
