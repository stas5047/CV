# Phase 4 Plan - Backend startup migrations, idempotent seed/setup, and storage bootstrap

1. [@role/developer-backend] Add startup switch settings.
   - Modify `backend/app/core/config.py`.
   - Add boolean settings for `RUN_MIGRATIONS_ON_START` and `RUN_SEED_ON_START`.
   - Verify with focused settings tests.

2. [@role/tester] Add failing settings tests.
   - Modify `backend/tests/test_settings.py`.
   - Verify defaults and env override parsing for startup switches.
   - Run: `python -m pytest tests/test_settings.py -q` from `backend/`.
   - Expected before implementation: tests fail because settings fields do not exist.

3. [@role/developer-backend] Implement password hashing helper for seed only.
   - Add focused backend helper under existing backend package.
   - Use bcrypt through existing `passlib[bcrypt]` dependency.
   - Provide hash and verify functions.
   - Do not implement login, JWT issuance, registration, or auth routes.

4. [@role/tester] Add failing seed password tests.
   - Add backend tests proving seeded password hash:
     - is not equal to plain password;
     - verifies with configured password;
     - does not print secret values.
   - Run targeted test file from `backend/`.

5. [@role/developer-backend] Implement storage bootstrap helper.
   - Create/verify only documented folders under `STORAGE_ROOT`:
     - `uploads`
     - `results`
     - `reports`
     - `models`
     - `temp`
     - `datasets`
   - Make helper idempotent.
   - Do not delete existing files.

6. [@role/tester] Add failing storage bootstrap tests.
   - Use `tmp_path` as `STORAGE_ROOT`.
   - Assert all six folders are created.
   - Assert rerun succeeds.
   - Run targeted test file from `backend/`.

7. [@role/developer-db] Implement idempotent admin seed/setup.
   - Use existing SQLAlchemy `User` model and session factory.
   - Create admin when `ADMIN_EMAIL` absent.
   - Re-run without duplicate when same admin exists.
   - Refresh hash for existing admin email from `ADMIN_PASSWORD`.
   - Fail safely if same email exists with non-admin role.
   - Never seed admin through public registration.
   - Skip optional model/experiment placeholder seeding unless existing documented relative artifacts are present.

8. [@role/tester] Add failing DB-level seed tests.
   - Verify one admin row is created.
   - Verify rerun leaves one row.
   - Verify role is `admin` and `is_active = true`.
   - Verify password hash verifies and plain password is not stored.
   - Verify non-admin same email conflict fails safely.
   - Run targeted seed tests from `backend/`.

9. [@role/developer-backend] Add manual seed/setup command.
   - Expose command through a Python module or project script under `backend/`.
   - Command runs storage bootstrap and admin seed.
   - Keep output safe: no passwords, hashes, DB URLs, JWT secrets, or absolute sensitive paths.
   - Verify command can run repeatedly.

10. [@role/developer-devops] Add backend startup script/entrypoint.
    - Modify `backend/Dockerfile` to use startup script instead of direct Uvicorn command.
    - Startup script behavior:
      - if `RUN_MIGRATIONS_ON_START=true`, run `alembic upgrade head`;
      - if `RUN_SEED_ON_START=true`, run seed/setup command;
      - start Uvicorn app factory.
    - Keep migration and seed switches local/demo oriented.

11. [@role/developer-devops] Wire environment switches.
    - Modify `.env.example` with safe placeholder/default values for startup switches.
    - Modify `docker-compose.yml` to pass startup switch env vars to backend.
    - Do not add new services.
    - Do not request GPU outside `cv-worker`.

12. [@role/docs-maintainer] Update implementation docs only.
    - Update `README.md` for Phase 4 commands, startup switches, seed behavior, and local-only demo credential warning.
    - Update `backend/index.md` with seed/setup command and startup behavior.
    - Do not modify product docs in `docs/` unless user explicitly asks.
    - Note existing stale state conflict in `docs/index.md`/`README.md` should be corrected only where task scope allows.

13. [@role/tester] Run backend quality gates.
    - From `backend/`: `python -m ruff check .`
    - From `backend/`: `python -m pytest`
    - Expected: PASS.

14. [@role/tester] Run runtime/config gates.
    - From repo root: `docker compose --env-file .env.example config`
    - If Docker/PostgreSQL available, run:
      - `docker compose --env-file .env.example run --rm backend alembic upgrade head`
      - implemented backend seed/setup command in container
    - Expected: config PASS; migration/seed PASS when Docker daemon and database are available.

15. [@role/code-reviewer] Review scope and safety.
    - Confirm no auth routes, upload APIs, frontend UI, worker queue behavior, model registry APIs, or experiment APIs were added.
    - Confirm admin password is hashed and not logged.
    - Confirm seed is idempotent and does not duplicate admin users.
    - Confirm storage bootstrap touches only documented folders.
    - Confirm DB still stores no media/model/report binaries.
