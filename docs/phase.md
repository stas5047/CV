## Phase 33 - Final full-stack QA, security audit, and release readiness

**Direction:** QA / Release
**Goal:** Verify the complete MVP against documented acceptance criteria.

### Scope

- Run backend tests.
- Run worker tests.
- Run frontend lint/typecheck/build/tests where configured.
- Run clean-volume Docker startup smoke.
- Execute manual E2E scenarios:
  - regular user image processing;
  - regular user video processing;
  - no-detection result;
  - admin model management;
  - admin experiments;
  - stale job recovery.
- Verify authentication and public registration toggle.
- Verify seeded admin login.
- Verify authorization and ownership for media, jobs, results, and downloads.
- Verify upload validation and path traversal rejection.
- Verify model selection priority.
- Verify CSV and JSON export contracts.
- Verify frontend Ukrainian text, loading states, error states, and empty states.
- Verify admin-only features are protected.
- Verify logs do not contain secrets or tokens.
- Verify API responses and exports remain inside the CV-only boundary.
- Audit absent out-of-scope features.
- Update final README and known limitations.

### Relevant docs

- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/FRONTEND_UX.md`
- all implementation docs

### Validation

- `docker compose up --build` reaches a usable app after documented setup.
- PostgreSQL, backend, CV worker, frontend, migrations, seed/setup, and storage initialization work together.
- Seeded admin can log in.
- Public registration works when enabled and is forbidden when disabled.
- User can upload and process image and video files.
- Worker reliably moves jobs from queued to processing to completed/failed.
- Progress updates during video processing.
- No-detection jobs complete successfully.
- Result media, CSV, and JSON downloads work.
- Admin model and experiment flows work.
- Ukrainian UI audit passes.
- Security and safety boundary audits pass.
- Remaining failures, if any, are documented as blockers with exact commands/logs.

### Commit

`chore(release): complete full-stack QA and release readiness audit`
