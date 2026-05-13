## Phase 11 - Admin backend APIs and safe storage cleanup

**Direction:** Backend / Admin  
**Goal:** Implement admin-only global statistics, global history, basic user list, and conservative storage cleanup.

### Scope

- Implement endpoints:
  - `GET /api/admin/stats`;
  - `GET /api/admin/jobs`;
  - `GET /api/admin/users`;
  - `POST /api/admin/storage/cleanup`.
- Enforce admin role explicitly on all admin endpoints.
- Provide global processing statistics and recent global job history.
- Provide basic user list without password hashes or sensitive fields.
- Implement conservative cleanup rules.
- Cleanup must not remove:
  - active model weights;
  - model cards for active models;
  - files referenced by non-deleted records;
  - recent user results accidentally;
  - files needed by visible completed jobs.
- Log cleanup actions safely.
- Add admin/regular-user access tests and cleanup safety tests.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Regular users cannot access admin routes.
- Admin can view global stats, jobs, and basic users.
- Cleanup dry-run or conservative mode works if implemented.
- Cleanup does not delete referenced files or active model artifacts.
- Admin endpoint tests pass.

### Commit

`feat(backend-admin): add admin stats users jobs and safe storage cleanup`