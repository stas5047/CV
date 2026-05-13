# Phase 2 Plan - Backend FastAPI Scaffold, Settings, Logging, And Health

## Scope

Only Phase 2 work. No auth endpoints, no user tables, no migrations with schema, no upload/media/job/result/model/experiment/admin APIs, no worker queue, no frontend UI, no training utilities.

## Ordered Atomic Plan

1. `@role/developer-backend` Verify current backend placeholder state.
   - Read `backend/index.md`, `backend/Dockerfile`, `docker-compose.yml`, `.env.example`.
   - Confirm no existing backend app or tests need preservation.
   - Verifiable: exact files exist and backend app files are absent before scaffold.

2. `@role/developer-backend` Add backend dependency manifest.
   - Create backend-local project manifest for FastAPI, Pydantic v2/settings, SQLAlchemy 2.x, Alembic dependency, PostgreSQL driver, ASGI server, CORS support through FastAPI/Starlette, pytest/httpx test tooling, and lint/format tooling.
   - Keep dependencies backend-local.
   - Verifiable: dependency install command exists for `backend/`.

3. `@role/developer-backend` Create backend package skeleton.
   - Add backend package directories for app entrypoint, API router, core settings/logging/CORS, DB connectivity, and tests.
   - Keep modules small and single-purpose.
   - Verifiable: imports resolve from test runner.

4. `@role/developer-backend` Implement typed settings.
   - Load env values already present in `.env.example`.
   - Parse `BACKEND_CORS_ORIGINS` as explicit origins.
   - Reject wildcard `*` CORS origins in settings validation; local development must use explicit localhost origins.
   - Keep secret-bearing fields masked or omitted from repr/logging.
   - Do not add new product env vars unless needed for Phase 2 startup and documented.
   - Verifiable: settings tests cover env parsing, wildcard CORS rejection, and secret-safe representation.

5. `@role/developer-auth-security` Implement safe logging baseline.
   - Configure structured application logging.
   - Ensure known sensitive names/values are never logged by startup/config logging.
   - Do not log raw `DATABASE_URL`, `JWT_SECRET_KEY`, `ADMIN_PASSWORD`, tokens, or passwords.
   - Verifiable: tests or inspection prove no sensitive strings appear in configured log output.

6. `@role/developer-backend` Implement database connectivity skeleton.
   - Create SQLAlchemy 2 engine/session helper from configured `DATABASE_URL`.
   - Add minimal DB health function using a simple connectivity query.
   - Do not add ORM models or schema.
   - Verifiable: DB health helper can be mocked in route tests and can run against PostgreSQL in Docker smoke.

7. `@role/developer-backend` Implement API router and app entrypoint.
   - Create FastAPI app with routes under `/api`.
   - Add only `GET /api/health` and `GET /api/health/db`.
   - Add CORS middleware using configured explicit origins.
   - Do not allow wildcard CORS origins.
   - Ensure health responses do not include secrets, raw config, stack traces, or filesystem paths.
   - Verifiable: route tests pass for both endpoints.

8. `@role/developer-backend` Add health/settings tests.
   - Add tests for settings load, CORS parsing, wildcard CORS rejection, safe setting representation, health success, DB-health success with mocked helper, and DB-health failure without raw exception text, DSN, or secret leakage.
   - Keep health response tests intentionally minimal so they assert safe status/availability without freezing an undocumented expanded schema.
   - Keep tests scoped to Phase 2.
   - Verifiable: backend test command passes.

9. `@role/developer-devops` Replace backend placeholder Docker startup.
   - Update `backend/Dockerfile` to install backend dependencies and start ASGI backend.
   - Keep container path `/app`.
   - Preserve Compose shared storage mount at `/app/storage`.
   - Verifiable: backend image builds and container starts.

10. `@role/developer-devops` Adjust Compose only for Phase 2 backend health access if needed.
    - Add backend port mapping using existing `BACKEND_PORT` if direct host health checks require it.
    - Keep existing `postgres`, `backend`, `cv-worker`, `frontend` service names.
    - Do not add new services.
    - Verifiable: `docker compose --env-file .env.example config` passes.

11. `@role/docs-maintainer` Update backend-local docs only if commands or files change.
    - Update `backend/index.md` with current files and backend-local install/test/start commands.
    - Update README only if root startup or Compose behavior changes.
    - Do not modify product docs.
    - Verifiable: docs reflect actual commands and still state unavailable later-phase capabilities as `not available yet`.

12. `@role/tester` Run relevant backend gates.
    - Run backend dependency install/check command.
    - Run backend lint/format check command if configured.
    - Run backend tests.
    - Run `docker compose --env-file .env.example config`.
    - Run backend container startup/health smoke if feasible.
    - Report unavailable commands as `not available yet`, not `PASS`.

13. `@role/code-reviewer` Review Phase 2 scope.
    - Confirm only Phase 2 files/behavior changed.
    - Confirm no auth endpoints, product routes, DB schema, migrations with tables, upload/job logic, worker logic, or frontend UI were added.
    - Confirm logs and health payloads do not expose secrets.
    - Confirm `/api` prefix and public health endpoints match docs.
    - Verifiable: review notes cite files and tests.

## Quality Gates For This Phase

- `backend` dependency install command: `PASS` or `FAIL` once command exists.
- `backend` lint/format check command: `PASS` or `FAIL` if configured; `not available yet` only if no lint tool was added.
- `backend` tests command: `PASS` or `FAIL`.
- CORS wildcard rejection settings test: `PASS` or `FAIL` as part of backend tests.
- `docker compose --env-file .env.example config`: `PASS` or `FAIL`.
- Backend Docker build/start smoke: `PASS` or `FAIL` if Docker available; otherwise exact blocker.
- `GET /api/health`: `PASS` or `FAIL` once backend running.
- `GET /api/health/db`: `PASS` or `FAIL` once backend and PostgreSQL running.

## Later-Phase Work Explicitly Excluded

- Phase 3 database schema and initial migration.
- Phase 4 startup migrations, seed/setup, and storage bootstrap from backend.
- Phase 5 auth/register/login/me.
- Phase 6 authorization, ownership, path-safety utilities beyond minimal settings/logging safety.
- Phase 7+ media upload, jobs, results, worker integration.
- Frontend implementation phases.
