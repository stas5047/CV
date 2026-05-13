# Phase 9 Status - Job Creation API and Model Selection Resolution

## Implementation

- Phase implemented: `Phase 9 - Job creation API and model selection resolution`.
- Scope kept to backend `POST /api/jobs`, active-user authentication, own-media validation, soft-deleted media rejection, processing parameter defaults/validation, model selection priority, queued job persistence, tests, and backend index update.
- Later phases not implemented: job list/detail/cancel endpoints, result/download APIs, CV worker queue polling/claiming, media processing, detections/tracks/exports, frontend upload/job UI, experiments/admin APIs.

## Files Changed By Codex

- `backend/app/api/router.py`
- `backend/app/api/jobs.py`
- `backend/app/core/config.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/jobs.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_settings.py`
- `backend/index.md`
- `.context/status.md`

## Quality Gates

- `cd backend; python -m pytest tests/test_jobs_api.py` - PASS, 19 passed.
- `cd backend; python -m pytest tests/test_media_api.py tests/test_models_api.py tests/test_auth.py tests/test_settings.py` - PASS, 48 passed.
- `cd backend; python -m ruff check .` - PASS.

## Code Review Resolution

- `.context/review-code-resolution.md` updated.
- `.context/review-code-openai.md` verdict: APPROVED; no critical, important, or optional issues.
- `.context/review-code-claude.md` is absent or empty; no issues to resolve.
- No accepted source fixes were required after code review.
- Final verification reran after resolution update and passed:
  - `cd backend; python -m pytest tests/test_jobs_api.py` - PASS, 19 passed.
  - `cd backend; python -m pytest tests/test_media_api.py tests/test_models_api.py tests/test_auth.py tests/test_settings.py` - PASS, 48 passed.
  - `cd backend; python -m ruff check .` - PASS.

## Security And Privacy

- `POST /api/jobs` requires active JWT user.
- Job creation is limited to media owned by the authenticated user, including admins.
- Missing, cross-owner, and soft-deleted media return safe not-found behavior.
- Invalid parameters and unavailable model resolution create no queued job.
- Response excludes result/export path fields and exposes no absolute storage paths, passwords, password hashes, tokens, or secrets.

## Notes

- Existing stale-doc conflict remains as recorded in `.context/research.md`: `docs/index.md` and `README.md` current-state text lag actual backend implementation. Phase selection came from `docs/phase.md`.
- No schema/migration change was needed; existing `processing_jobs`, `media_files`, and `model_versions` tables support Phase 9.
- Explicit inactive registered model selection is allowed by the Phase 9 contract; active model is only default selection.
- No real mistake logged.
