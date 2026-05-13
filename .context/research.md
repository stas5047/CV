# Phase 5 Research Contract

## Current Phase

Confirmed: `docs/phase.md` identifies current phase as **Phase 5 - Authentication and account activity**.

Confirmed risk surface: backend/security. User did not replace risk placeholder; assumed risk is **HIGH** because this phase creates auth, JWT, password checks, and protected-route access rules.

## Docs Consulted

Read first:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Relevant docs from `docs/phase.md`:

- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

Context files checked:

- `.context/status.md` was present and empty.
- `.context/research.md`, `.context/design.md`, `.context/plan.md` were present and empty before this contract.

## Confirmed Repository Facts

- Git checkout exists.
- `git status --short` showed modified `.context/*` files and modified `docs/phase.md`; source code was not shown as modified.
- Current source layout includes `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `scripts/`, Compose files, `.env.example`, and README.
- Backend Python scaffold exists with FastAPI app factory, `/api` router, health endpoints, settings, CORS, logging redaction, SQLAlchemy session setup, SQLAlchemy models, Alembic migration, setup command, and tests.
- Backend dependencies already include `bcrypt`, `python-jose[cryptography]`, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, psycopg, pytest, and Ruff.
- `backend/app/core/passwords.py` already has `hash_password()` and `verify_password()` using bcrypt.
- `backend/app/core/config.py` already defines `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ALLOW_PUBLIC_REGISTRATION`, and seeded admin settings.
- `backend/app/db/models.py` already defines `User` with `email`, `password_hash`, `role`, `is_active`, `created_at`, and `updated_at`.
- `backend/app/setup.py` already seeds an active admin from `ADMIN_EMAIL` and hashes `ADMIN_PASSWORD`.
- `backend/app/api/router.py` currently includes only health routes.
- Existing backend tests cover health, settings, logging redaction, data model, and setup.

## Existing Implementation State

Confirmed implemented before Phase 5:

- Public health endpoints:
  - `GET /api/health`
  - `GET /api/health/db`
- Database schema and initial Alembic migration exist.
- Admin seed/setup exists and hashes admin password.
- CORS rejects wildcard origins through settings validation.
- Logging redaction exists for secret-like messages.

Confirmed not implemented yet:

- No auth API endpoints exist:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - optional `POST /api/auth/logout`
- No JWT creation/verification helpers found.
- No FastAPI auth dependency for current active user found.
- No request-scoped database session dependency found.
- No role-check or ownership helpers are required by Phase 5; those belong to Phase 6.
- No media, jobs, downloads, models, experiments, admin APIs, worker queue logic, or frontend UI exist in this checkout.

## Unknowns And Assumptions

Confirmed docs do not specify exact JSON field names for auth responses beyond returning a JWT access token.
Confirmed `docs/API.md` marks `POST /api/auth/register` and `POST /api/auth/login` as guest-only endpoints for authenticated users/admins.
Confirmed `docs/phase.md` allows tokens only in the login token response, and `docs/AUTH_SECURITY.md` describes registration followed by login rather than registration auto-login.

Assumptions for implementation contract:

- Use the existing `users` table; no Phase 5 migration should be needed unless implementation discovers a schema mismatch.
- Use existing bcrypt helpers; do not add Argon2 unless there is a reason to replace current working helper.
- Use configured JWT algorithm and expiration from settings.
- `/api/auth/me` returns a safe current-user profile with role and no `password_hash`.
- Login token response may use a conventional bearer-token shape, but exact schema must be defined in implementation tests because docs only require a JWT access token.
- Registration returns safe user data only and must not return a JWT access token.
- Authenticated user/admin requests to guest-only register/login endpoints should be rejected with HTTP 403.
- Optional backend logout can be skipped in Phase 5 because API docs allow client-side token deletion and do not require token invalidation storage.
- Email normalization should at least trim and lower-case before uniqueness checks, matching existing seed behavior.

## Files Likely Relevant For Implementation

Existing files likely touched:

- `backend/app/api/router.py`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/passwords.py`
- `backend/app/db/session.py`
- `backend/app/db/models.py`
- `backend/tests/conftest.py`
- `backend/tests/test_settings.py`
- `backend/tests/test_setup.py`
- `backend/pyproject.toml`

Existing files likely referenced only:

- `backend/app/setup.py`
- `backend/tests/test_health.py`
- `backend/tests/test_logging.py`
- `backend/tests/test_data_model.py`
- `backend/migrations/versions/20260513_0001_initial_schema.py`

New implementation files are expected under existing `backend/app/` and `backend/tests/` only if needed. Exact filenames are implementation detail; do not add top-level folders or product-doc changes for Phase 5.

## Conflict Check

No `WARNING: CONFLICT` found. `docs/phase.md` Phase 5 matches `docs/ROADMAP.md` Phase 5 scope and relevant docs.
