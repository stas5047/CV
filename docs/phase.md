## Phase 7 - Media upload API and metadata extraction

**Direction:** Backend  
**Goal:** Implement media upload, validation, storage, metadata extraction, listing, detail, and soft deletion.

### Scope

- Implement endpoints:
  - `POST /api/media`;
  - `GET /api/media`;
  - `GET /api/media/{media_id}`;
  - `DELETE /api/media/{media_id}`.
- Validate extension, MIME type, file category, size, and filename safety before storage.
- Accept required image and video formats only.
- Generate internal storage paths using user ID and media ID.
- Store original filename only as sanitized display metadata.
- Extract media metadata where feasible:
  - width;
  - height;
  - frame count;
  - FPS;
  - duration.
- Ensure image records use `frame_count = 1`, `fps = null`, and `duration_seconds = null`.
- Enforce user ownership and admin visibility rules.
- Implement soft deletion through `deleted_at` only.
- Add pagination/filtering where useful.
- Add tests for accepted/rejected uploads and ownership.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Valid images upload and create `media_files` records.
- Valid videos upload and create `media_files` records.
- Unsupported extensions, invalid MIME types, oversized files, unsafe filenames, and path traversal attempts are rejected.
- Users see only own media; admins can view broader media metadata.
- Stored paths are generated and relative.
- Soft-deleted media is hidden from normal user lists.

### Commit

`feat(backend-media): add validated media upload and metadata API`