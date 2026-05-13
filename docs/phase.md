## Phase 2 - Backend FastAPI scaffold, settings, logging, and health

**Direction:** Backend  
**Goal:** Create the FastAPI backend foundation with configuration, logging, and health checks.

### Scope

- Scaffold `backend/` Python project.
- Add dependency management for FastAPI, Pydantic v2, Uvicorn/Gunicorn-Uvicorn, SQLAlchemy 2.x, Alembic, PostgreSQL driver, auth/security helpers, testing tools, and lint/format tools.
- Implement typed settings loaded from environment variables.
- Implement app factory or main app module.
- Implement structured logging baseline that does not log secrets.
- Implement public health endpoints:
  - `GET /api/health`;
  - `GET /api/health/db`.
- Add database connectivity layer skeleton.
- Add CORS configuration using explicit configured origins.
- Add backend Dockerfile and startup entrypoint placeholder.
- Add initial backend tests for health and settings.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Backend lint/format checks pass.
- Backend test suite passes.
- `GET /api/health` returns a safe status response.
- `GET /api/health/db` verifies PostgreSQL connectivity without leaking secrets.
- Backend container starts in Docker Compose.

### Commit

`feat(backend): scaffold FastAPI settings logging and health`