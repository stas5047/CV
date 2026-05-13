# Phase 9 Implementation Plan

## Scope

Phase only: Phase 9 - Job creation API and model selection resolution.

Do not implement:

- job list/detail/delete/cancel endpoints;
- result summary, detections, tracks, downloads, CSV, or JSON endpoints;
- CV worker queue polling or media processing;
- frontend upload/job UI;
- experiment/admin APIs;
- model upload or training launch;
- new database fields unless a verified schema mismatch blocks Phase 9.

## Ordered atomic plan

1. [@role/developer-backend] Re-read Phase 9 contract before coding.
   - Verify `docs/phase.md` still says Phase 9.
   - Verify relevant docs remain `docs/API.md`, `docs/CV_PIPELINE.md`, `docs/DATA_MODEL.md`, `docs/AUTH_SECURITY.md`, and `docs/TESTING_QA.md`.
   - Verifiable: no source change in this step.

2. [@role/developer-backend] Inspect current backend patterns.
   - Read existing media/model API, schema, service, auth dependency, settings, and tests.
   - Confirm no jobs API files already exist.
   - Verifiable: identify exact dependencies and response model style before editing.

3. [@role/tester] Add Phase 9 failing tests first.
   - Create `backend/tests/test_jobs_api.py`.
   - Test auth, active-account, ownership, soft deletion, defaults, media-type-aware tracker validation, invalid params, no-row-on-failure, response path safety, explicit inactive-model policy, and model priority.
   - Use existing SQLite/TestClient fixture style from media/model tests.
   - Verifiable: `python -m pytest tests/test_jobs_api.py` fails because endpoint/modules do not exist yet.

4. [@role/developer-backend] Add `ACTIVE_MODEL_ID` setting.
   - Modify `backend/app/core/config.py`.
   - Add optional setting mapped to `ACTIVE_MODEL_ID`.
   - Keep `__repr__` safe; do not treat model id as secret.
   - Update `backend/tests/test_settings.py` for empty/unset and configured value behavior.
   - Verifiable: settings tests cover new documented env field.

5. [@role/developer-backend] Add job schemas.
   - Create `backend/app/schemas/jobs.py`.
   - Define create request with documented user-facing fields only:
     - media id;
     - optional model version id;
     - optional confidence threshold;
     - optional IoU threshold;
     - optional tracker type for video media only.
   - Do not expose client `frame_stride`.
   - Define response schema from existing `ProcessingJob` fields safe for API output; do not include result/export path fields in Phase 9 create response.
   - Verifiable: validation rejects out-of-range thresholds, unknown tracker values, and image requests that supply `tracker_type` through API tests.

6. [@role/developer-backend] Add job service media validation.
   - Create `backend/app/services/jobs.py`.
   - Load media by id where `deleted_at IS NULL`.
   - Enforce current user owns media; admin creation still requires admin-owned media.
   - Use safe not-found behavior for missing, deleted, or cross-owner media.
   - Verifiable: own-media succeeds; cross-owner/deleted/missing media fails and creates no job row.

7. [@role/developer-backend] Add processing parameter resolution.
   - Apply defaults from docs:
     - confidence `0.25`;
     - IoU `0.45`;
     - image size `640`;
     - tracker `bytetrack`;
     - frame stride `1`.
   - Store resolved values in `input_params_json`.
   - Ensure user input cannot set `frame_stride`.
   - Reject invalid threshold or tracker values before creating job.
   - Reject any client-supplied `tracker_type` for image media; tracker selection is user-facing for video only.
   - Allow video media to omit `tracker_type` and receive default `bytetrack`.
   - Verifiable: success test inspects stored JSON; invalid/media-type-mismatch tests show no job row.

8. [@role/developer-backend] Add model-selection resolution.
   - If explicit `model_version_id` present, require existing registered model and use it, including inactive registered models by intended Phase 9 API policy.
   - Else use active `ModelVersion.is_active = true` row when present.
   - Else use `settings.active_model_id` only when no active DB model exists.
   - Require fallback id to reference an existing model before job creation.
   - Do not let fallback override explicit model or active DB model.
   - Verifiable: model-priority tests cover explicit active, explicit inactive, active default, fallback, and override cases.

9. [@role/developer-db] Create queued `ProcessingJob` row.
   - Set `user_id`, `media_file_id`, resolved `model_version_id`, `status = queued`, `progress_percent = 0`, and documented `input_params_json`.
   - Leave result/export paths, lock fields, heartbeat, start/completed timestamps, summary, and error null.
   - Commit only after all validation and model resolution passes.
   - Verifiable: database row matches expected defaults; validation failures leave row count unchanged.

10. [@role/developer-backend] Add jobs API route.
    - Create `backend/app/api/jobs.py`.
    - Implement `POST /api/jobs`.
    - Use `get_current_active_user`, DB session dependency, and settings dependency.
    - Return safe job response.
    - Verifiable: route exists exactly at `/api/jobs`.

11. [@role/developer-backend] Register jobs router.
    - Modify `backend/app/api/router.py`.
    - Include jobs router under existing `/api` prefix.
    - Verifiable: TestClient can post to `/api/jobs`.

12. [@role/tester] Run targeted Phase 9 test gate.
    - Command from `backend/`: `python -m pytest tests/test_jobs_api.py`
    - Expected: PASS after implementation.
    - If FAIL, record exact failing case and fix within Phase 9 scope.

13. [@role/tester] Run related regression gates.
    - Command from `backend/`: `python -m pytest tests/test_media_api.py tests/test_models_api.py tests/test_auth.py tests/test_settings.py`
    - Expected: PASS.
    - Reason: Phase 9 depends on media ownership, model registry, auth, and settings.

14. [@role/tester] Run lint gate.
    - Command from `backend/`: `python -m ruff check .`
    - Expected: PASS.

15. [@role/code-reviewer] Review Phase 9 diff against docs.
    - Check endpoint path and access behavior.
    - Check no cross-owner media job creation.
    - Check no jobs for soft-deleted media.
    - Check model priority order.
    - Check `ACTIVE_MODEL_ID` fallback cannot override explicit or active DB model.
    - Check client `tracker_type` is allowed for video jobs only and rejected for image jobs.
    - Check explicit inactive registered model selection is covered as intended API policy.
    - Check no media processing in API request.
    - Check `frame_stride` remains internal.
    - Check no absolute paths, result/export path fields, secrets, tokens, or password hashes in responses.
    - Check no later-phase endpoints or worker/frontend behavior leaked in.
    - Verifiable: review notes no blocking doc mismatch, or blocker cites exact file/doc rule.

16. [@role/docs-maintainer] Update index only if implementation changes file inventory.
    - Update `backend/index.md` if new jobs files/tests are added.
    - Do not modify product docs.
    - Do not modify `docs/index.md`, `README.md`, or `docs/phase.md` unless user explicitly requests.
    - Verifiable: docs changes are limited to backend index if needed.
