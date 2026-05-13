## Phase 4 - Backend startup migrations, idempotent seed/setup, and storage bootstrap

**Direction:** Backend / DevOps  
**Goal:** Make local/demo backend startup prepare the database and minimal demo setup automatically.

### Scope

- Add backend startup script that can run `alembic upgrade head` before starting the API in local/demo mode.
- Add an idempotent seed/setup command.
- Seed the initial admin account from `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
- Hash the seeded admin password before storage.
- Ensure public registration never creates admin accounts.
- Create or verify required storage directories under `STORAGE_ROOT`.
- Optionally seed documented placeholder model/experiment metadata only when corresponding relative artifacts exist.
- Add environment switches such as `RUN_MIGRATIONS_ON_START` and `RUN_SEED_ON_START` if useful.
- Document demo credentials policy and local-only warning.
- Ensure seed can run repeatedly without duplicating records.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Clean database startup applies migrations automatically in local/demo mode.
- Seed command creates exactly one admin account for the configured email.
- Re-running seed does not duplicate users or model/experiment placeholder records.
- Storage folders are created or verified.
- Seeded admin can authenticate once auth is implemented, or the seed output is testable at database level in this phase.

### Commit

`chore(backend-seed): add migrations seed setup and storage bootstrap`