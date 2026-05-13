# Phase Research

## Current phase

- Phase: Phase 6 - Authorization, ownership, CORS, path safety, and security utilities.
- Direction: Backend / Security.
- Risk: user supplied placeholder only; assumed HIGH because phase touches authorization, ownership, CORS, path traversal, logging safety, and protected-route behavior.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

No other product docs were consulted for product requirements.

## Confirmed repository facts

- `docs/phase.md` and `docs/ROADMAP.md` both identify Phase 6 as current target.
- Phase 6 relevant docs are exactly `AUTH_SECURITY.md`, `API.md`, `ARCHITECTURE.md`, and `TESTING_QA.md`.
- Git checkout exists. `git status --short` shows modified `.context/*` files and `docs/phase.md` before this contract write.
- Repository contains `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, root Compose/env/README files, and backend scaffold.
- Backend has FastAPI app under `backend/app/`.
- Backend routes are mounted under `/api` through `backend/app/api/router.py`.
- Existing backend auth endpoints live in `backend/app/api/auth.py`.
- Existing auth primitives live in `backend/app/core/auth.py`.
- Existing CORS setup lives in `backend/app/core/cors.py` and settings validation in `backend/app/core/config.py`.
- Existing logging redaction lives in `backend/app/core/logging.py`.
- Existing SQLAlchemy models include `users`, `media_files`, `processing_jobs`, `detections`, `tracks`, `model_versions`, `experiment_runs`, and `experiment_metrics`.
- Existing DB models already include relative path check constraints for stored media/result/model/report paths.
- Backend tests already cover settings, logging redaction, health, data model constraints, setup/seed, and Phase 5 auth.
- `frontend/` and `cv/` still contain placeholder Dockerfile/index files only.
- `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/status.md`, and review-resolution files were empty when read.

## Existing implementation state

- Implemented:
  - FastAPI app factory.
  - `/api/health` and `/api/health/db`.
  - typed settings with required auth/storage/CORS variables.
  - explicit CORS origin parsing and wildcard rejection.
  - secret-aware settings repr and logging redaction filter.
  - SQLAlchemy data model and initial migration.
  - storage bootstrap and seeded admin setup.
  - bcrypt password hashing.
  - JWT creation/validation.
  - public registration, login, and `/api/auth/me`.
  - active-user enforcement for `/api/auth/me`.
- Not yet confirmed/implemented for Phase 6:
  - reusable admin-only dependency.
  - reusable ownership-check helper for user-owned resources.
  - reusable path safety utilities for safe join under `STORAGE_ROOT`, relative path validation, path traversal prevention, and safe download names.
  - upload filename sanitization helper.
  - Phase 6-specific tests for admin dependency, ownership helper, path traversal utilities, absolute-path rejection at service boundary, CORS validation, and no-secret logs beyond existing baseline.
  - explicit secure error response pattern beyond current FastAPI defaults and existing auth errors.

## Unknowns and assumptions

- Unknown: exact desired internal filenames for new utility modules. Docs specify behavior, not module names.
- Assumption: implementation may add narrow backend helper modules under existing `backend/app/core/` or `backend/app/api/` structure if existing files would become mixed-responsibility.
- Unknown: whether current backend test suite passes now; planning mode did not run gates.
- Assumption: Phase 6 should not add product endpoints. Existing `/api/auth/me` can verify protected-route behavior.
- Assumption: admin-only dependency can be tested directly or through an app-local test route without adding public product API surface.
- Assumption: ownership helper should operate on existing model ownership fields and be reusable for later media/job/result APIs.
- Unknown: exact production-vs-local environment flag for CORS. Current docs require explicit configured origins and forbid wildcard in non-local configs; current implementation rejects wildcard everywhere, which is stricter and doc-consistent.

## Files likely relevant for implementation

- `backend/app/core/auth.py`
- `backend/app/api/deps.py`
- `backend/app/core/cors.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/main.py`
- `backend/app/db/models.py`
- `backend/tests/conftest.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_settings.py`
- `backend/tests/test_logging.py`
- New narrow backend security/path/ownership tests may be needed under `backend/tests/`.
- New narrow backend helper modules may be needed under existing backend package boundaries if current files would mix responsibilities.

## Conflicts

- No `WARNING: CONFLICT` found between consulted phase docs, `docs/phase.md`, and current implementation facts.
