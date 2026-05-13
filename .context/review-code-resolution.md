# Code Review Resolution - Phase 12 Experiment Import Backend API

## Verdict: FIXED

## Resolution table

| # | Review source | Priority | Item | Resolution | Reason |
|---:|---|---|---|---|---|
| 1 | OpenAI code review | important | Tracker-comparison wording guard rejects only exact forbidden strings, allowing variants such as `mota_score`, `tracking_accuracy_score`, and metadata label `IDF1 metric`. | accepted | Matches `docs/TRAINING_EXPERIMENTS.md`: tracker comparison is behavior comparison, not absolute tracking accuracy, and must not require MOTA, IDF1, HOTA, or manually annotated identity metrics. Fix is scoped to existing Phase 12 validation. |

## Accepted critical fixes

- None.

## Accepted important fixes

- Strengthen tracker-comparison forbidden-term validation so forbidden terms are rejected when embedded in metric names or metadata text, not only exact whole-string matches.
- Add regression tests for `mota_score`, `tracking_accuracy_score`, and `IDF1 metric` metadata wording.

## Accepted optional fixes

- None.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Fixes applied

- Updated `backend/app/services/experiments.py` so tracker-comparison forbidden wording is detected inside longer metric names and metadata text, with separator-insensitive matching.
- Updated `backend/tests/test_experiments_api.py` with regression cases for `tracking_accuracy_score`, `mota_score`, and `IDF1 metric`.

## Final verification

- `python -m ruff check app/api/experiments.py app/services/experiments.py app/schemas/experiments.py tests/test_experiments_api.py` from `backend/`: PASS.
- `python -m pytest tests/test_experiments_api.py -q` from `backend/`: PASS, 27 passed.
- `python -m pytest tests/test_experiments_api.py tests/test_admin_api.py::test_admin_stats_users_and_jobs_are_global_and_safe tests/test_data_model.py::test_detections_tracks_and_metrics_relationship_constraints` from `backend/`: PASS, 29 passed.
- Direct helper probe from `backend/`: `mota_score`, `tracking_accuracy_score`, and `IDF1 metric` rejected with 400; `video_processing_fps` accepted.
- `python -m ruff check .` from `backend/`: PASS.
- `python -m pytest` from `backend/`: PASS, 165 passed.
