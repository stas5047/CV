# Phase 15 Plan - PostgreSQL queue claiming, heartbeat, and stale job recovery

## Scope guard

- Phase only: worker queue claiming, heartbeat/progress helpers, stale recovery, practical shutdown.
- No backend API changes.
- No frontend changes.
- No DB migration unless implementation proves existing schema cannot satisfy docs.
- No model loading, YOLO inference, image/video processing, tracking, detections, exports, result media writes, or no-detection result generation.

## Ordered implementation plan

1. `@role/developer-cv-worker` Add focused worker queue code in `cv/aerovision_worker/` using existing DB/session helpers.
   - Verifiable: worker package still imports without backend package imports.

2. `@role/developer-cv-worker` Define worker job claim result shape with existing `processing_jobs` fields only.
   - Verifiable: no new schema fields, routes, or product states.

3. `@role/developer-cv-worker` Implement queued-job claim query.
   - Select oldest non-deleted `status = 'queued'` job ordered by `created_at`.
   - Use `FOR UPDATE SKIP LOCKED` for PostgreSQL.
   - Set `status`, `locked_by`, `locked_at`, `started_at`, `last_heartbeat_at`, and `updated_at` in same short transaction.
   - Verifiable: test sees claimed row moved to `processing` with all required fields set.

4. `@role/developer-cv-worker` Ensure claim returns no job cleanly when queue is empty.
   - Verifiable: empty queue test returns no claimed job and makes no DB changes.

5. `@role/developer-cv-worker` Add heartbeat/progress update helper.
   - Update `progress_percent`, `last_heartbeat_at`, and `updated_at` only for a row matching `job_id`, current worker `locked_by`, and `status = 'processing'`.
   - Keep progress within `0..100`.
   - Return or report no update when ownership/status guard fails so stale or superseded workers cannot refresh another worker's claim.
   - Verifiable: helper test updates heartbeat timestamp and progress for the owner and refuses mismatched `locked_by`.

6. `@role/developer-cv-worker` Add stale job recovery helper.
   - Find stale `processing` jobs older than configured threshold with `deleted_at IS NULL`.
   - Treat missing heartbeat on processing rows as recoverable stale state.
   - Update rows only while they still match `status = 'processing'` to avoid racing active heartbeats or another recovery pass.
   - If `retry_count < max_retries`, set job back to `queued`, increment `retry_count`, clear `locked_by`, `locked_at`, `started_at`, and heartbeat fields, clear previous worker error if appropriate, update `updated_at`.
   - If `retry_count >= max_retries`, set `status = failed`, stable safe timeout `error_message`, `completed_at`, clear lock fields, update `updated_at`.
   - Verifiable: tests cover reset path, fail path, soft-deleted ignored path, and status guard.

7. `@role/developer-cv-worker` Add polling loop integration in `cv/aerovision_worker/main.py`.
   - Run startup checks as today.
   - Run stale recovery on startup and periodically during loop.
   - Poll queued jobs using configured interval.
   - Hand claimed job to a worker-local processing hook or simulated handler boundary without implementing CV processing.
   - Runtime placeholder for real claimed jobs must fail safely with a stable non-sensitive "processing not implemented in this phase" style error instead of leaving jobs permanently `processing`.
   - Verifiable: loop can be tested with injected single-iteration/stop behavior and does not hang tests.

8. `@role/developer-cv-worker` Add practical shutdown handling.
   - Let worker stop cleanly on keyboard interrupt or termination path supported by current entrypoint.
   - Do not invent cancellation semantics for active DB jobs beyond stale recovery.
   - Verifiable: shutdown test or code path review confirms no infinite test-only hard exit.

9. `@role/tester` Add queue unit tests in `cv/tests/`.
   - Cover empty queue, oldest queued claim, required claim fields, heartbeat/progress update, stale reset, stale fail, and no backend imports.
   - Verifiable: `python -m pytest` from `cv/` passes.

10. `@role/tester` Add PostgreSQL-specific concurrency coverage when available.
    - Two sessions/workers attempt to claim queued jobs.
    - Assert same job is not claimed twice.
    - Assert claim transaction is committed before simulated processing starts.
    - Use Compose Postgres as the concrete integration path unless implementation discovers an existing better project harness:
      - root: `docker compose --env-file .env.example up -d postgres`
      - `cv/`: `python -m pytest -m postgres`
    - If this PostgreSQL gate cannot run, report Phase 15 queue-reliability completion as blocked with exact reason; SQLite/unit tests alone do not satisfy this phase.

11. `@role/docs-maintainer` Update `cv/index.md` only if implementation changes current worker command behavior or current file list.
    - Verifiable: index remains a narrow folder summary, not duplicated product docs.

12. `@role/code-reviewer` Review Phase 15 diff against docs.
    - Check no HTTP backend-worker job loop.
    - Check no Celery/Redis.
    - Check no later-phase CV processing.
    - Check no secret/path leakage in logs/errors.
    - Check DB transactions are short.
    - Check stale recovery cannot leave jobs permanently stuck.

13. `@role/tester` Run relevant gates.
    - `cd cv; python -m ruff check .` -> `PASS` required when available.
    - `cd cv; python -m pytest` -> `PASS` required when available.
    - `docker compose --env-file .env.example up -d postgres` from repo root -> `PASS` required for PostgreSQL queue validation unless environment blocks Docker/Postgres.
    - `cd cv; python -m pytest -m postgres` -> `PASS` required for PostgreSQL queue validation after tests are added.

14. `@role/developer-cv-worker` Record blockers only if relevant gates fail or PostgreSQL integration cannot be run.
    - Verifiable: final implementation report includes exact failing command or `not available yet`.
