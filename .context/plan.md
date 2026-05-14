# Phase 20 Implementation Plan - Worker error handling, logging, and integration hardening

## Scope

Only Phase 20 CV worker/QA hardening. Do not modify product docs. Do not modify frontend, training, Docker, public API contracts, database schema, auth, upload, model registry, admin features, or unrelated backend code.

## Ordered atomic plan

1. `@role/developer-cv-worker` Re-read Phase 20 relevant docs before source edits.
   - Files: `docs/CV_PIPELINE.md`, `docs/ARCHITECTURE.md`, `docs/AUTH_SECURITY.md`, `docs/TESTING_QA.md`.
   - Verify: documented failure cases, safe logging rules, no-detection success rule, queue/heartbeat rules, and relative-path rules are noted.

2. `@role/tester` Run current focused worker baseline.
   - Command: `cd cv; python -m pytest tests/test_startup.py tests/test_queue.py tests/test_logging.py tests/test_device.py tests/test_model_runtime.py tests/test_image_processing.py tests/test_video_processing.py -q`
   - Verify: preserve output. PASS means patch only proven gaps. FAIL means use exact failure as implementation target.

3. `@role/developer-cv-worker` Audit failed-job state writer.
   - File: `cv/aerovision_worker/queue.py`
   - Verify: `fail_processing_job` sets `status = failed`, safe `error_message`, `completed_at`, `updated_at`, final heartbeat, and clears lock fields only for claimed processing jobs.
   - Verify: stale timeout failure uses safe fixed text and does not expose paths/secrets.

4. `@role/developer-cv-worker` Audit startup/model/device failure paths.
   - Files: `cv/aerovision_worker/main.py`, `cv/aerovision_worker/device.py`, `cv/aerovision_worker/model_runtime.py`.
   - Verify: `auto` CUDA fallback chooses CPU, forced `cuda` fails clearly, missing model weights fails claimed job with safe message, model load logs omit absolute paths, unsupported claimed media type fails safely.

5. `@role/developer-cv-worker` Audit image processing failure paths.
   - File: `cv/aerovision_worker/image_processing.py`
   - Verify: missing source, unsafe source path, corrupt/undecodable image, inference failure, output directory failure, annotated image write failure, CSV failure, JSON failure, and DB completion failure map to safe failed-job messages.
   - Verify: no-detection images stay on completed path and set final progress/timestamps.

6. `@role/developer-cv-worker` Audit video processing failure paths.
   - Files: `cv/aerovision_worker/video_processing.py`, `cv/aerovision_worker/video_io.py`, `cv/aerovision_worker/video_exports.py`, `cv/aerovision_worker/video_persistence.py`, `cv/aerovision_worker/video_types.py`.
   - Verify: missing source, unsafe source path, corrupt/unopened video, unsupported first-frame decode, tracker runtime failure, annotated video write failure, CSV failure, JSON failure, and DB completion failure map to safe failed-job messages.
   - Verify: no-detection videos stay completed, write exports, and set final progress/timestamps.

7. `@role/developer-cv-worker` Patch only documented gaps found in steps 3-6.
   - Allowed files: worker modules listed in steps 3-6.
   - Verify: no schema fields, routes, frontend UI, Docker services, or product docs are added.
   - Verify: no broad exception swallowing without safe logging and a deterministic failed-job update path.

8. `@role/tester` Add/tighten queue failure-state tests only if missing behavior is found.
   - File: `cv/tests/test_queue.py`
   - Verify: failed jobs have `status = failed`, `error_message`, `completed_at`, `updated_at`, `last_heartbeat_at`, and cleared locks.
   - Verify: stale timeout message is safe and retry behavior remains unchanged.

9. `@role/tester` Add/tighten startup/model/device tests only if missing behavior is found.
   - Files: `cv/tests/test_startup.py`, `cv/tests/test_device.py`, `cv/tests/test_model_runtime.py`.
   - Verify: missing model file fails job safely; forced CUDA unavailable fails clearly; `auto` CUDA unavailable selects CPU; logs do not expose absolute model path.

