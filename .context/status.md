# Phase 4 Implementation Status

## Completed

- Added `RUN_MIGRATIONS_ON_START` and `RUN_SEED_ON_START` backend settings.
- Added bcrypt password hash/verify helper for seeded admin.
- Added idempotent setup command at `python -m app.setup`.
- Setup command creates documented storage folders under `STORAGE_ROOT`.
- Setup command creates configured admin if absent, refreshes existing admin password hash, and fails safely if `ADMIN_EMAIL` belongs to a non-admin user.
- Added backend container startup script that optionally runs Alembic migrations and setup before Uvicorn.
- Wired startup switches through `.env.example` and `docker-compose.yml`.
- Updated README and `backend/index.md`.
- Final code-review fix enforced 8-character minimum for `ADMIN_PASSWORD`.
- Final code-review fix aligned startup script enabled-value parsing with common boolean true forms.

## Quality gates run

- `python -m pytest tests/test_settings.py tests/test_setup.py -q` from `backend/`: PASS.
- `python -m ruff check app/core/config.py app/core/passwords.py app/setup.py tests/test_settings.py tests/test_setup.py` from `backend/`: PASS.
- `python -m ruff check .` from `backend/`: PASS.
- `python -m pytest` from `backend/`: PASS, 22 tests.
- `docker compose --env-file .env.example config` from repo root: PASS.
- `docker compose --env-file .env.example run --rm --build backend alembic upgrade head` from repo root: PASS.
- `docker compose --env-file .env.example run --rm backend python -m app.setup` from repo root: PASS after migration; rerun also PASS.
- `docker compose --env-file .env.example up -d --build backend` plus `GET /api/health` and `GET /api/health/db`: PASS.
- `docker run --rm --entrypoint /bin/sh aerovision-backend -n /app/startup.sh` from repo root: PASS.

## Notes

- One seed smoke failed before rerun because migration and seed were mistakenly launched in parallel. Logged in `docs/mistakes-codex.md`; rerun after migration passed.
- No auth endpoints, upload APIs, frontend UI, worker queue logic, model registry APIs, or experiment APIs were added.
