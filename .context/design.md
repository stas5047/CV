# Phase 3 Design - Database schema and initial Alembic migration

## Phase goal

Implement database schema foundation for documented MVP using SQLAlchemy 2.x models and Alembic initial migration. No API routes, auth flows, upload handling, worker logic, frontend UI, or training behavior in this phase.

## Intended behavior from docs

- PostgreSQL has documented tables:
  - `users`
  - `media_files`
  - `processing_jobs`
  - `detections`
  - `tracks`
  - `model_versions`
  - `experiment_runs`
  - `experiment_metrics`
- Tables include required fields, foreign keys, relationships, soft-deletion fields, status/role/type constraints, unique constraints, and indexes from `docs/DATA_MODEL.md`.
- Database stores metadata and structured records only.
- File references use relative paths only for:
  - `media_files.stored_path`
  - `processing_jobs.result_media_path`
  - `processing_jobs.csv_path`
  - `processing_jobs.json_path`
  - `model_versions.weights_path`
  - `experiment_runs.artifacts_path`
- `processing_jobs` supports PostgreSQL queue behavior required later:
  - `queued`, `processing`, `completed`, `failed`, `cancelled`
  - lock fields
  - heartbeat
  - retry count
  - progress
- Model registry supports one active model default where feasible with PostgreSQL constraint/index.
- No-detection remains representable as completed job with zero detections and nullable confidence summaries in JSON summary data.
- Migration applies to fresh PostgreSQL database and can run inside backend container.

## Architecture decisions

- Use existing backend stack: SQLAlchemy 2.x, Alembic, psycopg, PostgreSQL.
- Keep models in backend package; CV worker and frontend do not gain direct model ownership in this phase.
- Use SQLAlchemy declarative models with explicit table names matching docs.
- Use database-level constraints where docs require stable invariants:
  - unique `users.email`
  - role/status/type checks or enums
  - foreign keys
  - unique `(job_id, track_id)`
  - active model uniqueness
  - progress range
  - image-media invariants: `frame_count = 1`, `fps = null`, and `duration_seconds = null`
  - practical relative-path checks
- Use service-level validation TODO/test coverage notes only for rules that need cross-table/media context and cannot be cleanly enforced by database constraints.
- Keep Alembic metadata import tied to model metadata so future migrations are generated from same source.
- Do not add Celery, Redis, worker processing, auth endpoints, seed logic, upload routes, or frontend behavior.

## Backend impact

- Adds ORM schema layer and migration plumbing.
- Existing health endpoints and settings should keep working.
- Existing database session helper may need to expose model metadata cleanly for Alembic.
- No public API contract changes in this phase.

## DB impact

- Adds initial schema for all documented tables.
- Adds constraints, indexes, and relationships needed by later phases.
- Adds Alembic baseline migration.
- Adds database smoke tests for constraints and indexes.

## API impact

- No route or response behavior changes.
- API docs only inform schema support for future endpoints.

## Frontend impact

- None.

## Security/privacy impact

- `users.password_hash` exists but password hashing/auth implementation is later.
- Database must not include plain password fields.
- Path fields must not accept absolute path values where practical database checks can reject them.
- Migration/test outputs must not include real secrets.
- No API path exposure changes in this phase.

## Test strategy

- Backend lint:
  - `python -m ruff check .`
- Backend tests:
  - `python -m pytest`
- Migration validation:
  - apply Alembic initial migration against fresh PostgreSQL database.
  - run migration inside backend container when Compose database is available.
- Data model smoke tests:
  - required tables exist.
  - required table names are present in SQLAlchemy/Alembic metadata before migration assertions.
  - required indexes exist.
  - invalid enum/check values are rejected.
  - invalid progress is rejected.
  - image media with non-`1` `frame_count`, non-null `fps`, or non-null `duration_seconds` is rejected.
  - duplicate email is rejected.
  - duplicate `(job_id, track_id)` is rejected.
  - second active model is rejected.
  - multiple inactive model versions are accepted.
  - foreign-key integrity is enforced.
  - unsafe path values are rejected where database checks are implemented, including Unix absolute paths, Windows drive-letter paths, UNC-style paths, and `..` traversal segments.
  - nullable `experiment_metrics.metric_value` is accepted.
- Existing health/settings/logging tests remain passing.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found between `docs/phase.md`, `docs/ROADMAP.md`, and relevant docs.
- Ambiguity: exact module layout for ORM models is unspecified.
- Ambiguity: UUID default generation location is unspecified.
- Ambiguity: timestamp timezone convention is unspecified.
- Ambiguity: relative-path validation depth at database layer is partly practical; Phase 3 must still reject obvious unsafe stored paths, while deeper filename/storage sanitization belongs to Phase 6 service utilities.
