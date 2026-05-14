# Status - Phase 17 Image Processing Pipeline

## Current state

Phase 17 implemented for CV worker image jobs only.

## Completed

- Added image-only queue claiming so video jobs remain queued for later video phase.
- Added image processing module for safe source path resolution, image decode, YOLO inference adapter, detection conversion, annotation, CSV export, JSON export, summary metrics, and completed-job finalization.
- Added safe failure handling for missing source image, corrupted image decode, annotated output creation failure, CSV export creation failure, and JSON export creation failure.
- Final code-review fix added safe failure handling for unsafe DB-stored source paths, result output directory creation failures, and image-job database finalization failures where the worker can still record a failed state.
- Added job-scoped detection cleanup before completed retry finalization to avoid duplicate detection rows.
- Wired `run_poll_iteration` to load resolved model then process claimed image jobs.
- Added worker tests for successful image jobs, detection invariants, no-detection success, export contracts, artifact failures, safe error messages, and image-only queue claiming.
- Updated `cv/index.md` to reflect current worker state and command behavior.

## Quality gates

- `cd cv; python -m pytest tests/test_image_processing.py` -> PASS, 11 passed.
- `cd cv; python -m ruff check aerovision_worker/image_processing.py tests/test_image_processing.py` -> PASS.
- `cd cv; python -m ruff check .` -> PASS.
- `cd cv; python -m pytest` -> PASS, 71 passed.
- `cd cv; python -m pytest -m postgres` -> PASS, 3 passed, 68 deselected.
- `git diff --check` from repo root -> FAIL, unrelated existing trailing whitespace in `docs/phase.md:3`.

## Security/privacy

- DB result/export paths remain relative under `results/{job_id}/`.
- Source media paths are validated with existing relative-path safety helpers before filesystem access.
- Unsafe DB-stored source paths and result directory failures are converted to fixed safe failed-job messages.
- Failed job messages are fixed safe strings and do not include absolute host/container paths.
- CSV/JSON exports contain CV-only image-space detection data and no targeting/navigation/control fields.
- No secrets, tokens, passwords, or database passwords added to logs or exports.

## Deviations

- None from `.context/design.md`, `.context/plan.md`, or `.context/review-plan-resolution.md`.

## Remaining risks

- Video processing, ByteTrack/BoT-SORT tracking, video progress cadence, and track summaries remain later-phase work.
- Real Ultralytics result-object behavior is covered through adapter-shaped tests, not real model inference smoke with weights.
- Repo whitespace check still reports unrelated trailing whitespace in `docs/phase.md:3`; not changed because it was outside accepted review fixes.
