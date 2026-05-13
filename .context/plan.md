# Phase 8 Implementation Plan

## Scope

Phase only: Phase 8 - Model registry backend API.

Do not implement:

- jobs API;
- results API;
- experiment API;
- frontend model page;
- CV worker model loading;
- training utilities;
- model weight upload;
- schema fields not documented in `model_versions`.

## Ordered atomic plan

1. [@role/developer-backend] Re-read Phase 8 docs before coding.
   - Verify `docs/phase.md` still says Phase 8.
   - Verify relevant docs remain: `docs/API.md`, `docs/DATA_MODEL.md`, `docs/CV_PIPELINE.md`, `docs/TRAINING_EXPERIMENTS.md`, `docs/AUTH_SECURITY.md`, `docs/TESTING_QA.md`.
   - Verifiable: note no source change made in this step.

2. [@role/developer-backend] Inspect current backend router/schema/service patterns.
   - Read `backend/app/api/media.py`, `backend/app/schemas/media.py`, `backend/app/services/media.py`, and auth/security helpers.
   - Verifiable: identify exact existing dependency and response-model patterns before editing.

3. [@role/developer-backend] Add model registry schemas.
   - Create schema module matching existing backend schema style.
   - Include documented `model_versions` metadata only.
   - Add create payload validation for `model_family`, `variant`, `weights_path`, and metadata fields.
   - Do not add a new required YOLO11 fallback-documentation field absent from product docs.
   - Preserve supplied fallback documentation metadata for YOLO11 registrations in documented metadata fields.
   - Ensure response schema cannot expose absolute host/container paths.
   - Verifiable: schema unit/API tests can validate accepted and rejected payloads.

4. [@role/developer-backend] Add model registry service logic.
   - Implement list models with pagination and optional documented filters where already practical: active status, model family, variant.
   - Implement get model by UUID.
   - Implement admin create model.
   - Implement admin activate model.
   - Keep SQLAlchemy work in service layer, not route handlers.
   - Verifiable: service behavior covered through API tests.

5. [@role/developer-auth-security] Implement model path validation inside service logic.
   - Validate `weights_path` is non-empty relative path.
   - Use `models/.../weights.pt` as the canonical API/database path form, relative to `STORAGE_ROOT`.
   - Reject absolute Windows/POSIX paths.
   - Reject traversal segments.
   - Resolve path under `STORAGE_ROOT` and require the resolved file to be inside configured `MODELS_ROOT`.
   - Verify path exists and is a file.
   - Store only relative path, never resolved absolute path.
   - Verifiable: tests accept an existing canonical `models/.../weights.pt` file and reject absolute, traversal, outside-model-root, and missing-file inputs.

6. [@role/developer-auth-security] Enforce endpoint access control.
   - Use active-user dependency for `GET /api/models`.
   - Use active-user dependency for `GET /api/models/{model_id}`.
   - Use admin dependency for `POST /api/models`.
   - Use admin dependency for `PATCH /api/models/{model_id}/activate`.
   - Verifiable: guest gets 401; regular user gets 403 for admin mutations.

7. [@role/developer-db] Implement active-model transition without schema change.
   - Use existing `model_versions.is_active`.
   - Deactivate current active model and activate requested model in one transaction.
   - Let existing unique partial index enforce final one-active invariant.
   - Verifiable: activating second model leaves exactly one active model.

8. [@role/developer-backend] Add model API router and register it.
   - Add model router under `/models`.
   - Include router in `backend/app/api/router.py`.
   - Keep endpoint paths exactly documented:
     - `GET /api/models`
     - `GET /api/models/{model_id}`
     - `POST /api/models`
     - `PATCH /api/models/{model_id}/activate`
   - Verifiable: route tests hit exact paths.

9. [@role/tester] Add backend API tests for Phase 8.
   - Create model API tests covering:
     - authenticated list/detail success;
     - guest rejection;
     - inactive authenticated user rejection on `GET /api/models`;
     - inactive admin rejection on one model mutation when practical;
     - regular-user create/activate rejection;
     - admin create success with existing model file;
     - admin activate success;
     - one-active-model invariant;
     - YOLO26 accepted;
     - YOLO11 stores/reports `model_family = YOLO11` and preserves supplied fallback documentation metadata;
     - invalid family rejected;
     - canonical `models/.../weights.pt` path accepted when file exists under `MODELS_ROOT`;
     - unsafe path rejected;
     - path outside `MODELS_ROOT` rejected;
     - missing weights file rejected;
     - no absolute path in response body.
   - Verifiable: targeted test file fails before implementation and passes after implementation.

10. [@role/tester] Run relevant backend quality gates.
    - From `backend/`: `python -m ruff check .`
    - From `backend/`: `python -m pytest tests/test_models_api.py`
    - From `backend/`: `python -m pytest tests/test_data_model.py tests/test_security_utils.py tests/test_auth.py`
    - Verifiable: each command reports PASS, or blocker records exact failure.

11. [@role/code-reviewer] Review Phase 8 diff against docs.
    - Check endpoint paths and access matrix.
    - Check admin-only mutations.
    - Check no model weight upload was added.
    - Check no training launch behavior was added.
    - Check no frontend, worker, jobs, results, or experiments scope leaked in.
    - Check no absolute paths in database/API responses.
    - Verifiable: review notes no blocking doc mismatch, or blocker cites exact file/doc rule.

12. [@role/docs-maintainer] Update docs only if implementation changes documented commands or file indexes.
    - If new backend files or commands alter `backend/index.md`, update that index only.
    - Do not update product docs for Phase 8 behavior unless user explicitly requests.
    - Do not touch `docs/index.md`, `README.md`, or `docs/phase.md` during implementation unless requested.
    - Verifiable: docs changes are absent unless required by command/index change.
