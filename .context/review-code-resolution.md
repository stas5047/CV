# Phase 7 Code Review Resolution

## Verdict: FIXED

OpenAI/Codex code review has one important item. Claude code review file exists but is empty. No product-doc conflict found. No item needs user decision.

## Resolution table

| ID | Source | Priority | Review item | Resolution | Reason |
|---|---|---|---|---|---|
| OAI-I1 | `.context/review-code-openai.md` | important | Video extension/MIME/content mismatch accepted; AVI bytes uploaded as `.mp4` with `video/mp4` returned `201`. | accepted | `docs/AUTH_SECURITY.md` and `.context/plan.md` require extension, MIME/type, size, category, and mismatched header/content rejection before accepted storage. |

## Accepted critical fixes

None.

## Accepted important fixes

- Reject video uploads whose container header does not match the declared extension/category before persisting media metadata.
- Add regression coverage for mismatched video extension/MIME/content.

## Accepted optional fixes

None.

## Rejected items

None.

## Duplicate items

None.

## Items needing user decision

None.

## Fixes applied

- Added video container/header validation in `backend/app/services/media.py`.
- `.avi` uploads must have RIFF/AVI header.
- `.mkv` uploads must have EBML/Matroska header.
- `.mp4` and `.mov` uploads must have ISO BMFF `ftyp`; `.mov` requires QuickTime brand and `.mp4` rejects QuickTime brand.
- Added regression test for AVI bytes submitted as `.mp4` with `video/mp4` in `backend/tests/test_media_validation.py`.

## Final verification

- `cd backend; python -m pytest tests/test_media_api.py tests/test_media_validation.py`: PASS, 21 passed.
- `cd backend; python -m pytest tests/test_auth.py tests/test_security_utils.py`: PASS, 50 passed.
- `cd backend; python -m ruff check .`: PASS.
- `cd backend; python -m pytest`: PASS, 94 passed.
- `docker compose config`: PASS, with existing unset environment variable warnings when no env file is supplied.
- Security/privacy: applicable. Accepted fix tightens video upload trust boundary; no response now exposes `stored_path`, absolute storage paths, storage root, tokens, passwords, password hashes, or secrets.
