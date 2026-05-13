# Phase 10 Implementation Plan

## Scope

Phase only: Phase 10 - Jobs, results, detections, tracks, and safe downloads API.

Do not implement:

- CV worker queue polling, media processing, export generation, or stale recovery;
- frontend job/result pages;
- experiments/admin APIs;
- model registry changes;
- storage cleanup;
- training launch or training utilities;
- new database fields unless a verified schema mismatch blocks Phase 10;
- product doc changes.

## Ordered atomic plan

1. [@role/developer-backend] Re-read Phase 10 contract before coding.
   - Verify `docs/phase.md` still says Phase 10.
   - Verify relevant docs remain `docs/API.md`, `docs/DATA_MODEL.md`, `docs/AUTH_SECURITY.md`, `docs/CV_PIPELINE.md`, and `docs/TESTING_QA.md`.
   - Verifiable: no source change in this step.

2. [@role/developer-backend] Inspect current job/media/model patterns.
   - Read current jobs router/service/schemas, media list/detail/delete service, models list service, storage path helpers, auth dependency, and jobs tests.
   - Verifiable: exact helper reuse and schema style identified before edits.

3. [@role/tester] Add focused failing Phase 10 tests first.
   - Extend `backend/tests/test_jobs_api.py` or add `backend/tests/test_job_results_api.py`.
   - Cover job list/detail/delete, summary, detections, tracks, result metadata, downloads, ownership, admin visibility, inactive-user rejection, missing files, no-detection behavior, and path secrecy.
   - Include at least one inactive-user test for a representative result route and one inactive-user test for a download route.
   - Verifiable: targeted tests fail because Phase 10 endpoints/service behavior do not exist yet.

4. [@role/developer-backend] Add response/list schemas.
   - Add paginated jobs list response.
   - Add detail/summary/result metadata schemas using documented fields only.
   - Add detection response with derived `center_x`, `center_y`, `bbox_width`, and `bbox_height`.
   - Add track response with documented track summary fields.
   - Do not expose raw stored relative paths or absolute paths in public JSON.
   - Verifiable: schema tests/API assertions show safe fields only.

5. [@role/developer-backend] Add authorized job lookup helper.
   - Load job with related media/model where useful.
   - Enforce active user plus owner/admin access.
   - Return safe 404 for missing/cross-owner inaccessible jobs.
   - Decide and encode soft-deleted job detail behavior conservatively.
   - Verifiable: cross-owner job detail/result/download tests return safe not-found and no data.

6. [@role/developer-backend] Implement `GET /api/jobs` service logic.
   - Support `limit` and `offset`.
   - Support documented filters where practical: status, media type, date, model version, owner for admins.
   - Hide `deleted_at` jobs from normal user lists.
   - Restrict regular users to own jobs regardless of filters.
   - Verifiable: list tests prove user scope, admin scope, filters, pagination, and soft-delete hiding.

7. [@role/developer-backend] Implement `GET /api/jobs/{job_id}` service logic.
   - Return job status, progress, heartbeat, timestamps, input params, summary, safe result/download references, and media/model references where useful.
   - Do not expose result/export storage paths.
   - Verifiable: detail tests inspect fields and confirm no absolute paths, raw path fields, or raw storage field names such as `result_media_path`, `csv_path`, and `json_path`.

8. [@role/developer-backend] Implement `DELETE /api/jobs/{job_id}` behavior.
   - Apply doc-consistent soft-delete/cancellation behavior.
   - Do not physically delete files.
   - Do not require hard interruption of processing jobs.
   - Verifiable: delete tests prove ownership, idempotent/safe outcome as designed, list hiding, and no file removal.

9. [@role/developer-backend] Implement summary endpoint.
   - Return `processing_jobs.summary_json` with job status context as needed.
   - Treat missing summary on non-completed/failed jobs as safe empty/null metadata, not server error.
   - Keep no-detection summary valid with null confidence values.
   - Verifiable: summary tests cover completed no-detection and missing summary cases.

