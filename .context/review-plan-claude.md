# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 7 plan matches docs in main shape: backend-only media API, auth-required endpoints, upload validation, generated relative paths, metadata extraction, ownership/admin visibility, soft deletion, and targeted backend/security tests.

Implementation should adjust several Phase 7 details before coding: response schema must not expose storage internals, MIME validation must not trust only client-supplied headers, upload write path needs bounded/partial-file cleanup behavior, and validation tests should cover every documented accepted format where feasible.

## Blocking issues

None.

## Important issues

1. Response schema may expose shared-storage internals.
   - Evidence: `.context/plan.md` step 3 says "Define schemas from existing `MediaFile` fields only." Existing `media_files` fields include `stored_path` per `docs/DATA_MODEL.md`.
   - Risk: exposing `uploads/{user_id}/{media_id}/...` gives frontend/API clients internal shared-storage layout. `AGENTS.md` says frontend must stay away from shared storage internals. `docs/ARCHITECTURE.md` says API responses should expose download URLs or logical references, not internal filesystem paths.
   - Required change: plan/schema step should explicitly exclude `stored_path` from normal media responses, or replace it with safe logical resource identifiers only. Do not return absolute paths; avoid returning upload storage layout unless docs explicitly require it.

2. MIME validation trust boundary is underspecified.
   - Evidence: `docs/AUTH_SECURITY.md` requires extension and MIME/type validation. `.context/plan.md` step 4 says validate MIME, but does not say whether implementation checks file content/signature/decoder result or only `UploadFile.content_type`.
   - Risk: client-controlled `Content-Type` can bypass validation if trusted alone. This weakens upload validation and path safety surface.
   - Required change: plan should require MIME/category verification from decoded file content or trusted signature detection, with header MIME treated as advisory. Tests should include mismatched extension/header/content cases.

3. Oversized upload handling and partial-file cleanup need explicit step.
   - Evidence: `docs/AUTH_SECURITY.md` requires oversized files rejected before accepted storage. `.context/plan.md` step 7 writes upload bytes under `STORAGE_ROOT`, but does not define bounded streaming, temp/quarantine write, early size cutoff, or cleanup for partial files when size exceeds limit.
   - Risk: large videos can create memory pressure or leave partial accepted-looking files in shared storage.
   - Required change: plan should require streaming/bounded read with byte limit enforcement, final-path commit only after validation, and cleanup of partial files/directories on validation or write failure.

4. Test plan is not explicit enough for all documented accepted upload formats.
   - Evidence: `docs/TESTING_QA.md` says verify accepted `.jpg`, `.jpeg`, `.png`, `.webp`, `.mp4`, `.avi`, `.mov`, `.mkv`. `.context/plan.md` steps 4 and 6 mention accepted/rejected image/video cases and tiny fixtures, but not all required extensions.
   - Risk: implementation may pass narrow tests while rejecting documented formats, especially `.webp`, `.avi`, `.mov`, or `.mkv`.
   - Required change: add explicit validation coverage for all accepted extensions, or document any fixture/tooling limitation as blocker before marking phase complete.

## Optional improvements

1. Clarify soft-deleted admin detail/list behavior.
   - Evidence: `docs/DATA_MODEL.md` says soft-deleted media may remain visible to admins for audit/history. `.context/plan.md` step 9 says detail loads non-deleted media by ID.
   - Improvement: decide whether Phase 7 admin access includes deleted media metadata or whether that waits for admin/global audit routes. Current docs make this optional, not blocking.

2. Add pagination contract before route implementation.
   - Evidence: `docs/API.md` recommends pagination for growing lists and filters for media type/date/owner-for-admin. `.context/plan.md` says bounded pagination/filtering "where implemented."
   - Improvement: specify minimal query parameters and response shape now to avoid ad hoc endpoint shape.

## Questions for resolution

1. Should normal `GET /api/media` and `GET /api/media/{media_id}` omit `stored_path` entirely, returning only media ID, filename, type, size, dimensions, timestamps, and owner-visible metadata?

2. For video MIME validation, which dependency/tool is approved for content validation and metadata extraction in backend: OpenCV headless, `python-magic`/file signatures, or decoder-based validation through chosen metadata library?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
- `git status --short` output
