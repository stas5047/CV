# Phase 7 Design - Media Upload API and Metadata Extraction

## Phase Goal

Build backend media API for authenticated image/video upload, validation, storage, metadata persistence, media listing/detail, and soft deletion, exactly as Phase 7 documents require.

## Intended Behavior From Docs

Confirmed behavior:

- `POST /api/media` uploads and registers image or video media.
- `GET /api/media` lists media visible to current user.
- `GET /api/media/{media_id}` returns media metadata.
- `DELETE /api/media/{media_id}` soft-deletes media metadata.
- Guests cannot access media endpoints.
- Regular users can access only own media.
- Admins can access all media metadata.
- Admin uploads are scoped to admin account.
- Deletion uses `deleted_at` only.
- Physical file deletion is not part of Phase 7.
- Soft-deleted media is hidden from normal user lists.
- Upload validation must happen before accepted storage and job creation:
  - extension
  - MIME type
  - file size
  - file category: image or video
  - filename safety
- Accepted image extensions:
  - `.jpg`
  - `.jpeg`
  - `.png`
  - `.webp`
- Accepted video extensions:
  - `.mp4`
  - `.avi`
  - `.mov`
  - `.mkv`
- Upload limits come from:
  - `MAX_IMAGE_SIZE_MB`
  - `MAX_VIDEO_SIZE_MB`
- Internal storage paths must be generated, relative, and under `STORAGE_ROOT`.
- Raw user filenames must not control filesystem paths.
- Original filename may be stored only after sanitization.
- Recommended upload path pattern:
  - `uploads/{user_id}/{media_id}/original.{ext}`
- PostgreSQL stores metadata only, never binary media.
- Metadata to extract when feasible:
  - width
  - height
  - frame count
  - FPS
  - duration
- Image records must store:
  - `frame_count = 1`
  - `fps = null`
  - `duration_seconds = null`
- API responses must not expose unsafe absolute filesystem paths.
- No long media processing belongs in upload request.

## Architecture Decisions

Confirmed architecture:

- Backend owns public media API, auth, validation, upload storage, and `media_files` records.
- Shared storage stores upload bytes.
- Database stores relative `stored_path` and metadata only.
- CV worker remains out of Phase 7.
- Frontend remains out of Phase 7.

Implementation design:

- Add one media API router under `/api/media`.
- Keep route handlers thin.
- Put upload validation, storage path generation, file writing, and metadata extraction in backend service/helper code.
- Reuse existing auth dependency `get_current_active_user`.
- Reuse existing `ensure_owner_or_admin` and `owner_id_from_media`.
- Reuse existing `sanitize_upload_filename`, `validate_relative_storage_path`, and `safe_join_storage_path`.
- Generate `media_id` before writing file so path can include `{media_id}`.
- Write file only after extension/category/size checks pass.
- Store generated relative path, never returned as absolute host/container path.
- Use database transaction so persisted record matches accepted upload. If file write succeeds but DB commit fails, remove the newly written upload file as cleanup best effort.
- Do not delete physical file on `DELETE /api/media`; only set `deleted_at`.
- Exclude deleted media from regular list/detail behavior. Admin visibility may include broader metadata, but this phase should not add separate admin-only routes absent from Phase 7.

## Backend Impact

Touched:

- API router include media router.
- New schemas for media responses and paginated/list responses.
- New media service/helpers for validation, storage, and metadata.
- Tests for media endpoints and validation.
- Dependency manifest may need upload/metadata dependencies.

Not touched:

- Auth token format.
- Job creation.
- Result/download routes.
- Worker processing.
- Frontend UI.

## API Impact

Phase 7 endpoints only:

- `POST /api/media`
- `GET /api/media`
- `GET /api/media/{media_id}`
- `DELETE /api/media/{media_id}`

Response design constraints:

