# Phase 7 Implementation Plan - Media Upload API and Metadata Extraction

## Scope

Only Phase 7 work:

- Backend media upload/list/detail/delete API.
- Upload validation.
- Generated relative upload storage paths.
- Metadata extraction.
- Ownership/admin visibility.
- Soft deletion.
- Relevant backend tests.

No frontend, worker, job creation, result downloads, model APIs, experiment APIs, or product docs.

## Ordered Atomic Plan

1. `@role/developer-backend` Confirm current backend dependency set.
   - Verify whether upload handling and metadata extraction dependencies exist in `backend/pyproject.toml`.
   - Verifiable: dependency gap list is explicit before edits.

2. `@role/developer-backend` Add only dependencies needed for Phase 7 upload handling and metadata extraction.
   - Add `python-multipart` for FastAPI file uploads.
   - Add Pillow for image content validation and metadata if not already available.
   - Add `opencv-python-headless` for video content validation and metadata if not already available.
   - Verifiable: backend dependency file contains needed packages and no unrelated packages.

3. `@role/developer-backend` Add media response schemas.
   - Define schemas from safe `MediaFile` metadata fields only.
   - Exclude `stored_path` from normal API responses.
   - Do not expose shared-storage layout, absolute paths, storage root, or raw file references.
   - Exclude password, tokens, secrets, and absolute paths.
   - Verifiable: schema fields match `docs/DATA_MODEL.md` media metadata and API safety rules.

4. `@role/developer-auth-security` Add upload validation helpers.
   - Validate extension, MIME, size, media category, and sanitized filename.
   - Treat uploaded `Content-Type` as advisory only.
   - Verify image/video category from decoded content or trusted signature/decoder result.
   - Reject mismatched extension/header/content combinations.
   - Use `MAX_IMAGE_SIZE_MB` and `MAX_VIDEO_SIZE_MB`.
   - Reject unsupported extensions, invalid MIME/category mismatch, oversized files, and unsafe inputs.
   - Verifiable: unit tests cover accepted/rejected image/video cases.

5. `@role/developer-auth-security` Add generated path helper for uploaded media.
   - Generate `uploads/{user_id}/{media_id}/original.{ext}`.
   - Validate generated path through existing relative-path helper.
   - Join only through existing safe storage helper.
   - Verifiable: tests prove generated path is relative and cannot escape `STORAGE_ROOT`.

6. `@role/developer-backend` Add metadata extraction helper.
   - Extract image width/height and set image invariants.
   - Extract video width/height/frame count/FPS/duration where feasible.
   - Do not run CV inference or long processing.
   - Verifiable: tests assert image and video metadata behavior using tiny fixture files.

7. `@role/developer-backend` Add media service create flow.
   - Authenticate current active user.
   - Validate upload before accepted storage.
   - Generate `media_id` and relative path.
   - Stream or spool upload bytes with configured byte limit enforcement.
   - Write to a temporary path first.
   - Move/commit to final generated path only after validation succeeds.
   - Clean up partial files/directories on validation failure or write failure.
   - Create `MediaFile` row with sanitized original filename and metadata.
   - On DB commit failure, clean up newly written file best effort.
   - Verifiable: valid upload creates exactly one file and one row with matching relative path.

8. `@role/developer-backend` Add media list query.
   - Regular user: own non-deleted media only.
   - Admin: broader visible media metadata per docs.
   - Add explicit bounded pagination with `limit` and `offset`.
   - Add `media_type` filter.
   - Add owner filtering only for admins if implemented in this phase.
   - Verifiable: tests show regular user cannot see another user's media; admin can.

9. `@role/developer-backend` Add media detail query.
   - Load non-deleted media by ID.
   - Enforce owner-or-admin access.
   - Hide soft-deleted media for both users and admins in Phase 7 media detail.
   - Return safe metadata response.
   - Verifiable: own media returns 200; cross-owner access returns safe not-found/forbidden behavior without leaks.

10. `@role/developer-backend` Add media soft-delete flow.
    - Enforce owner-or-admin access.
    - Set `deleted_at`.
    - Do not delete physical upload file.
    - Do not alter existing job records.
    - Do not add `include_deleted` or admin audit behavior in this phase.
    - Verifiable: delete response succeeds; row has `deleted_at`; list/detail hides deleted media for normal access.

11. `@role/developer-backend` Add media API router.
    - Implement `POST /api/media`.
    - Implement `GET /api/media`.
    - Implement `GET /api/media/{media_id}`.
    - Implement `DELETE /api/media/{media_id}`.
    - Include router under existing `/api` router.
    - Verifiable: routes exist under exact documented paths.

12. `@role/developer-auth-security` Add API safety assertions.
    - Verify responses do not include absolute host/container paths.
    - Verify responses do not include `stored_path` or internal shared-storage layout.
    - Verify errors do not expose stack traces, secrets, raw tokens, or storage root.
    - Verifiable: tests inspect representative response bodies.

13. `@role/tester` Add documented format and MIME trust-boundary tests.
    - Cover accepted image extensions `.jpg`, `.jpeg`, `.png`, `.webp`.
    - Cover accepted video extensions `.mp4`, `.avi`, `.mov`, `.mkv` where fixtures/tooling support them.
    - Cover mismatched extension/header/content cases.
    - Cover oversized stream cleanup and partial-file cleanup.
    - If a required container fixture cannot be generated reliably, document exact limitation before marking the gate complete.
    - Verifiable: validation tests prove documented formats and rejection paths.

14. `@role/tester` Run targeted backend tests for Phase 7.
    - Command: `cd backend; python -m pytest tests/test_media_api.py tests/test_media_validation.py`
    - Expected: `PASS`.

15. `@role/tester` Run auth/security regression tests.
    - Command: `cd backend; python -m pytest tests/test_auth.py tests/test_security_utils.py`
    - Expected: `PASS`.

16. `@role/tester` Run backend lint.
    - Command: `cd backend; python -m ruff check .`
    - Expected: `PASS`.

17. `@role/tester` Run Docker config check if dependency or Compose runtime behavior changed.
    - Command: `docker compose config`
    - Expected: `PASS`.
    - If not run because no Compose change and no image smoke requested, report as skipped with reason.

18. `@role/code-reviewer` Review Phase 7 diff against docs.
    - Check endpoint paths, ownership, admin visibility, upload validation, path safety, relative paths, soft deletion, no source scope creep, and no frontend/worker/job work.
    - Verifiable: review notes have no unresolved Phase 7 blockers.

19. `@role/docs-maintainer` Decide docs/index updates.
    - Product docs should not change for this phase contract.
    - Update backend component index only if implementation changes backend-local commands or file inventory policy requires it.
    - Verifiable: docs updates are either absent with reason or limited to implementation notes/index, not product behavior.
