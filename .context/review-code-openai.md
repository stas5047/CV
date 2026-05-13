# OpenAI/Codex Code Review - Phase 3

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 3 mostly matches scope: SQLAlchemy models, Alembic config, initial migration, Docker migration availability, and focused DB tests. No auth/API/upload/worker/frontend/training scope creep found.

Two real schema/test gaps remain before approval: image media can persist with `frame_count = NULL`, and path checks still allow terminal parent-directory traversal such as `models/..` and `models\..`.

## Critical issues

None.

## Important issues

1. Image media can be stored with `frame_count = NULL`.
   - Evidence: `docs/DATA_MODEL.md:103` and `docs/DATA_MODEL.md:112` require image media `frame_count = 1`.
   - Evidence: `backend/app/db/models.py:96` to `backend/app/db/models.py:99` and `backend/migrations/versions/20260513_0001_initial_schema.py:71` to `backend/migrations/versions/20260513_0001_initial_schema.py:74` use `frame_count = 1` inside a SQL `CHECK`; SQL `CHECK` accepts `UNKNOWN`, so `frame_count NULL` passes.
   - Evidence: `backend/app/db/models.py:114` and migration line `62` make `frame_count` nullable.
   - Evidence: targeted in-memory DB probe accepted `image_null_frame_count`.
   - Impact: invalid image metadata can enter database before upload/API validation exists, violating documented media invariant and Phase 3 plan test intent at `.context/plan.md:21`.

2. Relative path checks allow terminal `..` path segments.
   - Evidence: `.context/review-plan-resolution.md:8` and `.context/plan.md:43` to `.context/plan.md:45` require `..` traversal segments to fail where DB checks are implemented.
   - Evidence: `backend/app/db/models.py:57` to `backend/app/db/models.py:60` and migration lines `27` to `30` reject leading and middle traversal, but not terminal `.../..` or `...\..`.
   - Evidence: targeted in-memory DB probe accepted `models/..` and `models\..` in `model_versions.weights_path`.
   - Impact: later path joins could resolve outside intended subtrees unless every later service layer catches it. Phase 3 promised practical DB checks for unsafe stored paths; this is one missing traversal case.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: inspected. Changed set includes Phase 3 context updates, backend DB files, migration files, and tests.
- `rtk git diff --stat`: inspected.
- `rtk git diff`: inspected.
- `python -m pytest tests\test_data_model.py` from `backend/`: PASS per `.context/status.md:23`; not rerun.
- `python -m ruff check .` from `backend/`: PASS per `.context/status.md:24`; not rerun.
- `python -m pytest` from `backend/`: PASS per `.context/status.md:25`; not rerun.
- `docker compose --env-file .env.example config`: PASS per `.context/status.md:26`; not rerun.
- `docker compose --env-file .env.example build backend`: PASS per `.context/status.md:27`; not rerun.
- `docker compose --env-file .env.example run --rm ... backend alembic upgrade head`: PASS per `.context/status.md:28`; not rerun.
- Targeted DB constraint probe from `backend/`: FAIL for review purposes. Bad rows `image_null_frame_count`, `terminal_forward_traversal`, and `terminal_back_traversal` were accepted.

## Security/privacy assessment

Path traversal gap is security-relevant because database path fields are later interpreted under `STORAGE_ROOT` or `MODELS_ROOT` (`docs/DATA_MODEL.md:365` to `docs/DATA_MODEL.md:378`). No secrets, tokens, plaintext passwords, binary media, datasets, model weights, or result files were found in touched source.

## Positive findings

- All required Phase 3 tables are represented in ORM metadata and migration.
- Required documented indexes are present for jobs, media, detections, tracks, experiments, and metrics.
- Active model uniqueness uses a partial unique index, allowing multiple inactive model rows while rejecting multiple active rows.
- No Celery/Redis, backend-worker HTTP job loop, auth endpoints, upload API, frontend UI, or training launch code added.
- Backend index was updated to reflect new Alembic/model commands and current contents.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `backend/app/db/models.py`
- `backend/migrations/env.py`
- `backend/migrations/versions/20260513_0001_initial_schema.py`
- `backend/tests/test_data_model.py`
- `backend/alembic.ini`
- `backend/Dockerfile`
- `backend/app/db/__init__.py`
- `backend/index.md`
- `backend/pyproject.toml`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
