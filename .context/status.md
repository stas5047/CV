# Phase 23 status

- Current phase: Phase 23 - Backend-worker end-to-end integration smoke.
- Mode: Code Review Resolution + Final Fix.
- Scope kept to backend/worker integration smoke coverage plus one worker path-compatibility fix found by the smoke.
- Product source-of-truth docs, research/design/plan files, and original review files were not modified in this final-fix pass.
- No frontend, training, API contract, database schema, migration, Docker service, or product behavior expansion was added.

## Review resolution

- `.context/review-code-resolution.md` updated first.
- Accepted important fix: Phase 23 smoke must use PostgreSQL, not SQLite.
- Accepted important fix: remove trailing whitespace from `docs/phase.md`.
- Rejected items: none.
- Duplicate items: none.
- Items needing user decision: none.

## Fixes applied

- `backend/tests/test_phase23_integration_smoke.py` now uses an isolated PostgreSQL schema with `search_path`, not SQLite.
- Backend and worker smoke paths share the same PostgreSQL URL and isolated shared storage.
- `docs/phase.md` trailing whitespace was removed.
- `backend/index.md` now says the Phase 23 smoke uses an isolated PostgreSQL schema.

## Existing Phase 23 implementation kept

- Automated Phase 23 smoke uses real backend registration/login/model registration/media upload/job creation/result/download routes.
- Worker `run_poll_iteration()` processes jobs through database/shared storage.
- Fake inference/tracker output only; no committed weights.
- Smoke covers image detection success, image no-detection success, video tracking/download success, missing-model failed-job behavior, and cross-owner result/download denial.
- Worker result paths canonicalize UUID-like job IDs before writing `results/{job_id}/...`; DB updates still use raw DB job IDs.

## Quality gates

- `python -m ruff check .` from `backend/` - PASS.
- `python -m pytest tests/test_phase23_integration_smoke.py -q` from `backend/` - PASS, 3 passed.
- `python -m pytest tests/test_phase23_integration_smoke.py tests/test_jobs_api.py tests/test_media_api.py tests/test_api_contract.py -q` from `backend/` - PASS, 42 passed.
- `python -m ruff check .` from `cv/` - PASS.
- `python -m pytest tests/test_startup.py tests/test_queue.py tests/test_image_processing.py tests/test_video_processing.py tests/test_storage_paths.py -q` from `cv/` - PASS, 48 passed.
- `python -m pytest -m postgres -q` from `cv/` - PASS, 3 passed, 80 deselected.
- `docker compose --env-file .env.example config` - PASS; backend and `cv-worker` share `/app/storage`, `CV_DEVICE=cpu`.
- `git diff --check -- . ':(exclude).context/review-code-claude.md' ':(exclude).context/review-code-resolution.md'` - PASS.

## Security/privacy

- Smoke checks responses/downloads for no absolute storage root, stack traces, and forbidden CV-boundary terms.
- Smoke checks cross-owner denial for job detail, summary, detections, tracks, result metadata, media download, CSV download, and JSON download.
- No secrets, tokens, passwords, raw model weights, generated media, or datasets were added.

## Index/docs

- `backend/index.md` updated for PostgreSQL-backed Phase 23 smoke coverage.
- `cv/index.md` remains updated for canonical result path ID handling from the original Phase 23 implementation.
- `docs/index.md` skipped because documentation structure and source-of-truth paths did not change.
- Mistake logs skipped; no final-state mistake or unresolved near-miss remained.

## Remaining risks

- Docker-backed real-inference E2E with actual YOLO weights was not run; automated smoke uses fake inference by contract because no valid local model artifact was confirmed.
- Test execution showed worker video tests emit an OpenCV `moov atom not found` warning for corrupted-media coverage; tests still pass.
