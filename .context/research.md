# Phase 19 Research - Worker CSV/JSON exports and no-detection contracts

## Current phase

Confirmed current phase from `docs/phase.md`:

- Phase 19 - Worker CSV/JSON exports and no-detection contracts
- Direction: CV Worker / Exports
- Goal: Generate CSV and JSON exports exactly according to API/export contracts.

Risk level:

- Assumption: MEDIUM. Export correctness affects downloads, result interpretation, no-detection behavior, DB path safety, and CV-only output boundary, but scope is worker-only and covered by focused tests.

## Docs consulted

Required workflow docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase `Relevant docs:` consulted:

- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/TESTING_QA.md`

Context files checked:

- `.context/research.md` was empty before this write.
- `.context/design.md` was empty before this write.
- `.context/plan.md` was empty before this write.
- `.context/status.md` was empty.
- `.context/review-plan-claude.md` was empty.
- `.context/review-plan-resolution.md` was empty.

## Confirmed repository facts

- Git checkout exists. `git status --short` showed modified `.context/*` review/status files and `docs/phase.md` before this planning write.
- Root contains expected project areas: `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `scripts/`, Compose files, and README/Makefile.
- `docs/index.md` says backend through Phase 13 is implemented, CV worker through video processing/export behavior is present, frontend is only placeholder Dockerfile, and training has no utilities.
- `cv/index.md` says worker currently covers queue claiming, model loading/cache, image processing, video processing, annotated media, CSV/JSON exports, detection/track rows, summaries, progress/heartbeat, and no-detection success.
- `cv/pyproject.toml` defines worker commands: `python -m ruff check .`, `python -m pytest`, and optional `python -m pytest -m postgres`.
- No product docs or source files should change in this phase-contract turn.

## Existing implementation state

Confirmed worker export-related files exist:

- `cv/aerovision_worker/image_processing.py`
  - Defines `CSV_COLUMNS` matching `docs/API.md` required CSV columns.
  - Writes image annotated media, CSV, JSON, detection rows, summary JSON, and relative result paths.
  - No-detection image jobs complete with zero detections, headers-only CSV, JSON `detections: []`, and nullable confidence summary values.
  - Image detections use `frame_index = 0`, `timestamp_ms = 0`, and `track_id = None`.
- `cv/aerovision_worker/video_exports.py`
  - Reuses `CSV_COLUMNS`.
  - Builds video result paths under `results/{job_id}/`.
  - Writes CSV rows from video detections.
  - Writes JSON top-level `job`, `media`, `model`, `parameters`, `summary`, `detections`, `tracks`.
  - Builds track summaries only from detections with non-null `track_id`.
  - Computes derived export values: `center_x`, `center_y`, `bbox_width`, `bbox_height`.
- `cv/aerovision_worker/video_processing.py`
  - Calls video export helpers after annotated MP4 processing.
  - Uses ByteTrack by default and BoT-SORT when requested/supported.
  - Updates video heartbeat/progress during frame processing.
- `cv/aerovision_worker/video_persistence.py`
  - Deletes/reinserts detections/tracks for completed job.
  - Stores `summary_json`, `result_media_path`, `csv_path`, `json_path`, completion time, progress 100, and clears locks.
- `backend/app/db/models.py`
  - `processing_jobs.csv_path`, `processing_jobs.json_path`, and `processing_jobs.result_media_path` have relative-path checks.
  - `detections` and `tracks` tables support export source data.
- `cv/tests/test_image_processing.py`
  - Covers image detection export paths, no-detection exports, failed CSV/JSON writes, CSV column contract, JSON top-level contract, and forbidden output smoke checks.
- `cv/tests/test_video_processing.py`
  - Covers video detections/tracks/exports/progress, no-detection video exports, tracker unavailable behavior, and BoT-SORT tracker argument.

No command gates were run during research because user requested planning artifacts only.

## Unknowns and assumptions

Confirmed facts:

- Phase docs require CSV one row per detection, headers-only CSV for no detections, JSON with required top-level objects/arrays, empty `detections` for no detections, relative `csv_path`/`json_path`, and no forbidden physical-control/targeting/geolocation/engagement fields.
- Docs do not require API/backend route changes in Phase 19 beyond relying on already-defined result download paths.
- Docs do not require frontend work in Phase 19.

Assumptions:

- Existing Phase 18 image/video processing code is allowed as baseline and should be refined only where it misses Phase 19 export contracts.
- JSON object internal field set should stay limited to existing job/media/model/parameter/summary/detection/track CV metadata unless docs explicitly require more.
- Export files remain under `results/{job_id}/detections.csv` and `results/{job_id}/detections.json` because existing backend tests and worker code already use this pattern.
- SQLite-backed worker tests are acceptable for focused export contract tests; PostgreSQL queue tests are not required unless persistence/path behavior changes beyond export completion updates.

Unknowns:

- Whether current code already fully satisfies Phase 19 until focused gates run.
- Whether hidden tests expect stricter JSON field details than docs explicitly list.
- Whether JSON `parameters` may include internal `frame_stride`; docs forbid exposing it in standard UI, not worker JSON export.

## Files likely relevant for implementation

Primary worker files:

- `cv/aerovision_worker/image_processing.py`
- `cv/aerovision_worker/video_exports.py`
- `cv/aerovision_worker/video_processing.py`
- `cv/aerovision_worker/video_persistence.py`
- `cv/aerovision_worker/video_types.py`
- `cv/aerovision_worker/storage_paths.py`

Primary tests:

- `cv/tests/test_image_processing.py`
- `cv/tests/test_video_processing.py`

Reference-only backend/data files:

- `backend/app/db/models.py`
- `backend/app/services/results.py`
- `backend/app/api/jobs.py`
- `backend/tests/test_jobs_api.py`

Do not touch unless contract mismatch is found:

- `docs/*`
- `frontend/*`
- `training/*`
