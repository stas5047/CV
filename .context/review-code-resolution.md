# Phase 3 Code Review Resolution

## Verdict: FIXED

## Resolution table

| ID | Source | Priority | Review item | Resolution | Reason |
|---|---|---|---|---|---|
| OAI-I-1 | `.context/review-code-openai.md` | important | Image media can be stored with `frame_count = NULL`. | accepted | `docs/DATA_MODEL.md` requires image media to have `frame_count = 1`; SQL `CHECK` needs explicit non-null condition for images. |
| OAI-I-2 | `.context/review-code-openai.md` | important | Relative path checks allow terminal `..` path segments such as `models/..` and `models\..`. | accepted | Phase 3 accepted practical DB checks for `..` traversal segments; terminal parent segments must be rejected too. |

## Accepted critical fixes

- None.

## Accepted important fixes

- Add explicit `frame_count IS NOT NULL` requirement for image media in ORM and migration image metadata check.
- Extend relative path check in ORM and migration to reject paths ending in `/..` or `\..`.
- Add focused database tests proving `frame_count = NULL`, terminal forward traversal, and terminal backslash traversal are rejected.

## Accepted optional fixes

- None.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Fixes applied

- Updated `backend/app/db/models.py` image-media check so image rows require `frame_count IS NOT NULL`, `frame_count = 1`, `fps IS NULL`, and `duration_seconds IS NULL`.
- Updated `backend/migrations/versions/20260513_0001_initial_schema.py` with the same image-media check for fresh PostgreSQL migrations.
- Updated ORM and migration relative-path checks to reject terminal `/..` and `\..` traversal segments.
- Added regression coverage in `backend/tests/test_data_model.py` for image `frame_count = NULL`, `models/..`, `models\..`, `uploads/secret/..`, and `uploads\secret\..`.
- Updated `docs/mistakes-codex.md` for the real missed SQL NULL and terminal traversal cases.

## Final verification

- `python -m pytest tests\test_data_model.py` from `backend/`: PASS, 7 tests.
- `python -m ruff check .` from `backend/`: PASS.
- `python -m pytest` from `backend/`: PASS, 16 tests.
- `docker compose --env-file .env.example config` from repo root: PASS.
- `docker compose --env-file .env.example build backend` from repo root: PASS.
- `docker compose --env-file .env.example run --rm -e DATABASE_URL=postgresql+psycopg://aerovision:change-me-postgres-password@postgres:5432/aerovision_phase3_check backend alembic upgrade head` from repo root: initial run failed because the check database did not exist; after creating `aerovision_phase3_check`, PASS.
