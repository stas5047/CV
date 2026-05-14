# Phase 15 Design - PostgreSQL queue claiming, heartbeat, and stale job recovery

## Phase goal

Implement worker-side PostgreSQL queue reliability before any media processing work:

- poll for queued jobs;
- claim one queued job safely with row-level locking;
- update queue ownership fields;
- expose heartbeat/progress helpers;
- recover stale processing jobs;
- keep actual CV inference/tracking/export work out of this phase.

## Intended behavior from docs

Confirmed:

- Worker polls PostgreSQL for `queued` jobs.
- Worker claims jobs with `FOR UPDATE SKIP LOCKED`.
- Claim transaction is short.
- During claim, worker sets:
  - `status = processing`
  - `locked_by`
  - `locked_at`
  - `started_at`
  - `last_heartbeat_at`
- Media processing happens after claim commit, outside the claim transaction.
- Poll interval default is 2 seconds and comes from worker settings.
- Heartbeat/progress updates write `progress_percent` and `last_heartbeat_at`.
- Video heartbeat default rule is every 30 frames or 2 seconds, whichever comes first. Phase 15 should provide helper primitives; actual video loop belongs to later phases.
- Stale threshold default is 10 minutes.
- Max retries default is 2.
- Stale recovery:
  - reset stale `processing` jobs to `queued` and increment `retry_count` while retry count is below max;
  - mark stale jobs as `failed` with worker-timeout error when retry count reached max.
- Stale recovery must ignore soft-deleted jobs (`processing_jobs.deleted_at IS NULL`) and must update only rows that are still `status = 'processing'` at update time.
- Worker restart must not leave jobs stuck in `processing`.

Assumptions:

- Stale rows with `status = processing` and missing `last_heartbeat_at` count as stale for recovery.
- `completed_at` should remain unset when stale job is requeued and should be set when stale job is marked failed.
- `error_message` for timeout should be short and safe, without paths, stack traces, secrets, or tokens.

## Architecture decisions

- Keep queue logic inside `cv/`; do not add backend HTTP calls or worker-owned API routes.
- Use existing `create_session_factory()` and worker settings.
- Use PostgreSQL row-level locking for the claim query. SQLite-only behavior cannot prove `SKIP LOCKED`.
- Keep claim and stale-recovery DB transactions short and explicit.
- Do not import backend app modules into the worker package unless implementation discovers an existing supported shared contract. Current repo shape does not show a shared model package.
- Add a worker-local job processing hook or equivalent seam so tests can simulate processing outside the claim transaction without implementing CV inference.
- Main worker loop may recover stale jobs periodically and poll for queued jobs, but must not add Phase 16-18 behavior.
- If the Phase 15 runtime loop claims a real job before media processing exists, placeholder handling must fail the job safely with a short safe error message rather than leaving it permanently `processing`. Test-only hooks may simulate processing without writing detections/results.
- Logging should record claim/recovery/status events without DB URLs, secrets, tokens, absolute storage paths, or raw stack traces in API-visible data.

## Backend impact

- No backend route or service changes expected.
- Backend schema is used as DB contract reference.
- Existing job creation already creates queued jobs with needed defaults.

## Frontend impact

- No frontend changes expected.

## DB impact

- No migration expected.
- Phase uses existing `processing_jobs` fields and index:
  - `status`
  - `created_at`
  - `locked_by`
  - `locked_at`
  - `started_at`
  - `last_heartbeat_at`
  - `retry_count`
  - `progress_percent`
  - `error_message`
  - `completed_at`
  - `updated_at`

## API impact

- No public API contract changes expected.
- Existing job status endpoints may reflect worker-updated fields through already implemented backend schemas.

## Security/privacy impact

- Worker must not log secrets, raw tokens, DB passwords, or sensitive environment values.
- Worker must not expose absolute host/container paths through DB fields or logs.
- Failed stale jobs should store safe timeout errors only; timeout/placeholder error messages must be stable, short, and free of paths, DB URLs, secrets, tokens, and stack traces.
- Phase produces queue state only, not detection outputs, tracking outputs, or any targeting/navigation/control data.

## Test strategy

- Unit tests:
  - settings already covered; add tests only if settings behavior changes;
  - heartbeat/progress helper clamps or rejects invalid progress according to DB constraint expectations;
  - heartbeat/progress helper updates only when `job_id`, `locked_by`, and `status = processing` match;
  - stale recovery updates retry/failure fields correctly with controlled timestamps;
  - stale recovery ignores soft-deleted processing jobs;
  - stale recovery update statements guard on `status = processing` to avoid races.
- PostgreSQL integration tests when available:
  - oldest queued job is claimed first;
  - two worker sessions cannot claim the same job;
  - claim sets required fields;
  - transaction used for claim is not held during simulated processing;
  - stale job below retry limit resets to queued and increments retry count;
  - stale job at retry limit becomes failed.
- Main-loop tests:
  - `--check-once` still performs startup checks and exits;
  - worker loop can be exercised with injected stop condition or single-iteration helper without infinite test hangs;
  - shutdown behavior exits cleanly where practical.
- Relevant gates:
  - from `cv/`: `python -m ruff check .`
  - from `cv/`: `python -m pytest`
  - PostgreSQL queue integration command: start the Compose Postgres service and run the PostgreSQL-marked worker queue tests against `DATABASE_URL`:
    - root: `docker compose --env-file .env.example up -d postgres`
    - `cv/`: `python -m pytest -m postgres`
  - If this PostgreSQL gate is not available or cannot run in the implementation environment, Phase 15 must report it as a blocker for queue-reliability completion rather than a routine `not available yet`.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found.
- Ambiguity: prompt risk placeholder was not filled; design assumes `MEDIUM`.
- Ambiguity: docs do not define exact `locked_by` format.
- Ambiguity: docs do not require a specific stale-recovery trigger cadence beyond startup, periodic timer, or admin action. Worker startup plus periodic worker loop recovery is acceptable.
- Ambiguity: docs do not say whether `retry_count == max_retries` should fail before or after one more processing attempt. Architecture wording supports fail when retry count has reached max.
