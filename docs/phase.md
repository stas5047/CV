## Phase 5 - Authentication and account activity

**Direction:** Backend / Security  
**Goal:** Implement registration, login, current-user, JWT, password hashing, and account activity checks.

### Scope

- Implement password hashing with bcrypt or Argon2.
- Implement JWT access-token creation and verification.
- Implement auth dependencies/middleware for protected routes.
- Implement endpoints:
  - `POST /api/auth/register`;
  - `POST /api/auth/login`;
  - `GET /api/auth/me`;
  - `POST /api/auth/logout` as optional consistency endpoint.
- Enforce `ALLOW_PUBLIC_REGISTRATION`.
- Enforce minimum password length of 8 characters.
- Ensure registration always creates `role = user`.
- Reject inactive users at login and on protected-route access.
- Ensure API responses never expose password hashes or tokens except login token response.
- Add tests for register/login/me/inactive/disabled-registration cases.

### Relevant docs

- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Registration works when public registration is enabled.
- Registration returns forbidden behavior when disabled.
- Public registration cannot create admin accounts.
- Login works with valid credentials and fails with invalid credentials.
- Inactive accounts cannot authenticate or access protected routes.
- Seeded admin can log in.
- Auth tests pass.

### Commit

`feat(backend-auth): add JWT auth registration login and account activity checks`