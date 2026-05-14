# OpenAI Code Review - Phase 17 Image Processing Pipeline

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 17 implementation is scoped correctly to CV worker image processing. It keeps video jobs queued, uses PostgreSQL/shared storage boundaries, writes relative result/export paths, produces CSV/JSON exports, handles no-detection as success, and has relevant worker tests.

One important defect remains: some documented worker error paths still escape safe failure handling and can leave the claimed job in `processing` until stale recovery instead of marking it `failed` immediately.

## Critical issues

None.

## Important issues

1. Output/path/database-adjacent failures can bypass job failure finalization.
   - Evidence: `process_image_job()` only catches `ImageProcessingError` in `cv/aerovision_worker/image_processing.py:139`.
   - Evidence: DB-stored `stored_path` validation happens at `cv/aerovision_worker/image_processing.py:188` through `validate_relative_storage_path(...)`; that helper raises `ValueError`, not `ImageProcessingError`, so an unsafe stored path escapes the catch block.
   - Evidence: result directory creation happens at `cv/aerovision_worker/image_processing.py:407`; `Path.mkdir(...)` can raise `OSError`, but `_output_path()` only converts `ValueError` from path validation at `cv/aerovision_worker/image_processing.py:403-406`.
   - Evidence: `docs/CV_PIPELINE.md:369-371` requires handling failed output media creation, failed CSV/JSON export creation, and database write failures.
   - Impact: a permission/path/storage failure during artifact setup, or an unsafe DB path, can crash the poll iteration instead of writing a safe `failed` job state. Existing tests cover `cv2.imwrite=False`, CSV `open()` failure, and JSON `write_text()` failure, but not `_output_path()` failures or unsafe stored-path failure.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for review input. Shows Phase 17 worker/context changes plus untracked `cv/aerovision_worker/image_processing.py` and `cv/tests/test_image_processing.py`.
- `rtk git diff --stat`: PASS for review input. Shows CV worker, tests, docs/context changes.
- `rtk git diff`: PASS for review input.
- `cd cv; python -m ruff check .`: PASS (`All checks passed!`).
- `cd cv; python -m pytest`: PASS (69 passed, 157 warnings).
- `cd cv; python -m pytest -m postgres`: PASS (3 passed, 66 deselected).

## Security/privacy assessment

No absolute result/export DB paths found in reviewed implementation. CSV/JSON exports stay inside CV image-space fields and do not include targeting/navigation/control data. Remaining privacy/safety risk is failure handling for unsafe stored paths: validation blocks traversal, but the unconverted `ValueError` can bypass safe job failure finalization.

## Positive findings

- Image-only queue claiming in `cv/aerovision_worker/queue.py:187-201` leaves valid video jobs queued for later phase.
- Image detection rows use `frame_index = 0`, `timestamp_ms = 0`, and `track_id = None` in `cv/aerovision_worker/image_processing.py:266-282`.
- No-detection image jobs still complete and produce headers-only CSV plus JSON with empty `detections`, covered by `cv/tests/test_image_processing.py:337-364`.
- Export contract test covers required CSV columns, JSON top-level keys, empty `tracks`, and no obvious forbidden output strings in `cv/tests/test_image_processing.py:492-538`.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/image_processing.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/settings.py`
- `cv/tests/test_image_processing.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_queue_postgres.py`
- `cv/tests/test_startup.py`
- `cv/index.md`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
