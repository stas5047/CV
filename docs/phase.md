## Phase 6 - Authorization, ownership, CORS, path safety, and security utilities

**Direction:** Backend / Security  
**Goal:** Add reusable authorization and safety primitives before implementing protected product APIs.

### Scope

- Add role-check dependency for admin-only endpoints.
- Add reusable ownership-check helpers for user-owned resources.
- Add account-active enforcement for protected routes.
- Add safe path utilities:
  - relative path validation;
  - path traversal prevention;
  - safe join under `STORAGE_ROOT`;
  - safe download filename handling.
- Add upload filename sanitization helper.
- Add CORS validation using explicit configured origins.
- Add secure error response patterns that do not expose stack traces.
- Add logging helpers/events that omit secrets and tokens.
- Add security tests for unauthorized, forbidden, inactive, ownership, CORS, and path traversal cases.

### Relevant docs

- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Protected test route or existing auth route rejects missing/invalid tokens.
- Admin-only dependency rejects regular users.
- Path traversal attempts fail in utility tests.
- Absolute paths are rejected for database-facing path fields.
- Logs do not include passwords, tokens, secrets, or database passwords in tests or manual inspection.

### Commit

`feat(backend-security): add authorization ownership and path safety utilities`