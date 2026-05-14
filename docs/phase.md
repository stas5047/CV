## Phase 23 - Backend-worker end-to-end integration smoke

**Direction:** Backend / CV Worker / QA
**Goal:** Verify that backend-created jobs are processed by the worker and returned through the API.

### Scope

- Run clean database and shared storage with backend and worker.
- Upload a valid image through backend API.
- Create a processing job through backend API.
- Let worker claim and process the job.
- Verify job details, summary, detections, tracks, result metadata, and downloads through backend API.
- Repeat for a valid video fixture when feasible.
- Verify no-detection fixture behavior.
- Verify failed-job behavior for corrupted media or missing model file.
- Verify ownership restrictions for results and downloads.
- Add integration smoke scripts or pytest markers as practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Image upload -> job -> worker -> result -> download flow works.
- Video upload -> job -> worker -> result -> download flow works or blocker is documented with exact command/log.
- No-detection flow completes successfully.
- Another user cannot access job details or downloads.
- CSV and JSON exports are downloadable.
- CPU mode works.

### Commit

`test(integration): verify backend worker media processing flow`
