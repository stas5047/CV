# Phase 22 Research

## Current phase

- Confirmed: `docs/phase.md` identifies current phase as `Phase 22 - Model artifact registration and experiment artifact import utilities`.
- Confirmed direction: Backend / Training Integration.
- Confirmed goal: bridge offline training artifacts into backend model registry and experiment import flows.
- Assumption: user prompt left risk placeholder unresolved; treat phase risk as `MEDIUM` because implementation will add admin-facing artifact import helpers, path validation, and database/API writes.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before writing showed modified `.context/*` files and modified `docs/phase.md`.
- Existing `.context/research.md`, `.context/design.md`, and `.context/plan.md` were 0 bytes before this write.
- Root contains `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `scripts/`, Compose files, Makefile, README, `AGENTS.md`, and `CLAUDE.md`.
- Backend package exists with FastAPI API modules, services, schemas, SQLAlchemy models, Alembic migration, setup command, and tests.
- Training package exists with dataset split, notebook checks, artifact schemas, artifact validator CLI, templates, README, and tests.
- Frontend still contains placeholder Dockerfile only; no Phase 22 frontend implementation needed.
- CV worker exists beyond scaffold, but Phase 22 does not require worker changes.

## Existing implementation state

- Backend model registry API already exists:
  - `GET /api/models`
  - `GET /api/models/{model_id}`
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
- Backend experiment API already exists:
  - `GET /api/experiments`
  - `GET /api/experiments/{experiment_id}`
  - `POST /api/experiments/import`
- Existing backend services validate relative model weights paths under `models/` and experiment artifact paths under `reports/`.
- Existing backend services reject absolute paths and storage-root leakage in API responses.
- Existing backend enforces admin-only model registration, model activation, and experiment import.
- Existing database model already includes `model_versions`, `experiment_runs`, and `experiment_metrics`.
- Existing training validator validates model cards and metrics artifacts but only reports import readiness; it does not register models or import experiments into backend.
- Existing `training/templates/model_card.placeholder.json` supports nullable metrics.
- Existing `training/templates/metrics.placeholder.json` covers four documented experiment families with nullable metrics.

## WARNING: CONFLICT

- `docs/DATA_MODEL.md` and `docs/API.md` use experiment type identifiers:
  - `model_comparison`
  - `threshold_analysis`
  - `tracker_comparison`
  - `false_positive_analysis`
- Existing `training/aerovision_training/schemas.py` and `training/templates/metrics.placeholder.json` use:
  - `model_comparison`
  - `confidence_threshold_analysis`
  - `tracker_behavior_comparison`
  - `false_positive_analysis`
- Impact: current training metrics artifact cannot be posted directly to existing backend experiment import API without a documented mapping or source alignment.

## Unknowns and assumptions

- Unknown: whether Phase 22 helper must be a backend-local database CLI, a training-local API client CLI, or both.
- Assumption: prefer training-local API client helper because backend REST API already owns authorization and validation for model registration and experiment import.
- Unknown: whether idempotent imports are required. Docs say test idempotency only when supported; existing schema/API do not document uniqueness keys for idempotent imports.
- Assumption: do not add idempotency unless user approves unique-key behavior or docs change.
- Unknown: exact admin credential/token workflow for helper.
- Assumption: helper should prefer an existing admin JWT token from environment or argument and avoid logging tokens/passwords.
- Unknown: whether README root or `training/README.md` should hold workflow docs.
- Assumption: update `training/README.md` for detailed artifact workflow; update root `README.md` only if new user-facing commands are added.

## Planning review resolution notes

- Accepted: implementation must make training schema/templates and backend-facing experiment payloads use documented canonical slugs: `model_comparison`, `threshold_analysis`, `tracker_comparison`, `false_positive_analysis`.
- Rejected for Phase 22: compatibility aliases for current legacy slugs `confidence_threshold_analysis` and `tracker_behavior_comparison`. Add aliases only after explicit user approval.
- Accepted: helper validation must reject absolute paths, traversal, and local/cloud path leaks in path-like metadata fields inside model cards and metrics artifacts, not only top-level `weights_path` and `artifacts_path`.
- Accepted: targeted backend API gates for model registration, activation, experiment import, and API contract must run even when backend source code is unchanged.
- Accepted: add mocked CLI smoke coverage for placeholder model card and metrics template payload shape, route/method, authorization header handling, and redacted output.
- Accepted: implementation docs must state helper registers existing files under storage and never uploads `.pt` weights or starts training.

## Files likely relevant for implementation

- `training/aerovision_training/schemas.py`
- `training/aerovision_training/validate_artifacts.py`
- `training/templates/model_card.placeholder.json`
- `training/templates/metrics.placeholder.json`
- `training/tests/test_schemas.py`
- `training/README.md`
- `training/index.md`
- `training/pyproject.toml`
- `backend/app/api/models.py`
- `backend/app/api/experiments.py`
- `backend/app/services/models.py`
- `backend/app/services/experiments.py`
- `backend/app/schemas/models.py`
- `backend/app/schemas/experiments.py`
- `backend/tests/test_models_api.py`
- `backend/tests/test_experiments_api.py`
- `backend/tests/test_api_contract.py`
- `README.md`
