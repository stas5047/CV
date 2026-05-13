## Phase 3 - Database schema and initial Alembic migration

**Direction:** Backend / Database  
**Goal:** Implement the concrete PostgreSQL schema and initial migration.

### Scope

- Add SQLAlchemy models for:
  - `users`;
  - `media_files`;
  - `processing_jobs`;
  - `detections`;
  - `tracks`;
  - `model_versions`;
  - `experiment_runs`;
  - `experiment_metrics`.
- Use UUID primary keys where appropriate.
- Add required enums/checks for roles, media types, job statuses, and experiment types.
- Add required foreign keys, relationships, indexes, unique constraints, and soft-deletion fields.
- Enforce only one active model version at a time where feasible with PostgreSQL constraints/indexes.
- Enforce relative-path storage at service validation level, and add database checks where practical.
- Add Alembic configuration and generate initial migration.
- Add database smoke tests for constraints and relationships.
- Document limitations where cross-table rules cannot be expressed cleanly in the database.

### Relevant docs

- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Alembic migration applies successfully to a fresh PostgreSQL database.
- Alembic migration can be run inside the backend container.
- Representative invalid rows are rejected by database constraints or covered by service validation TODO/tests.
- Required indexes exist.
- Backend test suite still passes.

### Commit

`feat(backend-db): add SQLAlchemy models and initial Alembic migration`