- Return media metadata for create/read/list.
- Include safe identifiers and metadata.
- Omit `stored_path` from normal create/read/list responses.
- Do not expose shared-storage layout such as `uploads/{user_id}/{media_id}/...` unless a later doc explicitly requires it.
- Do not expose absolute file paths.
- Do not expose password hashes, tokens, secrets, stack traces, or storage root.
- Use clear HTTP errors for unauthorized, forbidden/hidden ownership, unsupported file type, invalid MIME, oversized file, unsafe filename, missing resource.
- Use minimal bounded pagination for list responses:
  - `limit` with a conservative maximum;
  - `offset`;
  - optional `media_type`;
  - admin-only owner filter only if implemented with backend role enforcement.

## DB Impact

Existing `media_files` table already has required Phase 7 fields:

- `id`
- `user_id`
- `original_filename`
- `stored_path`
- `media_type`
- `mime_type`
- `file_size_bytes`
- `width`
- `height`
- `frame_count`
- `fps`
- `duration_seconds`
- `deleted_at`
- `created_at`

Expected DB changes:

- No schema change expected.
- If implementation discovers missing constraint/index versus docs, stop and report before modifying migration/schema.

## Security/Privacy Impact

Touched:

- Authenticated upload endpoint.
- Ownership rules for list/detail/delete.
- Admin broader metadata visibility.
- File validation before storage.
- Filename sanitization.
- Path traversal prevention.
- Relative path rule.
- Size limits.
- MIME/extension/category checks.

Security decisions:

- Reject missing/invalid token through existing auth.
- Hide cross-owner resources with safe not-found behavior.
- Sanitize original filename before persistence.
- Never use client-supplied filename as storage path.
- Never accept client-supplied storage path.
- Treat request `Content-Type` as advisory; verify image/video category by decoded file content or trusted signature/decoder result.
- Stream or spool upload bytes with configured byte limits instead of loading unbounded files into memory.
- Write to a temporary path first, then move/commit to final generated path only after validation passes.
- Clean up partial files/directories on validation failure, write failure, or database commit failure.
- Never execute uploaded files.
- Never return absolute filesystem path.
- Avoid logging file bytes, tokens, passwords, secrets, or unsafe paths.

Soft-delete visibility decision:

- Phase 7 `GET /api/media` and `GET /api/media/{media_id}` hide soft-deleted media for both regular users and admins.
- Deleted rows remain in PostgreSQL for referential integrity and possible future admin audit/storage cleanup.
- Do not add `include_deleted` or admin audit routes in this phase.

## Test Strategy

Relevant checks only:

- Backend media API tests:
  - valid image upload creates `media_files` row
  - valid video upload creates `media_files` row
  - image metadata invariant: `frame_count = 1`, `fps = null`, `duration_seconds = null`
  - valid video metadata fields filled when feasible
  - unsupported extension rejected
  - invalid MIME rejected
  - oversized image rejected
  - oversized video rejected
  - unsafe filename/path traversal rejected or sanitized safely
  - missing token rejected
  - inactive user rejected through auth dependency
  - regular user lists own media only
  - regular user cannot read/delete another user's media
  - admin can view broader media metadata
  - delete sets `deleted_at`
  - soft-deleted media hidden from normal lists/detail
  - stored paths are generated and relative
  - API response does not include absolute storage path
  - API response does not include `stored_path` or shared-storage layout
- Backend targeted commands:
  - `cd backend; python -m pytest tests/test_media_api.py tests/test_media_validation.py`
  - `cd backend; python -m pytest tests/test_auth.py tests/test_security_utils.py`
  - `cd backend; python -m ruff check .`

Accepted-format coverage:

- Validation tests must cover accepted extensions `.jpg`, `.jpeg`, `.png`, `.webp`, `.mp4`, `.avi`, `.mov`, and `.mkv` where fixtures/tooling support them.
- If a required video container fixture cannot be generated reliably in this phase, document the exact limitation before marking the gate complete.
- Tests must include mismatched extension/header/content cases; client-supplied MIME alone is not sufficient.

Docker smoke only if backend dependency/runtime changes require it:

- `docker compose config`
- backend container startup smoke if dependency changes affect image build.

## Ambiguities Or Conflicts

No confirmed doc conflict.

Ambiguities:

- User input left `<PHASE NUMBER AND TITLE>` and `<LOW | MEDIUM | HIGH>` placeholders unfilled.
- Docs do not specify exact media response fields beyond database metadata and no unsafe paths.
