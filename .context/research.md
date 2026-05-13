# Phase 7 Research - Media Upload API and Metadata Extraction

## Current Phase

Confirmed from `docs/phase.md`:

- Phase: `Phase 7 - Media upload API and metadata extraction`
- Direction: Backend
- Goal: Implement media upload, validation, storage, metadata extraction, listing, detail, and soft deletion.
- Risk level: not specified by user input. Assumption: `MEDIUM`, because phase touches authenticated uploads, ownership, storage paths, database records, and file validation.

## Docs Consulted

Required first-read docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase relevant docs from `docs/phase.md`:

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

Existing `.context/` artifacts:

- `.context/status.md` exists but is empty.
- `.context/research.md` exists but was empty before this update.
- `.context/design.md` exists but was empty before this update.
- `.context/plan.md` exists but was empty before this update.
- `.context/review-plan-resolution.md` exists but is empty.

No doc conflict found in consulted files.

## Confirmed Repository Facts

- Git checkout exists.
- `git status --short` showed existing modified files before this work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Required backend project exists under `backend/`.
- Backend already has FastAPI app, `/api` router, auth routes, settings, logging, database session, SQLAlchemy models, Alembic migration, setup/seed/storage bootstrap, security/path helpers, and tests.
- Existing routes included by `backend/app/api/router.py`:
  - auth router
  - health router
- No media API route file exists yet.
- No media schemas exist yet.
- No media upload tests exist yet.
- `backend/pyproject.toml` dependencies currently do not include `python-multipart`, Pillow, or OpenCV.
- `backend/app/core/config.py` already exposes:
  - `storage_root`
  - `max_image_size_mb`
  - `max_video_size_mb`
- `backend/app/core/storage_paths.py` already exposes:
  - `validate_relative_storage_path`
  - `safe_join_storage_path`
  - `sanitize_upload_filename`
  - `safe_download_filename`
- `backend/app/core/authorization.py` already exposes admin and ownership helpers.
- `backend/app/db/models.py` already defines `MediaFile` with documented fields and image metadata check.
- `backend/app/setup.py` already creates required storage folders, including `uploads`.

## Existing Implementation State

Confirmed implemented before Phase 7:

- Health API under `/api/health` and `/api/health/db`.
- Auth API for register, login, and current user.
- JWT auth and inactive-user enforcement.
- Admin dependency and ownership helper primitives.
- Relative path validation and safe storage join helpers.
- Filename sanitization helper.
- Database schema for `media_files`.
- Soft deletion column `media_files.deleted_at`.
- Backend tests for auth, settings, logging, setup, data model, and security utilities.

Confirmed not implemented yet:

- `POST /api/media`
- `GET /api/media`
- `GET /api/media/{media_id}`
- `DELETE /api/media/{media_id}`
- Upload extension/MIME/size/category validation wired to API.
- Generated upload storage path creation through API.
- Media metadata extraction in backend upload flow.
- Media ownership/admin visibility in API.
- Soft-delete API behavior.
- Media pagination/filtering in API.

## Unknowns And Assumptions

Confirmed unknowns:

- Exact paginated response shape is not fully specified in docs.
- Exact error response strings are not specified beyond safe/clear errors.
- Exact behavior when metadata extraction fails but file type/size is valid is not specified.

Assumptions for implementation contract:

- Use existing backend patterns: route modules under `backend/app/api/`, schemas under `backend/app/schemas/`, tests under `backend/tests/`.
- Use FastAPI `UploadFile`, which requires `python-multipart`.
- Use decoder-backed validation for content/category checks: Pillow for image validation/metadata and `opencv-python-headless` for video validation/metadata, unless implementation discovers a platform blocker before source changes.
- Treat uploaded `Content-Type` as advisory only; accepted uploads must pass extension/category checks and decoded content validation.
- Use generated relative paths matching documented pattern: `uploads/{user_id}/{media_id}/original.{ext}`.
- Use sanitized original filename only for display metadata.
- Treat metadata fields as nullable where docs allow unknown values, except image invariant requires `frame_count = 1`, `fps = null`, `duration_seconds = null`.
- If metadata extraction fails for an otherwise valid upload, reject with safe validation error unless implementation can still satisfy required image invariants and file category rules.
- Pagination should be minimal but explicit and bounded, with access control enforced before response.
- Media responses must omit `stored_path` and expose only safe metadata/logical identifiers.
- Phase 7 media list/detail should hide soft-deleted media for both users and admins; deleted rows remain in the database for referential integrity and possible later admin audit/storage cleanup.

## Files Likely Relevant For Implementation

Existing files likely touched:

- `backend/pyproject.toml`
- `backend/app/api/router.py`
- `backend/app/api/deps.py`
- `backend/app/core/config.py`
- `backend/app/core/storage_paths.py`
- `backend/app/core/authorization.py`
- `backend/app/db/models.py`
- `backend/tests/conftest.py`

Likely new backend files, following existing project patterns:

- `backend/app/api/media.py`
- `backend/app/schemas/media.py`
- `backend/app/services/media.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_media_validation.py`

Files not in Phase 7 scope:

- Frontend files.
- CV worker files.
- Job creation/result/download routes.
- Product docs.
- Migration/schema files, unless implementation discovers current `media_files` schema cannot support documented Phase 7 behavior.
