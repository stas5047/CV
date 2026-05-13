# Research - Phase 12 Experiment Import Backend API

## Current phase

- Confirmed: `docs/phase.md` identifies **Phase 12 - Experiment import backend API**.
- Confirmed direction: Backend / Admin / Experiments.
- Confirmed goal: implement imported experiment records and metrics without launching training from the app.
- Assumption: risk level is **MEDIUM**. User prompt left risk as placeholder; phase touches admin-only API, published visibility, null metric handling, and path safety, but not runtime CV processing or frontend UI.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/FRONTEND_UX.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before writing showed existing modified files:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- `.context/research.md`, `.context/design.md`, and `.context/plan.md` existed and were empty before this contract write.
- `backend/index.md` states experiment product APIs do not exist yet.
- `rg --files` confirms backend app, migrations, and tests exist; frontend and CV worker are still placeholder Dockerfile/index areas.
- Existing backend commands are documented in `backend/index.md`:
  - `python -m pip install -e ".[dev]"`
  - `python -m ruff check .`
  - `python -m pytest`
  - `alembic upgrade head`

## WARNING: CONFLICT

- `docs/index.md` current implementation state says the repository has Phase 1 scaffold only and `backend/`, `frontend/`, and `cv/` contain buildable placeholder Dockerfiles only.
- Repository facts and `backend/index.md` show backend implementation exists through auth, media, model, job/result/download, and admin API surfaces.
- Phase 12 product behavior docs still align on experiment API scope. Use product docs for behavior and current repository files for existing implementation state.

## Existing implementation state

- Existing SQLAlchemy models include `ExperimentRun` and `ExperimentMetric` in `backend/app/db/models.py`.
- Existing migration includes `experiment_runs` and `experiment_metrics`.
- Existing data-model tests cover experiment tables, allowed experiment types, null `metric_value`, and rejection of `tracking_accuracy`.
- Existing admin stats count total and published experiment runs.
- Existing storage cleanup protects `ExperimentRun.artifacts_path`.
- Existing API router includes auth, health, media, models, jobs, and admin routers only. No experiments router is registered.
- No `backend/app/api/experiments.py`, `backend/app/services/experiments.py`, `backend/app/schemas/experiments.py`, or `backend/tests/test_experiments_api.py` exists.
- Existing security helpers provide:
  - `get_current_active_user`
  - `get_current_admin_user`
  - `validate_relative_storage_path`
  - `safe_join_storage_path`
- Existing model API pattern uses thin route handlers, service functions, Pydantic schemas, pagination, role dependencies, and safe relative storage path validation.

## Unknowns and assumptions

- Unknown: exact experiment import request/response JSON shape is not fully specified in product docs.
- Assumption: implementation request schemas should expose only documented `experiment_runs` fields and child `experiment_metrics` fields, with no new product concepts.
- Unknown: whether imported artifact path must be a file or may be a directory. Docs say artifact paths from existing files under storage, while data model and cleanup allow `artifacts_path` as a protected file or directory prefix.
- Assumption: accept safe relative `artifacts_path` under `reports/` and require the resolved path to exist as file or directory under `STORAGE_ROOT`; reject absolute, traversal, missing, or outside paths.
- Unknown: exact pagination/filter response names for experiments. Existing backend list APIs use `items`, `total`, `limit`, and `offset`.
- Assumption: experiments list follows existing backend pagination pattern and documented filters: experiment type and published status for admins.
- Unknown: whether regular users should see metric rows on detail for published runs. API says users can view published experiment runs; training docs say frontend displays imported metrics. Assumption: detail for published run includes metrics.
- Unknown: whether model version reference must point to existing row. Data model has FK; service should return safe 400/404 instead of raw DB error.

## Files likely relevant for implementation

- `backend/app/api/router.py`
- `backend/app/api/experiments.py`
- `backend/app/services/experiments.py`
- `backend/app/schemas/experiments.py`
- `backend/app/db/models.py`
- `backend/app/core/storage_paths.py`
- `backend/app/core/authorization.py`
- `backend/app/core/config.py`
- `backend/tests/test_experiments_api.py`
- `backend/tests/test_admin_api.py`
- `backend/tests/test_data_model.py`
- `backend/index.md`
