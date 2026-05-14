# Phase 20 Research - Worker error handling, logging, and integration hardening

## Current phase

Confirmed from `docs/phase.md`:

- Phase 20 - Worker error handling, logging, and integration hardening
- Direction: CV Worker / QA
- Goal: Harden worker behavior before connecting frontend flows.

Risk level:

- Assumption: MEDIUM. User input left risk placeholder unset. Phase touches worker failure states, safe error messages, logs, DB status writes, no-detection behavior, and integration reliability, but does not require new public API, schema, frontend, Docker, or product behavior.

## Docs consulted

Required workflow docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase `Relevant docs:` consulted:

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

Context files checked:

- `.context/research.md` was empty before this write.
- `.context/design.md` was empty before this write.
- `.context/plan.md` was empty before this write.
- `.context/status.md` was empty.

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before this write showed modified `.context/*` review/status files and modified `docs/phase.md` already present.
- Root contains `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `scripts/`, Compose files, README, Makefile, `.env.example`, `AGENTS.md`, and `CLAUDE.md`.
- `docs/phase.md` is set to Phase 20.
- `cv/pyproject.toml` defines worker runtime dependencies and dev checks:
  - `python -m ruff check .`
  - `python -m pytest`
  - optional `python -m pytest -m postgres`
- `cv/index.md` says current worker implementation covers queue claiming, stale recovery, model runtime, image processing, video processing, annotated outputs, CSV/JSON exports, progress/heartbeat, and no-detection success.
- `backend/index.md` says backend APIs through Phase 13 are present.
- `frontend/` remains placeholder-only.
- `training/` remains index-only.

WARNING: CONFLICT:

- `docs/index.md` says `cv/` contains only Phase 14 scaffold and no queue/inference/tracking/export/result writes.
- `cv/index.md` and actual `cv/aerovision_worker/*` files show queue, image processing, video processing, exports, and result writes exist.
- `backend/index.md` also says later phases add worker queue/CV/export behavior, which conflicts with `cv/index.md` and actual `cv/` files.
- This is current-state documentation drift, not a product behavior conflict in Phase 20 docs.

## Existing implementation state

Confirmed worker files:

- `cv/aerovision_worker/main.py`
  - Runs startup checks, selects/logs device, waits for DB, recovers stale jobs, claims queued jobs, loads model, dispatches image/video processors, and marks model-load failures failed with safe model error text.
- `cv/aerovision_worker/queue.py`
  - Claims jobs with `FOR UPDATE SKIP LOCKED` on PostgreSQL.
  - Updates heartbeat/progress.
  - Recovers stale jobs by requeueing or failing with `Worker heartbeat timed out`.
  - `fail_processing_job` sets `status = failed`, `error_message`, `completed_at`, clears locks, sets `last_heartbeat_at`, and updates timestamp.
- `cv/aerovision_worker/device.py`
  - `auto` falls back to CPU when CUDA unavailable.
  - forced `cuda` raises `CUDA requested but unavailable`.
- `cv/aerovision_worker/model_runtime.py`
  - Resolves job-specific model, then active DB model, then `ACTIVE_MODEL_ID`.
  - Resolves relative/safe weights paths and hides absolute missing-path detail behind `Model weights file is missing`.
  - Logs model loading/loaded events.
- `cv/aerovision_worker/logging.py`
  - Redacts database URLs, password/token/secret assignments, JWT-like tokens, absolute paths, and secret words.
- `cv/aerovision_worker/image_processing.py`
  - Handles missing image file, unsafe source path, undecodable image, inference failure, output directory failure, annotated image write failure, CSV/JSON write failure, DB completion failure.
  - On known processing errors, marks job failed with safe `error_message`.
  - No-detection image jobs complete successfully and write empty exports.
  - Successful jobs set `progress_percent = 100`, `completed_at`, `last_heartbeat_at`, and result paths.
- `cv/aerovision_worker/video_processing.py`
  - Handles missing video file, unsafe source path, unopened/corrupt video, unsupported first-frame decode, tracker runtime failure, annotated output failure, export failure, DB completion failure.
  - Updates heartbeat/progress during frame processing.
  - No-detection video jobs complete successfully and write empty exports/tracks.
- `cv/aerovision_worker/video_exports.py`
  - Writes video CSV/JSON exports under relative `results/{job_id}/...`.
  - Maps export write failures to safe `VideoProcessingError`.
- `cv/aerovision_worker/video_persistence.py`
  - Inserts detection/track rows, writes summary/result/export relative paths, sets complete timestamps and progress, and clears locks.

Confirmed tests:

- `cv/tests/test_queue.py` covers claim, heartbeat/progress, stale recovery, and failed-job update shape.
- `cv/tests/test_queue_postgres.py` covers PostgreSQL queue behavior when DB is reachable.
- `cv/tests/test_startup.py` covers startup checks, stale recovery path, model-load failure path, image/video dispatch, and unsupported claimed media type.
- `cv/tests/test_device.py` covers CUDA fallback and forced CUDA failure.
- `cv/tests/test_model_runtime.py` covers model priority and missing unsafe weights path behavior.
- `cv/tests/test_logging.py` covers redaction helpers.
- `cv/tests/test_image_processing.py` covers no-detection success and multiple image failure cases.
- `cv/tests/test_video_processing.py` covers no-detection success and multiple video failure cases.

No command gates were run during this planning turn because user requested research/design/plan artifacts only.

## Unknowns and assumptions

Confirmed facts:

- Phase 20 validation requires safe failed-job messages, no-detection completion, worker logs for key lifecycle events/errors, no secrets or unsafe absolute paths in logs, and worker suite passing.
- Docs allow stack traces in worker logs but prohibit unsafe API responses.
- Docs require safe `error_message` on failed jobs.
- Docs do not require new schema fields, public API routes, frontend UI, or Docker changes for this phase.

Assumptions:

- Keep implementation inside existing worker modules unless a proven testability gap requires a small local helper.
- Use existing `status`, `error_message`, `completed_at`, `progress_percent`, `last_heartbeat_at`, and lock fields; no DB migration.
- Use tests rather than a separate manual log audit checklist where practical, because this contract turn must not create extra docs.
- Existing SQLite-backed worker tests are acceptable for most failure paths; use PostgreSQL-marked tests only for queue locking/recovery behavior.
- "Backend-created jobs" can be represented by worker test rows matching existing backend `media_files` and `processing_jobs` shape; no backend API changes are assumed.

Unknowns:

- Whether current tests already cover every Phase 20 failure case until focused gates run.
- Whether hidden tests expect `LOGGER.exception` stack traces for processing failures; docs say stack traces may be logged, not must.
- Whether DB write failure handling should fail open through stale recovery when `fail_processing_job` itself cannot write; docs do not define a second persistence channel.

## Files likely relevant for implementation

Primary worker files:

- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/logging.py`
- `cv/aerovision_worker/device.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/image_processing.py`
- `cv/aerovision_worker/video_processing.py`
- `cv/aerovision_worker/video_io.py`
- `cv/aerovision_worker/video_exports.py`
- `cv/aerovision_worker/video_persistence.py`
- `cv/aerovision_worker/video_types.py`

Primary tests:

- `cv/tests/test_startup.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_queue_postgres.py`
- `cv/tests/test_logging.py`
- `cv/tests/test_device.py`
- `cv/tests/test_model_runtime.py`
- `cv/tests/test_image_processing.py`
- `cv/tests/test_video_processing.py`

Reference-only files:

- `backend/app/db/models.py`
- `backend/app/services/jobs.py`
- `backend/app/services/results.py`
- `backend/tests/test_jobs_api.py`

Do not touch for Phase 20 unless a documented mismatch is proven:

- `docs/*`
- `frontend/*`
- `training/*`
- root Compose/runtime files
