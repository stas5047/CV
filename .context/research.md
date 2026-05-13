# Phase 8 Research

## Current phase

- Confirmed from `docs/phase.md`: Phase 8 - Model registry backend API.
- Direction: Backend / Admin.
- Goal: implement model registry records, active model management, and model path validation.
- Risk level: not supplied by user prompt. Assumption: MEDIUM, because phase touches authenticated backend API, admin-only mutations, model-path safety, and active-model state.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- `git status --short` showed existing modified files before this contract work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Root has `backend/`, `frontend/`, `cv/`, `training/`, `docs/`, `docker-compose.yml`, `docker-compose.gpu.yml`, `.env.example`, `Makefile`, and `scripts/bootstrap-storage.ps1`.
- Backend exists as FastAPI app, not placeholder-only.
- Backend dependencies include FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, psycopg, python-jose, passlib/bcrypt, Pillow, OpenCV headless, pytest, and Ruff.
- Backend router currently includes auth, health, and media routers only.
- `backend/app/db/models.py` already defines `ModelVersion` with documented fields:
  - `id`
  - `name`
  - `model_family`
  - `variant`
  - `weights_path`
  - `dataset_name`
  - `dataset_split_description`
  - `metrics_json`
  - `is_active`
  - `created_by_user_id`
  - `created_at`
  - `updated_at`
- `ModelVersion` already has a database check for `model_family IN ('YOLO26', 'YOLO11')`.
- `ModelVersion.weights_path` already has relative-path check constraint.
- `model_versions` already has unique active-model partial index `uq_model_versions_active_true`.
- `Settings` already exposes `storage_root` and `models_root`.
- `storage_paths.py` already provides:
  - `validate_relative_storage_path`
  - `safe_join_storage_path`
  - filename helpers
- `authorization.py` already provides active-user auth dependency through `get_current_active_user` and admin dependency `get_current_admin_user`.
- Existing tests cover schema constraints, auth, security utilities, settings, setup, health, media validation, and media API.

## Existing implementation state

- Implemented:
  - FastAPI app factory and `/api` router.
  - Health API.
  - JWT auth, public registration, login, current-user endpoint.
  - Active-user enforcement.
  - Admin dependency.
  - Ownership helpers.
  - Storage relative-path validation and safe join.
  - Media upload/list/detail/soft-delete API.
  - SQLAlchemy schema and initial Alembic migration for documented tables.
  - Storage setup and seeded admin command.
- Not implemented in current backend:
  - `GET /api/models`
  - `GET /api/models/{model_id}`
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
  - Model API schemas.
  - Model API service/domain module.
  - Model API tests.
- CV worker, frontend model page, jobs/results APIs, and experiment APIs are outside this phase.

## Unknowns and assumptions

- WARNING: CONFLICT
  - `docs/index.md` says `backend/`, `frontend/`, and `cv/` contain placeholder Dockerfiles only and no product app scaffold/routes/tests.
  - `README.md` says auth/uploads are not available yet and current state is Phase 4.
  - Actual repo and `backend/index.md` show backend auth, security, media API, schema, migrations, and tests exist.
  - `docs/phase.md` identifies Phase 8. Contract assumes `docs/phase.md` is current phase source and uses actual backend state for implementation planning.
- User prompt left phase title and risk placeholders unfilled. Assumption: current phase from `docs/phase.md`; risk MEDIUM.
- Planning review resolution chose the Phase 8 canonical `weights_path` wire/database form as relative to `STORAGE_ROOT` with the `models/.../weights.pt` prefix.
  - Implementation should resolve the stored value against `STORAGE_ROOT`, then require the resolved file to live under configured `MODELS_ROOT`.
  - Positive tests should use the exact canonical form, for example `models/yolo26s-seraphim-subset-v1/weights.pt`.
  - Paths outside `MODELS_ROOT`, absolute paths, traversal paths, empty paths, and missing files must be rejected.
- Docs do not define exact model request/response JSON field names beyond `model_versions` documented fields.
  - Assumption: Pydantic schemas mirror documented `model_versions` metadata and existing backend naming style.
- Docs say admin registers existing weights paths. Assumption: creation should verify the resolved weights file exists and is a file; no `.pt` upload is implemented.
- Docs allow YOLO11 only as documented fallback. Phase 8 does not define a required fallback-documentation field, so implementation should not invent a new mandatory field. It must store/report `model_family = YOLO11` accurately and preserve supplied fallback documentation metadata, for example in `metrics_json`, without treating YOLO11 as an alternative primary model.
- No model size field exists in `model_versions`; model size may live in `metrics_json` or later summary data. Do not add schema fields in this phase.

## Files likely relevant for implementation

- Existing:
  - `backend/app/api/router.py`
  - `backend/app/api/deps.py`
  - `backend/app/core/authorization.py`
  - `backend/app/core/config.py`
  - `backend/app/core/storage_paths.py`
  - `backend/app/db/models.py`
  - `backend/tests/conftest.py`
  - `backend/tests/test_data_model.py`
  - `backend/tests/test_security_utils.py`
  - `backend/pyproject.toml`
- Likely new backend modules following existing resource pattern:
  - `backend/app/api/models.py`
  - `backend/app/schemas/models.py`
  - `backend/app/services/models.py`
  - `backend/tests/test_models_api.py`
