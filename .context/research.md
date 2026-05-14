# Phase 15 Research - PostgreSQL queue claiming, heartbeat, and stale job recovery

## Current phase

- Confirmed current phase: `Phase 15 - PostgreSQL queue claiming, heartbeat, and stale job recovery`
- Source: `docs/phase.md`
- Direction: CV Worker / Queue
- Goal from docs: reliable PostgreSQL job queue behavior before media processing
- Risk level: assumed `MEDIUM` because current user prompt left risk placeholder unfilled and phase touches DB concurrency, worker state transitions, and stale-job recovery

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout is dirty before this planning work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Existing `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/status.md`, and review artifacts are empty at read time.
- `cv/index.md` says current worker has settings, secret-safe logging, device selection, database helpers, storage path safety, startup checks, Docker entrypoint, and tests.
- `cv/index.md` also says queue claiming, inference, tracking, exports, and result writes are not implemented yet.
- `cv/aerovision_worker/settings.py` already defines:
  - `WORKER_POLL_INTERVAL_SECONDS`, default `2`
  - `WORKER_HEARTBEAT_FRAMES`, default `30`
  - `WORKER_HEARTBEAT_SECONDS`, default `2`
  - `WORKER_STALE_JOB_MINUTES`, default `10`
  - `WORKER_MAX_RETRIES`, default `2`
- `cv/aerovision_worker/database.py` already provides SQLAlchemy engine/session factory helpers and DB availability checks.
- `cv/aerovision_worker/main.py` currently runs startup checks, logs selected device, checks DB, then idles forever with `worker_idle processing_not_implemented_in_phase_14`.
- `backend/app/db/models.py` already has `processing_jobs` fields required by Phase 15:
  - `status`
  - `progress_percent`
  - `last_heartbeat_at`
  - `locked_by`
  - `locked_at`
  - `retry_count`
  - `started_at`
  - `completed_at`
  - `deleted_at`
  - `created_at`
  - `updated_at`
- Initial migration already creates those fields and `ix_processing_jobs_status_created_at`.
- `backend/app/services/jobs.py` already creates jobs with `status="queued"`, `progress_percent=0`, and `retry_count=0`.
- `cv/pyproject.toml` already includes SQLAlchemy, psycopg, pytest, and ruff.

## Existing implementation state

- Worker can start and validate DB connectivity.
- Worker has no queue claim function.
- Worker has no polling loop that queries `processing_jobs`.
- Worker has no heartbeat/progress update helper.
- Worker has no stale recovery helper.
- Worker has no two-worker concurrency test.
- Worker has no actual image/video processing yet; that belongs to later phases.
- Backend data model appears ready for this phase; no schema migration is expected for Phase 15.
- Frontend is not relevant to this phase.
- API route changes are not expected for this phase.

## Unknowns and assumptions

- Assumption: risk level is `MEDIUM`; user prompt did not replace `<LOW | MEDIUM | HIGH>`.
- Assumption: Phase 15 implementation should keep the worker package independent from backend Python imports and interact with PostgreSQL through SQLAlchemy using worker-local query code.
- Assumption: `locked_by` can be a generated per-process worker identifier; docs require the field to be set but do not define a specific format.
- Assumption: stale `processing` jobs with `last_heartbeat_at IS NULL` should be recoverable to avoid permanent stuck jobs from older or partial runs.
- Assumption: Phase 15 may use simulated processing in tests to prove claim transaction boundaries, but must not implement model loading, image processing, video processing, tracking, detections, or exports.
- Unknown: whether the implementation environment will have a real PostgreSQL test service available for `FOR UPDATE SKIP LOCKED` concurrency tests.
- Unknown: whether SQLite fallback tests are acceptable for non-locking helper behavior. PostgreSQL-specific behavior still needs a real PostgreSQL check when available.

## Files likely relevant for implementation

- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/database.py`
- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/logging.py`
- `cv/pyproject.toml`
- `cv/tests/`
- `cv/index.md`
- `backend/app/db/models.py` for schema reference only
- `backend/migrations/versions/20260513_0001_initial_schema.py` for migration/schema reference only

## Conflicts

- No `WARNING: CONFLICT` found between `docs/phase.md`, `docs/ROADMAP.md`, and consulted phase-relevant docs.
