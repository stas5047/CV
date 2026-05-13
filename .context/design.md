# Phase 8 Design

## Phase goal

Implement backend model registry API for Phase 8 only:

- authenticated model viewing;
- admin-only model registration;
- admin-only active-model selection;
- relative model weights path validation under model storage;
- one active model at a time.

## Intended behavior from docs

Confirmed:

- All API routes are under `/api`.
- Required endpoints:
  - `GET /api/models`
  - `GET /api/models/{model_id}`
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
- Guests cannot access model endpoints.
- Authenticated users can list and view model versions.
- Regular users cannot register or activate models.
- Admins can register and activate model versions.
- Model family must be `YOLO26` or documented fallback `YOLO11`.
- First implementation registers existing relative weights paths under model storage.
- Large `.pt` upload through web UI/API is not required.
- `weights_path` must be relative; absolute paths and traversal paths are invalid.
- Only one model version may be active at once.
- Model registry must represent actual model family used.
- Training must not be launched from API or UI.

Assumptions:

- Responses expose model metadata from documented `model_versions` fields, with no absolute filesystem paths.
- `weights_path` wire/database values are canonical relative-to-`STORAGE_ROOT` paths with the `models/.../weights.pt` prefix.
- The service resolves `weights_path` against `STORAGE_ROOT`, then verifies the resolved file is inside configured `MODELS_ROOT`.
- Registration verifies weights path exists under configured model storage.
- Activation uses existing `model_versions.is_active` state; no new table or migration expected.
- Existing `metrics_json` stores key metrics and placeholder/null metric values if needed.
- For `YOLO11`, Phase 8 stores/reports the actual `model_family` and preserves supplied fallback documentation metadata, but does not invent a new required metadata field absent from product docs.

## Architecture decisions

- Keep route handlers thin and put model registry rules in a service module.
- Reuse existing auth dependencies:
  - `get_current_active_user` for list/detail.
  - `get_current_admin_user` for create/activate.
- Reuse existing storage path utility for relative path validation and safe path resolution.
- Do not add file upload for weights.
- Do not add training launch behavior.
- Do not add CV worker behavior.
- Do not modify database schema unless implementation discovers existing migration/model mismatch.
- For activation, update current active model to inactive and requested model to active in one database transaction. Rely on existing unique partial index as final guard.
- On missing models, return safe not-found error without exposing whether hidden admin state exists.

## Backend impact

Touched:

- Add model registry router under existing `/api` router.
- Add Pydantic request/response schemas for model registry.
- Add model service functions for list, get, create, activate, and path validation.
- Add backend tests for access control, validation, and active-model behavior.

Not touched:

- Jobs API.
- Results/download API.
- Experiments API.
- CV worker.
- Training utilities.
- Frontend.

## API impact

Implemented endpoints only:

- `GET /api/models`
- `GET /api/models/{model_id}`
- `POST /api/models`
- `PATCH /api/models/{model_id}/activate`

Access behavior:

- Guest: 401 on all model endpoints.
- Authenticated user: can list/view; 403 on create/activate.
- Admin: can list/view/create/activate.

Validation behavior:

- Reject invalid `model_family`.
- Reject absolute, empty, or traversal `weights_path`.
- Reject paths outside configured model storage.
- Reject missing/non-file weights path.
- Accept canonical positive paths such as `models/yolo26s-seraphim-subset-v1/weights.pt`.
- Preserve exactly one active model.

## Database impact

- Use existing `model_versions` table and `ModelVersion` ORM class.
- Use existing `model_family` check constraint.
- Use existing `weights_path` relative-path check.
- Use existing unique active-model partial index.
- No new schema fields planned.
- No Alembic migration planned unless a verified mismatch blocks Phase 8 behavior.

## Frontend impact

- No frontend source changes in this phase.
- Future frontend can consume model list/detail endpoints after backend is complete.

## Security/privacy impact

Touched:

- Protected endpoints require valid JWT and active user.
- Admin-only mutations require admin role.
- Model path validation must prevent absolute path exposure and traversal.
- API responses must not expose host/container absolute paths.
- No secrets, tokens, DB passwords, or admin password in logs/errors.

Not touched:

- Upload validation.
- Ownership for user media/jobs.
- Downloads.
- CORS behavior, except existing auth-protected API behavior continues.

## Test strategy

Relevant automated checks:

- `python -m ruff check .` from `backend/`.
- `python -m pytest tests/test_models_api.py` from `backend/`.
- `python -m pytest tests/test_data_model.py tests/test_security_utils.py tests/test_auth.py` from `backend/`.

Required test cases:

- Authenticated users can list models.
- Authenticated users can fetch one model.
- Guests receive 401 for model endpoints.
- Inactive authenticated users receive 401 or 403 for at least `GET /api/models`.
- Inactive admin users receive 401 or 403 for at least one model mutation when fixture setup is practical.
- Regular users receive 403 for registration and activation.
- Admin can register model with existing relative path under model storage.
- Admin can activate exactly one model.
- Activating second model deactivates first.
- `YOLO26` and documented fallback `YOLO11` metadata are accepted.
- `YOLO11` responses preserve `model_family = YOLO11` and supplied fallback documentation metadata.
- Invalid model family rejected.
- Absolute path rejected.
- Traversal path rejected.
- Path outside model storage rejected.
- Missing weights file rejected.
- Canonical `models/.../weights.pt` path form succeeds when the file exists under `MODELS_ROOT`.
- Responses never include absolute filesystem paths.

Skipped as out of scope:

- Frontend build/tests.
- CV worker tests.
- Docker Compose smoke.
- Experiment import tests.
- Job/model selection worker priority tests beyond ensuring active model API state.

## Ambiguities or conflicts

- WARNING: CONFLICT
  - `docs/index.md` and `README.md` current-state sections are stale relative to actual backend implementation and `backend/index.md`.
  - Contract uses `docs/phase.md` for phase selection and actual backend files for implementation-state facts.
- Resolved planning-review item: Phase 8 canonical `weights_path` form is `models/.../weights.pt`, relative to `STORAGE_ROOT`, with a service check that the resolved file is inside `MODELS_ROOT`.
- Ambiguity: exact response schema is not specified in API docs. Implementation should mirror documented `model_versions` metadata and existing Pydantic style.
