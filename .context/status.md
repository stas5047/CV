# Phase 11 Status

## Current state

Implemented.

## Scope completed

- Added admin-only backend routes:
  - `GET /api/admin/stats`
  - `GET /api/admin/jobs`
  - `GET /api/admin/users`
  - `POST /api/admin/storage/cleanup`
- Added safe admin response schemas.
- Added admin service logic for global stats, user listing, job history reuse, and conservative storage cleanup.
- Storage cleanup physically deletes only unreferenced files under `temp/`.
- Storage cleanup protects non-deleted DB references, active model weights, derived active model card/directories, experiment artifact directories, and fresh result files.
- Added targeted admin API tests.
- Updated `backend/index.md`.
- Final code-review fix corrected dry-run cleanup accounting with explicit `would_delete_*` response counters.

## Quality gates

- `python -m pytest tests/test_admin_api.py` from `backend/`: PASS
- `python -m ruff check .` from `backend/`: PASS
- `python -m pytest` from `backend/`: PASS

## Security/privacy

- All admin routes use `get_current_admin_user`.
- Regular users receive 403 for admin routes; inactive admin tokens receive 401 through active-user dependency.
- User listing uses `UserResponse` and does not expose password hashes.
- Job listing reuses safe job detail responses and does not expose internal result paths.
- Cleanup response and logs contain counts/categories only, not absolute storage paths or secrets.
- Dry-run cleanup logs and responses now distinguish actual deletions from would-delete candidates.

## Deviations

- None from `.context/design.md`, `.context/plan.md`, or `.context/review-plan-resolution.md`.

## Remaining risks

- Product docs do not define retention policy for non-temp storage cleanup, so `uploads/`, `results/`, `reports/`, `models/`, and `datasets/` remain report-only.
- `.context/research.md` notes stale implementation-state text in `docs/index.md`; no product behavior conflict found for Phase 11.
