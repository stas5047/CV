# Phase 4 Research - Backend startup migrations, idempotent seed/setup, and storage bootstrap

## Current phase

- Confirmed current phase: `Phase 4 - Backend startup migrations, idempotent seed/setup, and storage bootstrap`.
- Source: `docs/phase.md`.
- Direction: Backend / DevOps.
- Goal from docs: local/demo backend startup prepares database and minimal demo setup automatically.
- Risk level: not provided by user input; assumed `MEDIUM` because phase touches startup, database writes, admin credentials, and storage creation.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase 4 relevant docs only:
  - `docs/ARCHITECTURE.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/DATA_MODEL.md`
  - `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout exists.
- `git status --short` showed existing modified files before this planning task:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Required top-level service folders exist: `backend/`, `frontend/`, `cv/`, `training/`, `scripts/`, `storage/`, `docs/`.
- Root runtime files exist: `docker-compose.yml`, `docker-compose.gpu.yml`, `.env.example`, `Makefile`, `README.md`.
- `docker-compose.yml` defines `postgres`, `backend`, `cv-worker`, and `frontend`.
- `backend` and `cv-worker` both mount `./storage:/app/storage`.
- `.env.example` contains safe placeholder values for DB, auth, storage, backend, CV, worker, and local ports.
- `scripts/bootstrap-storage.ps1` exists for local storage directory bootstrap.
- `backend/pyproject.toml` includes FastAPI, Pydantic settings, SQLAlchemy, Alembic, psycopg, passlib bcrypt, jose, pytest, and ruff dependencies.

## Existing implementation state

- Backend FastAPI app factory exists at `backend/app/main.py`.
- Backend health routes exist under `/api/health` and `/api/health/db`.
- Backend settings exist in `backend/app/core/config.py`.
- Existing settings include:
  - `DATABASE_URL`
  - `JWT_SECRET_KEY`
  - `JWT_ALGORITHM`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `ADMIN_EMAIL`
  - `ADMIN_PASSWORD`
  - `ALLOW_PUBLIC_REGISTRATION`
  - `STORAGE_ROOT`
  - `MODELS_ROOT`
  - `BACKEND_CORS_ORIGINS`
  - `MAX_IMAGE_SIZE_MB`
  - `MAX_VIDEO_SIZE_MB`
- Existing settings do not include:
  - `RUN_MIGRATIONS_ON_START`
  - `RUN_SEED_ON_START`
- Database session factory exists at `backend/app/db/session.py`.
- SQLAlchemy models exist in `backend/app/db/models.py` for all required tables from `docs/DATA_MODEL.md`.
- Alembic configuration exists in `backend/alembic.ini` and `backend/migrations/env.py`.
- Initial migration exists at `backend/migrations/versions/20260513_0001_initial_schema.py`.
- Backend Dockerfile currently starts Uvicorn directly:
  - `CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]`
- No backend seed/setup command exists.
- No startup script exists for running `alembic upgrade head` before API start.
- No backend storage bootstrap service/module exists.
- No auth endpoints exist yet, so seeded admin authentication can only be verified at DB/hash level in this phase.
- Existing backend tests cover health, settings, logging redaction, and data-model constraints.
- Existing `.context/research.md`, `.context/design.md`, and `.context/plan.md` were empty when read.

## WARNING: CONFLICT

- `docs/index.md` says current implementation contains only Phase 1 Docker Compose scaffold and placeholder backend/frontend/CV Dockerfiles with no product app scaffolds, dependency manifests, source packages, migrations, tests, API routes, or worker logic.
- Repository facts contradict that statement:
  - `backend/pyproject.toml`
  - `backend/app/main.py`
  - `backend/app/api/health.py`
  - `backend/app/db/models.py`
  - `backend/migrations/versions/20260513_0001_initial_schema.py`
  - `backend/tests/*`
- `README.md` says database schema and migrations are not available yet, but repo contains SQLAlchemy models and an initial Alembic migration.
- `backend/index.md` matches repo state and says DB schema/migration exist.
- This appears to be stale implementation-state documentation, not conflict with Phase 4 product behavior.

## Unknowns and assumptions

- User did not replace placeholder `Goal` or `Risk level`; contract assumes current phase from `docs/phase.md` and `MEDIUM` risk.
- Password hashing algorithm can use existing dependency `passlib[bcrypt]`; Argon2 is allowed by docs but not currently installed.
- Seed behavior assumption:
  - If `ADMIN_EMAIL` does not exist, create active admin user with hashed `ADMIN_PASSWORD`.
  - If `ADMIN_EMAIL` exists as admin, refresh password hash from current env and ensure account remains active.
  - If `ADMIN_EMAIL` exists as non-admin, fail with a safe error instead of silently escalating a regular user.
- Email normalization is not specified in docs; avoid adding undocumented canonicalization beyond trim/lower only if existing auth implementation later establishes it.
- Optional model/experiment placeholder seeding should be skipped in this phase unless existing relative artifacts are present and docs already define safe metadata.
- Auth endpoints are later-phase work; no `/api/auth/*` implementation belongs in this phase.
- Storage bootstrap should create only documented folders under `STORAGE_ROOT`: `uploads/`, `results/`, `reports/`, `models/`, `temp/`, `datasets/`.

## Files likely relevant for implementation

- `backend/app/core/config.py`
- `backend/app/db/session.py`
- `backend/app/db/models.py`
- `backend/migrations/env.py`
- `backend/Dockerfile`
- `backend/pyproject.toml`
- `backend/tests/conftest.py`
- New backend seed/setup module under `backend/app/` or `backend/app/db/`
- New backend startup/entrypoint script under `backend/`
- New backend tests for seed/setup, startup switches, password hashing, and storage bootstrap
- `.env.example`
- `docker-compose.yml`
- `README.md`
- `backend/index.md`
