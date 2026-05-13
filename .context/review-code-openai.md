# Phase 7 OpenAI/Codex Code Review

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 7 backend media API mostly matches docs: protected `/api/media` endpoints exist, ownership/admin visibility works, API responses omit `stored_path`, uploads use generated relative storage paths, image metadata invariants hold, soft deletion hides media, and targeted/full backend gates pass.

One important validation defect remains: video content is only checked as "decodable video", not as content matching claimed extension/MIME. This misses planning contract for mismatched video extension/header/content rejection.

## Critical issues

None.

## Important issues

1. Video extension/MIME/content mismatch accepted.
   - Evidence: `backend/app/services/media.py:169-185` validates video MIME from client-provided `UploadFile.content_type` against extension allow-list only.
   - Evidence: `backend/app/services/media.py:293-323` uses `cv2.VideoCapture` only to prove file is decodable video; no video container/format check equivalent to image check at `backend/app/services/media.py:262-273`.
   - Evidence: `backend/tests/test_media_validation.py:160-171` covers mismatched content only for image, not video.
   - Evidence: ad hoc probe uploaded AVI/MJPG bytes as `wrong.mp4` with `video/mp4`; API returned `status=201`.
   - Docs/contract: `docs/AUTH_SECURITY.md` requires extension, MIME/type, size, and file category validation before storage. `.context/plan.md` requires rejecting mismatched extension/header/content combinations and treating client `Content-Type` as advisory.
   - Impact: backend can persist misleading media metadata (`mime_type = video/mp4`, `original_filename = wrong.mp4`) for non-MP4 content, weakening upload validation and future worker assumptions.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: inspected; changed surface includes Phase 7 backend media files/tests plus context/docs updates.
- `rtk git diff --stat`: inspected.
- `rtk git diff`: inspected; untracked media files/tests were read directly because diff did not include their content.
- `python -m pytest tests/test_media_api.py tests/test_media_validation.py` from `backend/`: PASS, 20 passed.
- `python -m pytest tests/test_auth.py tests/test_security_utils.py` from `backend/`: PASS, 50 passed.
- `python -m pytest` from `backend/`: PASS, 93 passed.
- `python -m ruff check .` from `backend/`: PASS.
- `docker compose config`: PASS, with existing unset-environment warnings when no env file supplied.
- Ad hoc video mismatch probe: FAIL for expected behavior; returned `201` for AVI bytes submitted as `.mp4`/`video/mp4`.

## Security/privacy assessment

Applicable. Ownership checks, active-user auth, relative stored paths, and response path hiding look correct in reviewed Phase 7 code. Remaining risk is upload validation trust boundary for videos: client-declared MIME plus generic decoder success is insufficient to reject mismatched video extension/content.

## Positive findings

- Media response schema omits `stored_path` and absolute filesystem paths.
- Regular users list/read/delete only own non-deleted media; admins can see all non-deleted media metadata.
- Soft deletion uses `deleted_at` and does not remove physical files.
- Image validation checks decoded image format against extension.
- Tests cover accepted image formats, accepted video extensions, oversized uploads, soft deletion, cross-owner denial, and no media row after oversized rejection.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
- `backend/app/api/router.py`
- `backend/app/api/media.py`
- `backend/app/schemas/media.py`
- `backend/app/services/media.py`
- `backend/app/core/storage_paths.py`
- `backend/app/db/models.py`
- `backend/pyproject.toml`
- `backend/index.md`
- `backend/tests/conftest.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_media_validation.py`
