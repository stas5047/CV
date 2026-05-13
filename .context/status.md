# Phase 8 Status - Model Registry Backend API

## Implementation

- Phase implemented: `Phase 8 - Model registry backend API`.
- Scope kept to backend model list/detail/register/activate API, admin-only mutations, active-user access, relative weights path validation, active-model uniqueness, tests, and backend index update.
- Later phases not implemented: jobs, results/downloads, experiment API, frontend model page, CV worker model loading, training utilities, model weight upload.

## Files Changed By Codex

- `backend/app/api/router.py`
- `backend/app/api/models.py`
- `backend/app/schemas/models.py`
- `backend/app/services/models.py`
- `backend/tests/test_models_api.py`
- `backend/index.md`
- `.context/status.md`

## Quality Gates

- `cd backend; python -m pytest tests/test_models_api.py` - PASS, 15 passed.
- `cd backend; python -m ruff check .` - PASS.
- `cd backend; python -m pytest tests/test_data_model.py tests/test_security_utils.py tests/test_auth.py` - PASS, 57 passed.

## Code Review Resolution

- `.context/review-code-resolution.md` updated.
- `.context/review-code-openai.md` verdict: APPROVED; no critical, important, or optional issues.
- `.context/review-code-claude.md` exists but is empty; no issues to resolve.
- No accepted source fixes were required after code review.
- Final verification reran after resolution update and passed:
  - `cd backend; python -m ruff check .` - PASS.
  - `cd backend; python -m pytest tests/test_models_api.py` - PASS, 15 passed.
  - `cd backend; python -m pytest tests/test_data_model.py tests/test_security_utils.py tests/test_auth.py` - PASS, 57 passed.

## Security And Privacy

- Model list/detail endpoints require active JWT user.
- Model registration and activation require admin role.
- Inactive user/admin tokens are rejected.
- Registration validates `weights_path` as relative, under configured model storage, existing file only.
- Absolute paths, traversal paths, outside-model-storage paths, missing files, and invalid families are rejected.
- API responses expose only stored relative `weights_path`; no resolved host/container paths, passwords, tokens, or secrets.

## Notes

- Existing stale-doc conflict remains as recorded in `.context/research.md`: `docs/index.md` and `README.md` current-state text lag actual backend implementation. Phase selection came from `docs/phase.md`.
- No source schema/migration change was needed; existing `model_versions` table and active-model partial index were used.
- No real mistake logged.
