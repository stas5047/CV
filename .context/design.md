# Phase 2 Design - Backend FastAPI Scaffold, Settings, Logging, And Health

## Phase Goal

Create backend foundation for AeroVision: FastAPI app, environment-based settings, safe logging baseline, public health endpoints, database connectivity skeleton, explicit CORS, backend Docker startup, and initial backend tests. Do not implement auth, database schema, uploads, jobs, CV processing, model registry, experiments, admin APIs, or frontend UI in this phase.

## Intended Behavior From Docs

Confirmed facts:

- Backend exposes REST API under `/api`.
- Public health endpoints:
  - `GET /api/health`
  - `GET /api/health/db`
- `GET /api/health` returns safe backend health status.
- `GET /api/health/db` verifies PostgreSQL connectivity without leaking secrets.
- Backend settings load from environment variables.
- CORS uses explicit configured origins from `BACKEND_CORS_ORIGINS`.
- Logs omit secrets, tokens, passwords, password hashes, DB passwords, admin password, and sensitive env values.
- Backend container must start in Docker Compose.
- Phase 2 adds tests for health and settings.

Assumptions:

- Health JSON can be minimal and safe because docs do not require exact response schema.
- DB health may return available/unavailable status and appropriate HTTP behavior, but must not expose DSN, credentials, host internals, stack traces, or raw exception text.
- Phase 2 may include Alembic dependency and placeholder config, but concrete migrations and SQLAlchemy models remain Phase 3.

## Architecture Decisions

- Create a backend-local Python project under `backend/`, keeping backend ownership separate from frontend and CV worker.
- Use a small app factory or main module that includes an `/api` router and health router.
- Keep route handlers thin. Health route calls a database connectivity helper instead of embedding DB setup directly in route body.
- Use Pydantic v2 settings model for environment parsing and validation.
- Parse `BACKEND_CORS_ORIGINS` as explicit origins list.
- Reject `*` in `BACKEND_CORS_ORIGINS` during settings validation rather than adding a local/non-local environment flag. Local development should use explicit localhost origins, as `.env.example` already does.
- Add secret-safe settings representation so logs/tests do not print sensitive values.
- Add logging setup with redaction or omission for known sensitive fields.
- Add SQLAlchemy 2 engine/session skeleton only; no models, no migrations beyond optional empty Alembic scaffolding.
- Update backend Dockerfile from placeholder to install backend dependencies and start ASGI app.
- Adjust Compose only as needed for Phase 2 backend startup and health verification, using existing environment variables and shared storage mount.

## Backend Impact

- Backend project scaffold appears in `backend/`.
- Backend app serves only Phase 2 public health endpoints.
- Backend settings include existing env groups needed by Phase 2:
  - database URL;
  - JWT/auth placeholders from `.env.example` as settings only, not auth logic;
  - storage root/model root as settings only;
  - CORS origins;
  - upload size limits as settings only.
- Backend startup must not run migrations or seed setup in Phase 2 unless docs change; that belongs to Phase 4.
- Backend must not implement auth endpoints in Phase 2.

## API Impact

- Adds `GET /api/health`.
- Adds `GET /api/health/db`.
- No other API routes in Phase 2.
- Health responses must be public and safe.
- API must not expose absolute filesystem paths, credentials, stack traces, JWT secrets, raw tokens, or database URL.

## DB Impact

- Add database connectivity skeleton only.
- No concrete tables, constraints, seed data, or migrations in this phase.
- DB health performs a minimal connectivity check against PostgreSQL.
- Phase 3 remains responsible for SQLAlchemy models and initial Alembic migration.

## Frontend Impact

- None, except Compose/frontend may continue to point at backend `/api`.
- No React UI changes in Phase 2.

## Security/Privacy Impact

- Settings must treat `JWT_SECRET_KEY`, `ADMIN_PASSWORD`, `POSTGRES_PASSWORD`, database URL, and tokens as sensitive.
- Logging must not emit secrets or full settings dumps.
- DB health must not return connection strings, passwords, exception tracebacks, or internal env values.
- CORS must use explicit configured origins.
- CORS settings must reject wildcard origins so non-local wildcard drift cannot occur.
- Public health endpoints must not reveal more than service/database availability.

## Test Strategy

Relevant checks only:

- Backend settings tests:
  - required env values load;
  - CORS origins parse as explicit list;
  - wildcard CORS origins are rejected;
  - sensitive fields are not exposed by settings representation/log output.
- Backend health tests:
  - `GET /api/health` returns success and safe payload;
  - `GET /api/health` payload contains no sensitive values;
  - `GET /api/health/db` calls DB health helper and returns safe available response when helper succeeds;
  - `GET /api/health/db` returns safe unavailable response when helper fails, without raw exception text, DSN, or secret leakage.
  - health response assertions intentionally freeze only minimal safe status/availability fields, not an expanded product schema.
- Backend command checks:
  - backend lint/format command if configured;
  - backend test suite;
  - Docker Compose backend build/start smoke when available.

Out of scope tests:

- Auth, ownership, uploads, jobs, model selection, worker queue, CV processing, frontend routes, exports, admin routes.

## Ambiguities Or Conflicts

- No docs conflict found for Phase 2.
- Risk value not provided by user; contract assumes MEDIUM.
- Exact health response schema is unspecified; implementation should keep it minimal and avoid treating chosen shape as product-wide contract beyond Phase 2 tests.
- Exact dependency manager and lint tools are unspecified; implementation should pick pragmatic backend-local tooling and document commands if added.
- Whether to add `alembic.ini` in Phase 2 is mildly ambiguous: phase requires Alembic dependency, while Phase 3 owns initial migration. Safer design: include dependency and optional config placeholder only if needed by backend tooling; do not create migration scripts or schema in Phase 2.
- Claude review asked what flag defines non-local CORS behavior if wildcard is allowed locally. Final contract avoids the ambiguity by rejecting wildcard CORS values in all modes.
