# OpenAI Code Review - Phase 14

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 14 scaffold mostly matches scope: worker package exists, settings/logging/device/database/storage helpers are narrow, Dockerfile now runs worker entrypoint, and tests cover main scaffold behavior.

One real defect: startup retry wrapper turns CUDA configuration failure into database-unavailable failure. This breaks documented `CV_DEVICE=cuda` fail-clear behavior and can waste 30 seconds before surfacing wrong top-level error.

## Critical issues

None.

## Important issues

1. `CV_DEVICE=cuda` unavailable path is misreported as database startup failure.
   - Evidence: `docs/CV_PIPELINE.md:166-168` defines `cuda` as force CUDA, and `docs/CV_PIPELINE.md:367-368` requires CUDA unavailable with `CV_DEVICE=cuda` to fail clearly.
   - Plan evidence: `.context/plan.md:37-38` requires `auto` CPU fallback and `cuda` unavailable clear failure; `.context/plan.md:86-88` requires tests for these cases plus DB retry behavior.
   - Code evidence: `cv/aerovision_worker/main.py:37-40` wraps all startup checks in `wait_for_database`; `cv/aerovision_worker/database.py:39-43` catches every `Exception` and raises `RuntimeError("database unavailable after ... attempts")`.
   - Repro evidence: direct startup-check wrapper with `cv_device="cuda"` and mocked CUDA unavailable returns top-level `RuntimeError database unavailable after 2 attempts`; original cause is `DeviceUnavailableError CUDA requested but unavailable`.
   - Impact: CPU-only host with GPU override gets wrong operator signal and delayed failure. This violates product docs and accepted planning resolution.
   - Required change: keep DB retry around DB connectivity only, or make retry catch only database/SQLAlchemy connectivity failures. Let `DeviceUnavailableError` fail immediately with CUDA-specific message. Add startup-level regression test, not only `select_device()` unit test.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS inspection. Changed Phase 14 context/docs plus `README.md`, `cv/Dockerfile`, `cv/index.md`; new `cv/aerovision_worker/`, `cv/pyproject.toml`, `cv/tests/`.
- `rtk git diff --stat`: PASS inspection.
- `rtk git diff` content: PASS inspection for implementation files and allowed context/docs. Forbidden review-resolution content not read.
- `docker compose --env-file .env.example config`: PASS.
- `python -m pytest` from `cv/`: PASS, 30 passed.
- `python -m ruff check .` from `cv/`: PASS.
- `python -m aerovision_worker.main --check-once` from `cv/` with `DATABASE_URL=sqlite+pysqlite:///:memory:` and `CV_DEVICE=cpu`: PASS smoke for import/settings/device/DB helper path, but not PostgreSQL connectivity.
- `docker compose --env-file .env.example build cv-worker`: FAIL, Docker daemon unavailable: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`.
- Full Phase 14 Docker/PostgreSQL startup smoke: not verified because Docker daemon unavailable.

## Security/privacy assessment

No blocking security issue found in touched worker scaffold. Logging redacts database URLs, token-like strings, secret words, and absolute paths; tests cover redaction. Storage resolver rejects absolute paths, traversal, UNC-like paths, empty paths, and NUL bytes. No backend HTTP job-loop calls, new services, Celery, Redis, Flask, Streamlit, GUI OpenCV calls, or inference/tracking/export scope creep found.

## Positive findings

- Worker remains separate from backend API and uses SQLAlchemy database access only.
- `CV_DEVICE=auto` and direct `CV_DEVICE=cuda` helper behavior are unit-tested.
- Path safety helper normalizes safe relative paths and keeps resolved paths under root.
- Docker GPU override remains isolated to `cv-worker`.
- Phase 14 stays out of queue claiming, inference, tracking, exports, schema changes, and frontend work.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `README.md`
- `.env.example`
- `docker-compose.yml`
- `docker-compose.gpu.yml`
- `Makefile`
- `cv/Dockerfile`
- `cv/index.md`
- `cv/pyproject.toml`
- `cv/aerovision_worker/__init__.py`
- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/logging.py`
- `cv/aerovision_worker/device.py`
- `cv/aerovision_worker/database.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/main.py`
- `cv/tests/test_settings.py`
- `cv/tests/test_logging.py`
- `cv/tests/test_device.py`
- `cv/tests/test_database.py`
- `cv/tests/test_storage_paths.py`
- `cv/tests/test_startup.py`