10. `@role/tester` Add/tighten image failure tests only if missing behavior is found.
    - File: `cv/tests/test_image_processing.py`
    - Verify: documented image failure cases mark job failed with safe messages that do not contain `storage_root`, model paths, DB URLs, passwords, tokens, or stack traces.
    - Verify: DB completion failure becomes safe failed job when the failure can be persisted.
    - Verify: no-detection image job remains completed with `progress_percent = 100`.

11. `@role/tester` Add/tighten video failure tests only if missing behavior is found.
    - File: `cv/tests/test_video_processing.py`
    - Verify: documented video failure cases mark job failed with safe messages that do not contain `storage_root`, model paths, DB URLs, passwords, tokens, or stack traces.
    - Verify: unsupported first-frame decode is distinct from unopened video when fixture supports it.
    - Verify: DB completion failure becomes safe failed job when the failure can be persisted.
    - Verify: no-detection video job remains completed with `progress_percent = 100`.

12. `@role/tester` Add/tighten logging tests or explicit manual log-audit assertions.
    - File: `cv/tests/test_logging.py`
    - Verify: redaction covers database URLs, password/token/secret assignments, JWT-like tokens, absolute Windows paths, absolute POSIX paths, and secret words.
    - Verify: worker lifecycle coverage includes selected CV device on startup, worker job claim, stale recovery, model loading, processing start/end with duration, export generation, and worker processing errors.
    - Verify: each lifecycle log either has automated assertion coverage or is named in the final implementation report with exact manual audit evidence.

13. `@role/tester` Add worker integration coverage with backend-shaped job rows where practical.
    - Files: existing worker tests, preferably `cv/tests/test_startup.py`, `cv/tests/test_image_processing.py`, or `cv/tests/test_video_processing.py`.
    - Verify: claimed jobs shaped like backend-created `media_files`/`processing_jobs` records complete or fail safely.
    - Verify: no backend source files are changed unless an actual backend contract mismatch is proven.

14. `@role/tester` Run focused worker hardening tests.
    - Command: `cd cv; python -m pytest tests/test_startup.py tests/test_queue.py tests/test_logging.py tests/test_device.py tests/test_model_runtime.py tests/test_image_processing.py tests/test_video_processing.py -q`
    - Expected: PASS.

15. `@role/tester` Run worker lint.
    - Command: `cd cv; python -m ruff check aerovision_worker tests`
    - Expected: PASS.

16. `@role/tester` Run PostgreSQL queue integration only if PostgreSQL is reachable or queue semantics changed.
    - Command: `cd cv; python -m pytest -m postgres -q`
    - Expected: PASS or `not available yet` with exact DB availability reason.

17. `@role/code-reviewer` Review changed files against Phase 20 docs.
    - Verify: no CV-only boundary violation.
    - Verify: no unsafe `error_message` persistence.
    - Verify: logs redact secrets and absolute paths.
    - Verify: lifecycle logging coverage from step 12 is satisfied for all Phase 20 validation events.
    - Verify: no-detection remains success.
    - Verify: no backend/frontend/schema/Docker/product-doc scope creep.

18. `@role/docs-maintainer` Decide docs/index updates.
    - Expected: skipped unless implementation changes commands, structure, environment variables, artifact layout, or documented paths.
    - Verify: final implementation report states docs/index updates skipped or lists exact index update.

## Relevant quality gates

- `cd cv; python -m pytest tests/test_startup.py tests/test_queue.py tests/test_logging.py tests/test_device.py tests/test_model_runtime.py tests/test_image_processing.py tests/test_video_processing.py -q`
- `cd cv; python -m ruff check aerovision_worker tests`
- `cd cv; python -m pytest -m postgres -q` only when PostgreSQL is reachable or queue semantics changed.

Not in scope:

- Backend full suite unless backend files change.
- Frontend checks.
- Docker Compose smoke unless runtime config changes.
- Training checks.

## Stop conditions

- Stop and report `WARNING: CONFLICT` if docs or code disagree on safe errors, no-detection success, relative paths, queue boundaries, or CV-only output.
- Stop before source edits if a required failure behavior needs a new schema field, new API route, or product behavior not documented.
- Do not mark complete with failing focused gates unless exact failing command/output is documented as blocker.
