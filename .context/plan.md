# Phase 23 Plan

## Scope

Only Phase 23: backend-worker end-to-end integration smoke. No frontend work, no schema changes, no new product APIs, no product-doc edits, no training work.

## Ordered Atomic Steps

1. `@role/tester` Re-check repo state.
   - Run: `git status --short`
   - Verify: only expected pre-existing modified files plus planned Phase 23 test/script changes appear.

2. `@role/tester` Confirm Compose contract.
   - Run: `docker compose --env-file .env.example config`
   - Verify: command passes; backend and `cv-worker` both mount `/app/storage`; `CV_DEVICE=cpu`.

3. `@role/tester` Define clean integration environment.
   - Use isolated test database/schema and isolated temp/shared storage for automated smoke.
   - Ensure setup removes stale jobs, stale model rows, stale result files, and generated media for the smoke scope only.
   - If clean environment cannot be prepared, stop and document exact Docker/local blocker.
   - Verify: smoke cannot pass because of pre-existing local state.

4. `@role/tester` Pick smoke harness location from existing repo areas.
   - Prefer existing `scripts/` for manual Docker/API smoke or existing `backend/tests/` / `cv/tests/` for pytest smoke.
   - Verify: no new top-level folder.

5. `@role/developer-backend` Map existing backend API setup helpers needed by smoke.
   - Read only current auth/media/jobs/model helpers/tests.
   - Verify: smoke can create/login user, upload media, create job, query results, and download files through existing endpoints.

6. `@role/developer-cv-worker` Map worker callable path for deterministic smoke.
   - Use existing worker queue/poll/processing entry points.
   - Verify: smoke can run one worker iteration against same database/storage used by backend API.

7. `@role/tester` Build clean test fixture strategy.
   - Use generated valid PNG image fixture.
   - Use generated tiny MP4 fixture only if OpenCV codec support is available; otherwise document exact blocker.
   - Do not commit generated media.
   - Verify: uploaded media pass backend validation.

8. `@role/tester` Build deterministic model strategy.
   - For automated smoke, use test-only fake model object if no valid local YOLO weights are available.
   - Fake model may replace only inference output; smoke must still use real backend routes, real database queue rows, real worker dispatch/write path, real storage writes, and real backend export/download checks.
   - For manual Docker real-inference smoke, require external valid weights under ignored `storage/models/`.
   - Verify: no model weights are committed.

9. `@role/developer-backend` Add or update integration smoke for image success flow.
   - Flow: register/login user -> upload valid image -> register/activate model if needed -> create job -> run worker iteration -> fetch job detail/summary/detections/result metadata -> download media/CSV/JSON.
   - Verify: job reaches `completed`, progress is `100`, result refs available, downloads return 200, API response text has no absolute storage path.

10. `@role/developer-cv-worker` Add or update integration smoke for no-detection flow.
   - Flow: upload no-detection fixture -> create job -> run worker iteration -> fetch summary/detections/tracks/downloads.
   - Verify: status `completed`, `total_detections = 0`, empty detections/tracks, CSV headers exist, JSON `detections` array is empty, annotated media result/download exists when output creation is possible.
   - If annotated media cannot be created because of codec/image writer limits, document exact command/log blocker.

11. `@role/developer-cv-worker` Add or update integration smoke for failed-job behavior.
    - Use missing model file or corrupted accepted media fixture.
    - Verify: worker marks job `failed`; backend job detail/result exposes safe error/status; API response has no stack trace or absolute path.

12. `@role/developer-auth-security` Add or update ownership smoke.
    - Flow: second user attempts job detail/result/download for first user's completed job.
    - Verify: cross-owner requests for job detail, summary, detections, tracks, result metadata, annotated media download, CSV download, and JSON download return not found/forbidden behavior without leaking existence or paths.

13. `@role/developer-cv-worker` Add video smoke if feasible.
    - Flow: upload valid tiny video -> create job -> run worker iteration -> fetch detail/progress/summary/detections/tracks/downloads.
    - Verify: job completes, annotated MP4/CSV/JSON available, progress updates observed when practical, track rows exist when fake/real tracker produces IDs.
    - If not feasible: record blocker with exact codec/model/runtime reason and command/log.

14. `@role/tester` Run targeted backend gates if backend tests/scripts changed.
    - From `backend/`: `python -m ruff check .`
    - From `backend/`: `python -m pytest tests/test_jobs_api.py tests/test_media_api.py tests/test_api_contract.py`
    - Verify: PASS or exact blocker.

15. `@role/tester` Run targeted worker gates if worker tests/scripts changed.
    - From `cv/`: `python -m ruff check .`
    - From `cv/`: `python -m pytest tests/test_startup.py tests/test_queue.py tests/test_image_processing.py tests/test_video_processing.py`
    - Verify: PASS or exact blocker.

16. `@role/tester` Run PostgreSQL queue integration when PostgreSQL is reachable.
    - From `cv/`: `python -m pytest -m postgres`
    - Verify: PASS, or `not available yet`/blocker with exact database connection reason.

17. `@role/tester` Run new Phase 23 smoke command.
    - Command depends on chosen harness in step 4.
    - Verify: clean environment setup, image success, no-detection including annotated media when possible, failed-job safety, complete result-route ownership, CPU mode all pass.

18. `@role/code-reviewer` Review Phase 23 changes only.
    - Verify: no product API/schema/frontend/training behavior added.
    - Verify: backend/worker boundary remains PostgreSQL/shared-storage only.
    - Verify: CV-only output boundary preserved.
    - Verify: no secrets, tokens, raw passwords, absolute paths, generated media, or weights in tracked files.

19. `@role/docs-maintainer` Decide docs/index updates.
    - Product docs must not be modified in this planning task.
    - During implementation, update only component index/README if a new smoke command is added and docs update is explicitly in scope.
    - Verify: no product docs changed without user approval.

20. `@role/tester` Final status report.
    - Include files changed.
    - Include command results as `PASS`/`FAIL`/`not available`.
    - Include security/privacy result.
    - Include documented blockers, especially missing weights or video codec limits.

## Relevant Checks Only

- `docker compose --env-file .env.example config`
- Backend targeted lint/tests only if backend area changes.
- Worker targeted lint/tests only if worker area changes.
- PostgreSQL queue marker when database reachable.
- New Phase 23 smoke command.
- Docker-backed real-inference smoke is not mandatory when valid model weights are unavailable; pytest smoke is acceptable if it uses real backend routes, PostgreSQL, isolated shared storage, and worker polling.

Excluded checks:

- Frontend build/tests.
- Training tests.
- GPU launch.
- Full release QA.
