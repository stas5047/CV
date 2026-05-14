## Phase 20 - Worker error handling, logging, and integration hardening

**Direction:** CV Worker / QA
**Goal:** Harden worker behavior before connecting frontend flows.

### Scope

- Audit worker failure handling for:
  - missing uploaded file;
  - corrupted image;
  - corrupted video;
  - unsupported decode result;
  - missing model file;
  - CUDA unavailable;
  - failed annotated output write;
  - failed export generation;
  - database write failures.
- Store safe `error_message` for failed jobs.
- Keep stack traces in worker logs only, not unsafe API responses.
- Ensure successful jobs set `completed_at` and final progress.
- Ensure failed jobs set `status = failed` and updated timestamp.
- Ensure no-detection jobs are never marked failed solely because no detections were found.
- Add logging tests or manual log audit checklist.
- Add worker integration tests with backend-created jobs where practical.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Failure cases produce safe job error messages.
- No-detection jobs still complete.
- Worker logs include device selection, job claim, model loading, processing start/end, exports, and errors.
- Worker logs do not include secrets or unsafe user-facing absolute paths.
- Worker test suite passes.

### Commit

`test(worker): harden CV worker errors logging and integration behavior`
