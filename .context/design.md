# Phase 20 Design - Worker error handling, logging, and integration hardening

## Phase goal

Harden CV worker failure handling and logging before frontend flows depend on job status, progress, exports, and safe error messages.

## Intended behavior from docs

Confirmed facts:

- Worker must handle missing uploads, corrupted media, unsupported decode results, missing model files, CUDA availability problems, annotated output failures, export failures, and DB write failures.
- Failed jobs store clear safe `error_message`.
- Failed jobs set `status = failed` and update timestamp fields.
- Successful jobs set `completed_at` and final progress.
- No-detection jobs are successful `completed` jobs, not failures.
- Worker logs include selected device, job claim, model loading, processing start/end, export generation, and errors.
- Logs must not include passwords, JWT tokens, JWT secrets, database passwords, sensitive environment values, or unsafe absolute paths.
- API responses must not expose stack traces or unsafe internal paths.
- Backend and worker coordinate through PostgreSQL and shared storage, not HTTP job-loop calls.
- Worker stores relative result/export paths only.

Assumptions:

- Use existing worker error classes and `fail_processing_job` instead of adding schema/status/API concepts.
- Keep stack traces in logs only when useful for debugging and always behind existing redaction filter.
- Use safe generic error strings for persisted `error_message`; detailed exception text stays out unless already safe and intentional.
- Integration hardening can use worker-side tests with DB rows shaped like backend-created jobs.

WARNING: CONFLICT:

- Current-state documentation differs: `docs/index.md` and `backend/index.md` understate worker implementation, while `cv/index.md` and actual worker files show queue/processing/export behavior. No Phase 20 product-rule conflict found.

## Architecture decisions

- Keep failure handling inside CV worker modules. Backend remains API/authorization/download authority and does not process worker failures.
- Keep queue state in existing `processing_jobs` fields. No migration.
- Keep `fail_processing_job` as canonical failed-state writer.
- Keep completion persistence atomic per job completion where current code already does so.
- Keep no-detection path on normal success path; do not special-case it as error handling.
- Keep logging through `aerovision_worker.logging.configure_logging` and `RedactionFilter`.
- Prefer focused tests over manual-only audit because failure behavior is deterministic and worker-local.
- Do not add Celery, Redis, HTTP worker callbacks, frontend UI, new API routes, or new public behavior.

## Backend impact

Expected impact:

- No backend source changes.
- Backend job/detail/download APIs may surface `error_message` already stored by worker, so worker must keep persisted text safe.

Do not change:

- Auth, ownership, API routes, schemas, downloads, or admin endpoints unless a proven safety mismatch is found.

## Frontend impact

Expected impact:

- None. Frontend phases are later.
- No Ukrainian UI work in Phase 20.

## DB impact

Expected impact:

- No schema changes.
- Worker updates existing `processing_jobs.status`, `error_message`, `completed_at`, `updated_at`, `progress_percent`, `last_heartbeat_at`, `locked_by`, `locked_at`, result/export paths, and summary fields.
- Worker inserts/clears existing `detections` and `tracks` only on successful completion.

DB invariants:

- Failed jobs must not store absolute paths or secrets in `error_message`.
- Completed jobs must use relative result/export paths only.
- No-detection completed jobs must keep zero/null summary values where applicable.

## API impact

Expected impact:

- No route or schema changes.
- Existing API responses must remain safe because worker-persisted `error_message` is safe and stack traces are not stored.

## Security/privacy impact

Touched security/privacy surfaces:

- Worker logs.
- Worker persisted `error_message`.
- Result/export path persistence.
- Model path and database error handling.

Rules:

- Do not log secrets, tokens, passwords, password hashes, database passwords, JWT secrets, sensitive env values, or unsafe absolute paths.
- Do not store stack traces in `processing_jobs.error_message`.
- Do not expose absolute host/container paths in DB fields or export contents.
- Do not execute uploaded files.
- Keep outputs inside CV-only boundary.

## Test strategy

Focused worker checks:

- `cd cv; python -m pytest tests/test_startup.py tests/test_queue.py tests/test_logging.py tests/test_device.py tests/test_model_runtime.py tests/test_image_processing.py tests/test_video_processing.py -q`
- `cd cv; python -m ruff check aerovision_worker tests`

Optional integration check when PostgreSQL is reachable:

- `cd cv; python -m pytest -m postgres -q`

Targeted assertions to keep/add:

- Missing image/video source marks job failed with safe message.
- Corrupt image/video and unsupported decode result mark job failed with safe message.
- Missing model weights mark job failed with safe message.
- `CV_DEVICE=auto` falls back to CPU when CUDA unavailable.
- forced `CV_DEVICE=cuda` fails clearly before unsafe processing.
- Annotated output write failure marks job failed safely.
- CSV/JSON export failure marks job failed safely.
- DB completion write failure marks job failed safely when possible.
- Failed jobs set `status = failed`, `error_message`, `completed_at`, `updated_at`, and release locks.
- Successful image/video jobs set `completed_at`, `progress_percent = 100`, and final heartbeat.
- No-detection image/video jobs stay `completed`.
- Logs redact database URLs, passwords, tokens, secrets, and absolute paths.
- Lifecycle log coverage is verified by assertions or a manual log-audit note for selected CV device on startup, worker job claim, stale recovery, model loading, processing start/end with duration, export generation, and worker processing errors.

Checks not required unless related files change:

- Backend full suite.
- Frontend build/tests.
- Docker Compose smoke.
- Training checks.

## Ambiguities or conflicts

WARNING: CONFLICT:

- `docs/index.md` current-state section conflicts with `cv/index.md` and actual worker files about implemented queue/inference/export behavior.
- `backend/index.md` also says worker queue/CV/export behavior comes later, conflicting with actual worker state.

Ambiguities:

- User-provided risk placeholder was unset; plan assumes MEDIUM risk.
- Docs allow but do not require stack traces in worker logs. Implementation should not add noisy stack traces unless needed to diagnose a known failure, and must never persist them.
- Docs do not define behavior when the database is unavailable while attempting to mark a job failed. Implementation should log safely and rely on stale recovery once DB connectivity returns, unless an existing retry point can update the job safely.
