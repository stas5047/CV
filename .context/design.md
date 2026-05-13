# Phase 4 Design - Backend startup migrations, idempotent seed/setup, and storage bootstrap

## Phase goal

Make local/demo backend startup able to prepare the database and minimal setup automatically by running migrations, seeding the initial admin account from environment variables, and creating required storage directories.

## Intended behavior from docs

- Backend startup can run `alembic upgrade head` before starting API in local/demo mode.
- Seed/setup command is idempotent.
- Initial admin account is created from `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
- Seeded admin password is stored only as secure hash.
- Public registration never creates admin accounts; no registration endpoint belongs in this phase.
- Required storage folders are created or verified under `STORAGE_ROOT`.
- Optional placeholder model/experiment metadata is seeded only when corresponding relative artifacts exist.
- Startup switches such as `RUN_MIGRATIONS_ON_START` and `RUN_SEED_ON_START` may be added when useful.
- Demo credentials policy and local-only warning must be documented during implementation.
- Re-running seed must not duplicate users or placeholder records.
- Seeded admin authentication is not testable through API until auth phase; verify DB row and password hash in this phase.

## Architecture decisions

- Keep Phase 4 as backend/devops setup only. No API routes, auth endpoints, upload flows, worker queue processing, or frontend changes.
- Add startup switch settings for:
  - `RUN_MIGRATIONS_ON_START`
  - `RUN_SEED_ON_START`
- Use backend container entrypoint/start script to run migrations and seed before launching Uvicorn when switches are enabled.
- Keep direct manual commands available:
  - migration command: `alembic upgrade head`
  - seed/setup command: Python module or console entry backed by backend code
- Implement storage bootstrap in backend code so Docker startup can create/verify folders inside mounted `STORAGE_ROOT`.
- Keep existing root PowerShell storage helper as local helper; do not replace it.
- Skip optional model/experiment placeholder seeding unless implementation finds existing documented relative artifacts. Current repo has no such artifacts.
- Avoid any new top-level folders.

## Backend impact

- Add startup configuration fields.
- Add seed/setup command or module.
- Add password hashing helper only as much as needed for seeded admin.
- Add storage bootstrap helper.
- Add Docker startup script/entrypoint wiring.
- Add tests for setup behavior.
- No new public API behavior.

## Database impact

- No schema changes planned.
- Seed/setup writes to `users` only.
- User row rules:
  - `email = ADMIN_EMAIL`
  - `role = admin`
  - `is_active = true`
  - `password_hash` contains bcrypt hash, never plain text
- Existing `users.email` unique constraint protects duplicate admin rows.

## API impact

- None.
- `/api/health` and `/api/health/db` remain existing Phase 2 health endpoints.
- Auth endpoints remain later-phase work.

## Frontend impact

- None.

## Security/privacy impact

- `ADMIN_PASSWORD` must never be logged.
- Password hash must never expose plain env password.
- Existing logging redaction should include admin password and DB URL.
- Seed output/logs should identify action without printing sensitive values.
- Existing CORS behavior should remain unchanged.
- Storage bootstrap must create only paths under configured `STORAGE_ROOT`.
- No absolute storage paths should be stored in database.

## Test strategy

- Unit tests for settings defaults and env parsing:
  - startup switches parse as booleans.
- Unit tests for storage bootstrap:
  - creates `uploads`, `results`, `reports`, `models`, `temp`, `datasets` under temp `STORAGE_ROOT`.
  - rerun succeeds without deleting existing content.
- DB-level tests for seed:
  - creates exactly one admin user for configured email.
  - password hash differs from plain password.
  - bcrypt verification succeeds.
  - rerun does not duplicate user.
  - existing admin email rerun refreshes hash without duplicate.
  - existing non-admin same email fails safely.
- Startup/entrypoint tests can verify command composition or script behavior without requiring full Docker runtime where practical.
- Relevant commands for implementation phase:
  - `python -m ruff check .` from `backend/`
  - `python -m pytest` from `backend/`
  - `docker compose --env-file .env.example config` from repo root
  - `docker compose --env-file .env.example run --rm backend alembic upgrade head` when Docker/PostgreSQL available
  - seed command from backend container when implemented

## Ambiguities or conflicts

- WARNING: CONFLICT: `docs/index.md` and `README.md` are stale about current DB/migration implementation state. Repo and `backend/index.md` show Phase 3 artifacts exist.
- Docs do not specify exact behavior when `ADMIN_EMAIL` already exists as a regular user. Design chooses safe failure rather than silent privilege escalation.
- Docs allow bcrypt or Argon2. Existing dependencies include bcrypt via passlib, so bcrypt is selected for this phase.
- Docs say optional model/experiment placeholders may be seeded when artifacts exist. Current repo has no model or experiment artifacts, so design skips optional placeholder records.