10. [@role/developer-backend] Implement detections endpoint.
    - Query `detections` by authorized `job_id`.
    - Support pagination if result size can grow.
    - Optionally support documented detection filters: frame index, confidence range, track ID.
    - Compute derived center/size values from bbox corners.
    - Verifiable: detection tests prove job scoping, derived values, pagination/filtering, and empty no-detection response.

11. [@role/developer-backend] Implement tracks endpoint.
    - Query `tracks` by authorized `job_id`.
    - Return documented track summary fields.
    - Return empty list for image/no-track/no-detection jobs.
    - Verifiable: track tests prove job scoping, data shape, and empty list behavior.

12. [@role/developer-backend] Implement result metadata endpoint.
    - Return result availability and safe download URLs/references for annotated media, CSV, and JSON.
    - Define `available` as file-present availability: the path is recorded, passes job-specific association, resolves under `STORAGE_ROOT`, and exists as a file.
    - Include job/media/model/summary references needed by frontend without storage internals.
    - Do not expose missing-file internal paths when checking availability.
    - Verifiable: result metadata tests confirm safe references, file-present availability semantics, no raw storage field names, and no path leakage.

13. [@role/developer-auth-security] Implement download file resolution helper.
    - Re-check job ownership/admin access.
    - Select only one of the job-owned path fields: `result_media_path`, `csv_path`, or `json_path`.
    - Validate relative path and safe-join under `STORAGE_ROOT`.
    - Require selected result/export path to live under `results/{job_id}/` for the requested job.
    - Verify file exists and is a file.
    - Use sanitized download filename.
    - Return safe missing-file errors with no internal path.
    - Verifiable: download tests cover success, missing file, cross-owner, path traversal/absolute path rejection, wrong-job result directory rejection, inactive-user rejection, and no path leakage.

14. [@role/developer-backend] Add download routes.
    - Add:
      - `GET /api/jobs/{job_id}/download/media`
      - `GET /api/jobs/{job_id}/download/csv`
      - `GET /api/jobs/{job_id}/download/json`
    - Set appropriate media types for image/video/csv/json where practical.
    - Verifiable: TestClient downloads fixture files from authorized jobs.

15. [@role/tester] Verify no-detection completed-job behavior.
    - Seed completed job with `summary_json.total_detections = 0`, null confidence values, empty detections/tracks, and CSV/JSON fixture paths.
    - Assert summary/result/detections/tracks/downloads behave as successful result.
    - Verifiable: no-detection tests pass without failed-job or error semantics.

16. [@role/tester] Run targeted Phase 10 gate.
    - Command from `backend/`: `python -m pytest tests/test_jobs_api.py`
    - If separate file added: `python -m pytest tests/test_job_results_api.py`
    - Expected: PASS after implementation.

17. [@role/tester] Run related security/regression gates.
    - Command from `backend/`: `python -m pytest tests/test_media_api.py tests/test_auth.py tests/test_security_utils.py`
    - Expected: PASS.
    - Reason: Phase 10 depends on ownership, auth, and path safety.

18. [@role/tester] Run lint gate.
    - Command from `backend/`: `python -m ruff check .`
    - Expected: PASS.

19. [@role/code-reviewer] Review Phase 10 diff against docs.
    - Check endpoint list matches `docs/phase.md` and `docs/API.md`.
    - Check ownership/admin access on every route.
    - Check soft-deleted jobs hidden from normal lists.
    - Check no absolute paths or raw storage paths in JSON responses.
    - Check downloads verify job association and path safety.
    - Check association rejects paths outside `results/{job_id}/`.
    - Check inactive users cannot access representative result/download routes.
    - Check no-detection results are not treated as failures.
    - Check detections/tracks stay CV-only and image-space.
    - Check no worker/frontend/later-phase functionality leaked in.
    - Verifiable: review notes no blocking doc mismatch, or blocker cites exact file/doc rule.

20. [@role/docs-maintainer] Update backend index only if implementation changes file inventory.
    - Update `backend/index.md` if new result/service/schema/test files are added.
    - Do not modify product docs under `docs/`.
    - Verifiable: docs change, if any, is limited to backend-local index.
