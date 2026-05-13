# Phase 3 Status - Database schema and initial Alembic migration

## Current state

- Phase 3 implementation complete and code review final fixes applied.
- SQLAlchemy metadata now defines all required Phase 3 tables:
  - `users`
  - `media_files`
  - `processing_jobs`
  - `detections`
  - `tracks`
  - `model_versions`
  - `experiment_runs`
  - `experiment_metrics`
- Alembic configuration and initial migration are present under `backend/`.
- Backend Docker image now copies Alembic config and migration files so container migrations can run.
- Backend index updated for current files and commands.
- Code review fixes tightened image-media NULL handling and terminal `..` path traversal checks in ORM, migration, and tests.

## Quality gates run

| Command | Result |
|---|---|
| `python -m pytest tests\test_data_model.py` from `backend/` | PASS |
| `python -m ruff check .` from `backend/` | PASS |
| `python -m pytest` from `backend/` | PASS |
| `docker compose --env-file .env.example config` from repo root | PASS |
| `docker compose --env-file .env.example build backend` from repo root | PASS |
| `docker compose --env-file .env.example run --rm -e DATABASE_URL=postgresql+psycopg://aerovision:change-me-postgres-password@postgres:5432/aerovision_phase3_check backend alembic upgrade head` from repo root | PASS |

## Notes

- Phase 3 stayed scoped to schema, migration plumbing, focused tests, backend Docker migration availability, and backend index update.
- No auth endpoints, seed/setup command, upload API, job API, worker queue loop, frontend UI, or training behavior implemented.
- No source/doc contract conflict found.
- Migration-in-container check database `aerovision_phase3_check` had to be created before the final migration command could run.
- Real mistake logged in `docs/mistakes-codex.md`: initial SQL check allowed image `frame_count = NULL` and terminal path traversal segments.
