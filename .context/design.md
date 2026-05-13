# Phase 5 Design Contract

## Phase Goal

Implement backend authentication and account activity only:

- public registration controlled by `ALLOW_PUBLIC_REGISTRATION`;
- login with email/password;
- JWT access-token creation and verification;
- current-user endpoint;
- guest-only access enforcement for register/login;
- protected-route dependency that rejects inactive accounts;
- focused tests for the documented auth cases.

No frontend, uploads, jobs, downloads, role/ownership utility expansion, worker, training, or admin API work belongs in this phase.

## Intended Behavior From Docs

Confirmed required endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Confirmed optional endpoint:

- `POST /api/auth/logout` may exist, but token invalidation storage is not required.

Confirmed auth rules:

- JWT access tokens are required for protected routes.
- Passwords must be hashed with bcrypt or Argon2; current repo already uses bcrypt.
- Password minimum length is 8 characters.
- Public registration obeys `ALLOW_PUBLIC_REGISTRATION`.
- Disabled public registration returns HTTP 403.
- Public registration always creates `role = user`.
- Public registration must never create admins.
- Inactive users must not receive tokens at login.
- Inactive users must not access protected endpoints.
- Register/login are guest-only endpoints per `docs/API.md`; authenticated users/admins must be rejected with HTTP 403.
- Login is the only Phase 5 endpoint that returns a JWT access token.
- Registration returns safe user data only and must not return a JWT access token.
- Auth responses must not expose `password_hash`, JWT secret, or raw token except in the login token response.

Confirmed data rules:

- Use existing `users` table.
- `users.email` is unique.
- `users.role` is `user` or `admin`.
- `users.is_active` gates authentication and protected route access.

Confirmed QA rules:

- Register enabled works.
- Register disabled returns forbidden behavior.
- Short password is rejected.
- Login works with valid credentials.
- Login fails with invalid credentials.
- JWT token allows protected access.
- Missing/invalid token blocks protected access.
- Seeded admin can log in.
- Inactive account cannot authenticate or access protected route.
- Public registration cannot create admin account.

## Architecture Decisions

- Keep auth in backend only; frontend and worker remain untouched.
- Keep route handlers thin; place token/password/user lookup rules in backend auth helpers or services under existing backend package.
- Reuse `backend/app/core/passwords.py` bcrypt helpers.
- Use `python-jose` already present in `backend/pyproject.toml` for JWT encode/decode unless implementation finds a concrete blocker.
- Add request-scoped SQLAlchemy session dependency so auth routes and current-user dependency do not use global sessions directly.
- Normalize email consistently with seed behavior: trim and lower-case before lookup/create.
- Use generic login failure errors for invalid email/password or inactive user to avoid account-state disclosure unless tests/docs require more detail.
- Reject authenticated requests to `POST /api/auth/register` and `POST /api/auth/login` with HTTP 403 because the API access matrix says user/admin access is `No`.
- Do not create extra roles, refresh tokens, password reset, email confirmation, OAuth, 2FA, account lockout, rate limiting, or token blacklist.
- Do not add database migrations unless implementation proves current `users` schema cannot satisfy Phase 5.

## Backend Impact

Touched backend surface:

- Add auth router under `/api/auth`.
- Register auth router in existing `/api` router.
- Add schemas for register/login/current-user/token responses.
- Add JWT helper for token create/verify.
- Add current active user dependency.
- Add DB session dependency if absent.
- Add tests for auth behavior.

Out of scope:

- Media/job/result/model/experiment/admin APIs.
- Role-check dependency for admin-only endpoints beyond what `/me` needs.
- Ownership helpers.
- Upload/path safety utilities beyond existing config/log safety.

## Frontend Impact

No frontend source changes in Phase 5.

Frontend-relevant contract only:

- Backend must provide stable auth endpoints for later Ukrainian UI phases.
- Response errors should be safe and localizable; no frontend Ukrainian copy is required in this backend phase.

## DB Impact

Expected no schema change.

Use current `users` fields:

- `id`
- `email`
- `password_hash`
- `role`
- `is_active`
- `created_at`
- `updated_at`

If implementation discovers missing DB support, stop before migration and report because Phase 3 already owns schema.

## API Impact

Auth routes only:

- `POST /api/auth/register`: guest-only public registration when enabled; creates `user` account only; returns safe user data only; never returns a token.
- `POST /api/auth/login`: guest-only credential login; returns JWT access token for active users only.
- `GET /api/auth/me`: protected; returns current active user profile.
- `POST /api/auth/logout`: optional; if implemented, authenticated no-op consistency endpoint only, no token invalidation storage.

Ambiguous response details:

- Docs require a JWT access token but do not define exact token response fields.
- Docs require current-user profile and role but do not define exact profile fields.
- Implementation tests must lock chosen safe response schemas without adding undocumented business behavior.
- Authenticated requests to register/login should return HTTP 403.

## Security/Privacy Impact

Security rules for this phase:

- Never store plain-text passwords.
- Never return `password_hash`.
- Never return JWT tokens except from `POST /api/auth/login`.
- Never log passwords, password hashes, JWT tokens, JWT secret, admin password, or database password.
- Reject inactive users at login and protected-route access.
- Reject missing, malformed, expired, or invalid JWT on protected routes.
- Ensure public registration cannot set or smuggle `role = admin`.
- Keep CORS behavior unchanged and explicit.

## Test Strategy

Backend tests only:

- register success when `ALLOW_PUBLIC_REGISTRATION=true`;
- register forbidden when disabled;
- short password rejected;
- duplicate email rejected safely;
- registration stores bcrypt hash, not plain password;
- registration payload with `role = admin` or another role-like extra field cannot create an admin;
- registration result cannot create admin and does not expose `password_hash` or a token field;
- authenticated regular-user and admin requests to register are rejected with HTTP 403;
- login success returns JWT access token;
- login invalid password/email fails;
- authenticated regular-user and admin requests to login are rejected with HTTP 403;
- inactive user login fails;
- `/api/auth/me` succeeds with valid token;
- `/api/auth/me` rejects missing/invalid/expired token;
- inactive user token cannot access `/api/auth/me`;
- `/api/auth/me` response omits `password_hash` and any token field;
- seeded admin can log in using existing setup behavior.

Relevant checks:

- `cd backend; python -m ruff check .`
- `cd backend; python -m pytest`

Docker smoke is optional for this planning contract unless implementation changes Docker/startup behavior. No frontend/CV gates apply.

## Ambiguities Or Conflicts

No confirmed doc conflicts.

Ambiguities:

- Exact login token response JSON field names are not specified.
- Exact `/api/auth/me` response fields are not specified beyond current user profile and role.
- Optional logout endpoint is not required because client-side token deletion is acceptable.
