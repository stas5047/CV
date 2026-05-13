## Phase 10 - Jobs, results, detections, tracks, and safe downloads API

**Direction:** Backend  
**Goal:** Implement job history, job details, result metadata, detections, tracks, summary, and download endpoints.

### Scope

- Implement endpoints:
  - `GET /api/jobs`;
  - `GET /api/jobs/{job_id}`;
  - `DELETE /api/jobs/{job_id}`;
  - `GET /api/jobs/{job_id}/summary`;
  - `GET /api/jobs/{job_id}/detections`;
  - `GET /api/jobs/{job_id}/tracks`;
  - `GET /api/jobs/{job_id}/result`;
  - `GET /api/jobs/{job_id}/download/media`;
  - `GET /api/jobs/{job_id}/download/csv`;
  - `GET /api/jobs/{job_id}/download/json`.
- Enforce ownership or admin access on every job/result/download route.
- Support pagination and filters for job lists.
- Hide soft-deleted jobs from normal user lists.
- Return status, progress, heartbeat, timestamps, summary, and safe download URLs/references.
- Serve downloads only after verifying that the file belongs to the requested job.
- Return clear missing-file errors without exposing internal paths.
- Treat no-detection completed jobs as successful results.
- Add tests for ownership, downloads, missing result files, and soft deletion/cancellation behavior.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Users list and view only own jobs.
- Admin can view all jobs through allowed permissions/routes.
- Result endpoints enforce ownership.
- Downloads enforce ownership and resource association.
- Absolute filesystem paths are not exposed.
- Completed no-detection jobs can still provide CSV/JSON downloads when files exist.
- Backend tests pass.

### Commit

`feat(backend-results): add jobs results detections tracks and downloads API`