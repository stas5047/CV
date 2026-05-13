# Phase 11 Design Contract

## Phase goal

Build admin-only backend APIs for global stats, global job history, safe user listing, and conservative storage cleanup:

- `GET /api/admin/stats`
- `GET /api/admin/jobs`
- `GET /api/admin/users`
- `POST /api/admin/storage/cleanup`

No frontend, worker, training, migration, or product-doc work in this phase.

## Intended behavior from docs

Confirmed:

- All `/api/admin/*` routes require authenticated active admin user.
- Guests and regular users cannot access admin routes.
- Admin can view global jobs/history and basic users list.
- User list must exclude password hashes and sensitive fields.
- Admin stats must be global processing/system statistics, limited to documented CV/backend data.
- Storage cleanup must be safe and conservative.
- Cleanup must not delete:
  - active model weights;
  - active model cards;
  - files referenced by non-deleted records;
  - recent user results accidentally;
  - files needed by visible completed jobs.
- Cleanup logs must omit secrets, tokens, unsafe absolute user-facing paths, passwords, password hashes, DB passwords, and sensitive env values.
- API responses must not expose absolute host/container paths.
- API outputs must remain inside CV-only boundary.

Assumptions:

- Admin jobs response may reuse existing safe `JobListResponse`/`JobDetailResponse` semantics.
- Basic users response may reuse `UserResponse` fields.
- Stats response should aggregate only from existing documented tables; exact fields remain an implementation ambiguity because docs do not name them.
- Cleanup should default to dry-run/report-only when deletion eligibility is ambiguous. Because no retention policy exists, Phase 11 must not physically delete files from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/`. Physical deletion, if implemented, is limited to clearly safe unreferenced `temp/` files.

## Architecture decisions

- Add a dedicated `admin` router under existing `/api` router with prefix `/admin`.
- Use `get_current_admin_user` on every admin endpoint.
- Keep route handlers thin; place aggregation and cleanup rules in `backend/app/services/admin.py`.
- Keep Pydantic response models in `backend/app/schemas/admin.py`.
- Reuse existing SQLAlchemy session dependency and ORM models.
- Reuse existing job-list logic where it preserves safe output and global admin visibility.
- Do not add DB tables, migrations, Redis/Celery, background cleanup jobs, or worker coupling.
- Do not expose storage internals in responses. Cleanup reports should prefer counts and categories. If paths are returned at all, they must be relative/logical and never absolute.

## Backend impact

Touched:

- New admin router.
- New admin schemas.
- New admin service functions.
- Main API router inclusion.
- Backend tests for admin access and cleanup safety.

Not touched:

- Auth token format.
- Password hashing.
- Media upload behavior.
- Job creation behavior.
- CV worker behavior.
- Database schema.
- Frontend routes.

## API impact

Confirmed route additions:

- `GET /api/admin/stats`
- `GET /api/admin/jobs`
- `GET /api/admin/users`
- `POST /api/admin/storage/cleanup`

Contract limits:

- Do not expose `password_hash`.
- Do not expose absolute paths.
- Do not expose forbidden CV boundary data.
- Do not create or modify jobs through admin history endpoint.
- Do not physically delete referenced files.

Ambiguous:

- Exact JSON field names for admin stats.
- Cleanup request body shape.
- Cleanup response body shape.
- Retention threshold for old files/recent results.

## DB impact

- No schema change planned.
- Queries aggregate from existing documented tables.
- Cleanup reference protection must inspect existing relative path fields:
  - `media_files.stored_path`;
  - `processing_jobs.result_media_path`;
  - `processing_jobs.csv_path`;
  - `processing_jobs.json_path`;
  - `model_versions.weights_path`;
  - `experiment_runs.artifacts_path`.
- Non-deleted media/jobs and active model artifacts must be protected.
- Active model-card protection must be derived from the active model directory or documented `models/{model_version_id}/model_card.json` layout because the database stores `weights_path` but no explicit model-card path.
- Referenced directories, including `experiment_runs.artifacts_path` and derived active model directories, must be protected as prefixes so descendants cannot be deleted by exact-path-only cleanup logic.

## Security/privacy impact

- High sensitivity: admin endpoints expose global data and cleanup touches filesystem.
- Enforce admin role server-side on all endpoints.
- Inactive admin tokens must be rejected through existing active-user dependency chain.
- Regular users receive 403, not partial data.
- Cleanup path handling must use safe join under `STORAGE_ROOT`.
- Logs must describe cleanup counts/actions without secrets or absolute host paths.
- Responses must not include password hashes, raw tokens, JWT secrets, DB passwords, or stack traces.
- Cleanup must not physically delete from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/` in Phase 11 because no retention window exists.

## Test strategy

Targeted backend tests only:

- Guest cannot access admin routes.
- Regular user cannot access admin routes.
- Inactive admin token cannot access admin routes.
- Admin can access stats, jobs, users, cleanup endpoint.
- Admin users endpoint omits `password_hash` and sensitive fields.
- Admin jobs endpoint returns global job history safely and omits internal result path fields/absolute paths.
- Cleanup protects active model weights and derived active model-card/directory paths.
- Cleanup protects files referenced by non-deleted records.
- Cleanup protects child files under referenced artifact directories and derived active model directories.
- Cleanup preserves a fresh unreferenced file under `results/`.
- Cleanup physically deletes only clearly safe unreferenced files under `temp/`, if physical deletion is implemented at all.
- Cleanup protects files needed by visible completed jobs.
- Cleanup does not escape `STORAGE_ROOT`.
- Cleanup logs do not include secrets or absolute storage root.

Relevant gates:

- `python -m ruff check .` from `backend/`
- `python -m pytest tests/test_admin_api.py` from `backend/`
- `python -m pytest` from `backend/` if targeted tests pass

Not relevant for this phase:

- Frontend build/typecheck.
- Worker/CV processing tests.
- Docker full-stack smoke unless backend wiring changes break container startup.

## Ambiguities or conflicts

WARNING: CONFLICT:

- `docs/index.md` stale implementation-state text conflicts with current repository and `backend/index.md`. It says only Phase 1 placeholders exist; repo has backend implementation through Phase 10.

Ambiguities:

- Stats field contract absent.
- Cleanup request/response contract absent.
- "Recent user results" retention window absent.
- Physical cleanup scope absent beyond negative safety rules.

Planning position:

- Implement only what docs confirm.
- Do not invent a retention window. Use temp-only physical deletion plus report-only behavior for other storage categories.
- If implementation cannot define stats/cleanup JSON shape without inventing unsafe behavior, stop before source edits and request user/product-doc decision.
