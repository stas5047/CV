# OpenAI Code Review - Phase 1

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 1 scaffold mostly matches docs: required services exist, backend/worker share `/app/storage`, GPU override targets only `cv-worker`, storage helper exists, and placeholders avoid product logic.

One important docs/setup defect remains: README tells user to create real `.env`, then launch with `.env.example`, so updated secrets are ignored.

## Critical issues

None.

## Important issues

1. README launch flow ignores user-edited `.env` and starts with placeholder secrets.
   - Evidence: README step says copy `.env.example` to `.env` and replace placeholder secrets before real use (`README.md:27`-`README.md:28`).
   - Evidence: start command still uses `docker compose --env-file .env.example up --build` (`README.md:41`-`README.md:44`) and command table repeats that (`README.md:75`-`README.md:76`).
   - Evidence: docs require safe placeholders in `.env.example` and one-command local/demo launch after setup (`docs/phase.md:10`, `docs/phase.md:15`; `docs/AUTH_SECURITY.md:307`-`docs/AUTH_SECURITY.md:318`).
   - Impact: user following README can edit `.env` but still run Compose with placeholder DB/admin/JWT values from `.env.example`. This makes setup docs inaccurate and weakens secret-handling expectations.
   - Required change: keep `.env.example` for validation examples, but make real launch use `.env` or omit `--env-file` after copy.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for inspection. Shows Phase 1 scaffold plus context/doc updates; `rtk` also prints no-hook warning.
- `rtk git diff --stat`: PASS for inspection, but only tracked diffs; untracked scaffold files required separate read.
- `rtk git diff`: PASS for inspection, but only tracked diffs; untracked scaffold files required separate read.
- `docker compose --env-file .env.example config`: PASS, rerun during review.
- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config`: PASS, rerun during review. Rendered GPU reservation only under `cv-worker`.
- Storage directory presence check: PASS. Required folders exist.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1`: PASS per `.context/status.md`; not rerun during review because directory check was enough.
- `docker compose --env-file .env.example build`: FAIL per `.context/status.md:38`; Docker Desktop daemon unavailable. Not source evidence, but build/start smoke remains unverified.
- Backend tests: not available yet.
- CV worker tests: not available yet.
- Frontend tests/build: not available yet.

## Security/privacy assessment

Applicable because Phase 1 touches env and runtime setup.

- `.env.example` contains placeholder secrets only (`change-me-*`), no real credentials found.
- `.gitignore` excludes `.env`, generated storage contents, model weights, media, Python caches, and Node artifacts.
- Compose adds no unsupported Redis/Celery/Flask/Streamlit/RTSP/live-camera services.
- Main security/privacy concern is README command drift: real `.env` edits are bypassed by launch command using `.env.example`.

## Positive findings

- `docker-compose.yml` defines only documented runtime services: `postgres`, `backend`, `cv-worker`, `frontend`.
- Backend and CV worker both mount `./storage` at `/app/storage`.
- GPU override is isolated to `cv-worker` and sets `CV_DEVICE=cuda`.
- Placeholder Dockerfiles are build-oriented only and do not add API routes, UI, worker queue logic, CV inference, auth, migrations, or training.
- README honestly marks product features and tests as not available yet.
- Component index files correctly describe placeholder state.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `.env.example`
- `.gitignore`
- `docker-compose.yml`
- `docker-compose.gpu.yml`
- `Makefile`
- `README.md`
- `scripts/bootstrap-storage.ps1`
- `backend/Dockerfile`
- `cv/Dockerfile`
- `frontend/Dockerfile`
- `backend/index.md`
- `cv/index.md`
- `frontend/index.md`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
