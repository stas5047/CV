# Phase 7 Status - Media Upload API and Metadata Extraction

## Implementation

- Phase implemented: `Phase 7 - Media upload API and metadata extraction`.
- Scope kept to backend media API, upload validation, generated relative storage paths, metadata extraction, ownership/admin visibility, soft deletion, tests, and backend index update.
- Later phases not implemented: jobs, results/downloads, model APIs, experiments, admin APIs, frontend, CV worker.

## Files Changed By Codex

- `backend/pyproject.toml`
- `backend/app/api/router.py`
- `backend/app/api/media.py`
- `backend/app/schemas/media.py`
- `backend/app/services/media.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_media_validation.py`
- `backend/index.md`
- `.context/status.md`

## Quality Gates

- `cd backend; python -m pytest tests/test_media_api.py tests/test_media_validation.py` - PASS
- `cd backend; python -m pytest tests/test_auth.py tests/test_security_utils.py` - PASS
- `cd backend; python -m pytest` - PASS, 94 passed.
- `cd backend; python -m ruff check .` - PASS
- `docker compose config` - PASS, with existing unset environment variable warnings when no env file is supplied.

## Security And Privacy

- Media endpoints require active JWT user.
- Regular users see/delete only own non-deleted media.
- Admins can list/read/delete all non-deleted media metadata.
- Uploads validate extension, MIME, size, filename, and decoded image/video content.
- Stored paths are generated under `uploads/{user_id}/{media_id}/original.{ext}` and validated as relative.
- API media responses omit `stored_path`, absolute paths, storage root, tokens, passwords, and secrets.
- Video uploads now reject mismatched container headers such as AVI bytes submitted as `.mp4` with `video/mp4`.
- Soft delete sets `deleted_at`; physical file removal remains out of Phase 7.

## Notes

- Installed local test dependencies with `python -m pip install python-multipart pillow opencv-python-headless` to run upload/media tests in this environment.
- Code review resolution accepted and fixed one important OpenAI review item: video extension/MIME/content mismatch acceptance.
- No source-of-truth conflict found.
- No real mistake logged.
