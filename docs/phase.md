## Phase 13 - Backend contract, pagination, OpenAPI, and security test audit

**Direction:** Backend / QA  
**Goal:** Consolidate backend API behavior before worker and frontend implementation depend on it.

### Scope

- Audit all implemented endpoint paths against `API.md`.
- Ensure `/api` prefix is consistent.
- Ensure OpenAPI schemas are usable for frontend development.
- Normalize error response shapes for frontend Ukrainian localization.
- Ensure paginated list endpoints are consistent.
- Re-run auth, authorization, ownership, upload, model, job, result, admin, and experiment tests.
- Add missing tests for edge cases discovered during audit.
- Confirm API outputs do not expose absolute filesystem paths or forbidden CV-boundary fields.
- Update README/API notes with current commands and endpoint groups.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`

### Validation

- Backend lint/format/type-equivalent checks pass.
- Backend test suite passes.
- Manual OpenAPI route audit passes.
- Protected routes consistently reject missing/invalid tokens.
- Regular users cannot bypass ownership through filters or IDs.
- API/export boundary audit passes for implemented responses.

### Commit

`test(backend): audit API contract security and ownership coverage`