# Phase 5 Implementation Plan

Scope: **Phase 5 - Authentication and account activity** only.

Risk assumption: **HIGH** because auth/security behavior gates all later protected APIs.

## Ordered Atomic Steps

1. `@role/developer-backend` Inspect existing backend auth-adjacent code.
   - Verify current `User` model, settings, bcrypt helper, API router, DB session setup, and tests.
   - Verifiable: exact existing functions/classes to reuse are listed before edits.

2. `@role/developer-backend` Define Phase 5 auth schemas inside existing backend app structure.
   - Include register input, login input, safe user output, and login token output.
   - Exclude `password_hash` from every response schema.
   - Exclude token fields from registration and `/me` responses.
   - Verifiable: schema tests or route tests prove password hash is absent and only login returns a token.

3. `@role/developer-auth-security` Add JWT helper.
   - Use configured `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
   - Include expiry claim.
   - Reject invalid/expired tokens.
   - Verifiable: tests cover valid, invalid, and expired token behavior.

4. `@role/developer-backend` Add request-scoped DB session dependency if absent.
   - Use existing SQLAlchemy session factory.
   - Ensure sessions close after request.
   - Verifiable: auth route tests can override/use test DB session cleanly.

5. `@role/developer-auth-security` Add current active user dependency.
   - Read bearer token from `Authorization`.
   - Decode JWT.
   - Load user by token subject.
   - Reject missing user or inactive user.
   - Verifiable: `/api/auth/me` rejects missing, invalid, expired, unknown-user, and inactive-user cases.

6. `@role/developer-backend` Implement `POST /api/auth/register`.
   - Reject authenticated user/admin requests with HTTP 403.
   - Obey `ALLOW_PUBLIC_REGISTRATION`.
   - Require password length >= 8.
   - Normalize email consistently with seed flow.
   - Hash password before save.
   - Always set `role = user`.
   - Ignore or reject role-like input so public registration cannot smuggle `role = admin`.
   - Reject duplicate email safely.
   - Return safe user data only; do not return a JWT access token.
   - Verifiable: tests cover enabled, disabled, authenticated caller forbidden, short password, duplicate email, hashed password, no admin creation, and no registration token.

7. `@role/developer-backend` Implement `POST /api/auth/login`.
   - Reject authenticated user/admin requests with HTTP 403.
   - Verify normalized email and password.
   - Reject inactive users.
   - Return JWT access token for valid active user.
   - Use generic failure for bad credentials/inactive state unless implementation tests require split status.
   - Verifiable: tests cover valid regular user, seeded admin, authenticated caller forbidden, wrong password, unknown email, inactive user.

8. `@role/developer-backend` Implement `GET /api/auth/me`.
   - Use current active user dependency.
   - Return safe user profile with role.
   - Verifiable: tests prove valid token succeeds and response omits password hash and token fields.

9. `@role/developer-backend` Decide optional `POST /api/auth/logout`.
   - Preferred Phase 5 minimal scope: skip endpoint because docs allow client-side token deletion and no invalidation storage is required.
   - If implemented, make it authenticated no-op consistency endpoint only.
   - Verifiable: plan/status notes state skipped or tests cover authenticated no-op behavior.

10. `@role/developer-backend` Register auth router under existing `/api` router.
    - Keep health endpoints public.
    - Verifiable: `/api/health` still works without token; auth routes live under `/api/auth`.

11. `@role/tester` Add focused backend auth tests.
    - Cover registration, login, JWT, `/me`, inactive users, seeded admin login, guest-only register/login enforcement, role-smuggling prevention, and response secrecy.
    - Do not add upload/job/admin/frontend/worker tests in this phase.
    - Verifiable: `python -m pytest` from `backend/` runs these tests.

12. `@role/tester` Run backend lint.
    - Command: `cd backend; python -m ruff check .`
    - Expected: `PASS`.

13. `@role/tester` Run backend tests.
    - Command: `cd backend; python -m pytest`
    - Expected: `PASS`.

14. `@role/code-reviewer` Review Phase 5 diff against docs.
    - Check no password/token leakage, no public admin creation, inactive checks, no extra roles, no out-of-scope APIs, no frontend/worker/media/job work.
    - Verifiable: review notes list any accepted/rejected issues.

15. `@role/docs-maintainer` Decide docs/index updates.
    - Product docs must not change for this implementation unless commands, env vars, or documented paths change.
    - Backend index/README update only if implementation changes current-state or commands.
    - Verifiable: final implementation report says docs updated or skipped with reason.

## Relevant Quality Gates

- `cd backend; python -m ruff check .`
- `cd backend; python -m pytest`

Not relevant for Phase 5:

- frontend build/tests;
- CV worker tests;
- Docker full-stack smoke, unless backend startup/Docker files change;
- migration validation, unless implementation adds an unexpected migration.

## Scope Exclusions

- No source work in this planning turn.
- No product docs modification in this planning turn.
- No schema change unless implementation later proves blocker.
- No role/ownership helpers beyond current active user dependency.
- No media, jobs, results, downloads, models, experiments, admin routes.
- No frontend UI.
- No worker/CV/training changes.
- No refresh tokens, password reset, email verification, OAuth, 2FA, rate limiting, lockout, token blacklist, or extra roles.
