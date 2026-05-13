# Phase 9 Design

## Phase goal

Implement Phase 9 only: backend job creation API and model-selection resolution.

Required result:

- authenticated user can create a queued processing job for own, non-deleted media;
- request parameters are validated before any job row is created;
- backend resolves intended model using documented priority;
- job is stored with `status = queued`, default queue fields, owner fields, and internal processing parameters;
- no media processing runs inside API request.

## Intended behavior from docs

Confirmed:

- Endpoint in scope: `POST /api/jobs`.
- Protected route: guests receive 401.
- Users and admins can create jobs only for media owned by the authenticated account.
- Admin job creation is still scoped to admin-owned media; no delegated processing.
- Media must exist, must not be soft-deleted, and must belong to requester.
- Long image/video processing must not run in request.
- Created job status is `queued`.
- `processing_jobs.input_params_json` contains at least:
  - `confidence_threshold`
  - `iou_threshold`
  - `image_size`
  - `tracker_type`
  - `frame_stride`
- Defaults from CV docs:
  - confidence threshold `0.25`
  - IoU threshold `0.45`
  - image size `640`
  - tracker `ByteTrack` as the documented internal default
  - frame stride `1`
- `frame_stride` is internal and must not be accepted as standard user-facing API input.
- `tracker_type` is user-facing for video jobs only.
- Image jobs reject any client-supplied `tracker_type`; they still do not run tracking and later image detections must have `track_id = null`.
- Model selection priority:
  1. explicit `model_version_id`;
  2. active `model_versions` row;
  3. `ACTIVE_MODEL_ID` only when no active DB model exists.
- `ACTIVE_MODEL_ID` must not override explicit job model or active DB model.
- Store resolved `model_version_id` on job when possible.
- Invalid model, threshold, IoU, or tracker values must be rejected without creating a job.
- Output boundary remains CV-only; Phase 9 does not create detections, tracks, exports, or result files.

Assumptions:

- `POST /api/jobs` response mirrors documented job metadata needed by later status/detail views and existing backend style: job id, owner/media/model ids, status, input params, progress, and timestamps. Phase 9 create response should not include result/export path fields.
- Explicit `model_version_id` may reference any existing registered model, active or inactive, because docs use `is_active` for default selection only. This is the intended Phase 9 API policy and must be covered by tests.
- If no explicit model and no active model exist, `ACTIVE_MODEL_ID` must reference an existing registered model or job creation fails with safe error.
- `confidence_threshold` and `iou_threshold` are accepted as numbers from 0 to 1.
- For video media, `tracker_type` defaults to `bytetrack`; unknown or unsupported values are rejected.
- Phase 9 does not expose or accept `frame_stride` from clients.

## Architecture decisions

- Add a small jobs router and register it under existing `/api` router.
- Keep route handler thin: parse schema, depend on active user and DB session, call service, return schema.
- Put ownership, parameter validation that depends on DB/media, and model resolution in `app.services.jobs`.
- Use existing `MediaFile`, `ModelVersion`, and `ProcessingJob` ORM models.
- Reuse active-user auth dependency; do not add new roles.
- Reuse safe not-found behavior for missing/cross-owner/deleted media.
- Add optional `active_model_id` to settings because `.env.example` and docs define `ACTIVE_MODEL_ID`.
- Do not add migrations; schema already supports Phase 9 fields.
- Do not add worker behavior, queue claiming, progress updates beyond initial defaults, results, downloads, listing, cancellation, frontend, or docs product changes.

## Backend impact

Touched:

- New jobs API module.
- New jobs schemas.
- New jobs service.
- API router registration.
- Settings field for `ACTIVE_MODEL_ID`.
- Focused backend tests.
- Backend index only if file inventory changes during implementation.

Not touched:

- Media upload behavior.
- Model registry behavior except reading existing model rows.
- CV worker.
- Results/downloads APIs.
- Experiments/admin APIs.
- Frontend.
- Database migration, unless implementation discovers verified schema mismatch.

## API impact

Implemented endpoint:

- `POST /api/jobs`

Access:

- Guest: 401.
- Active user/admin: may create job for own non-deleted media only.
- Cross-owner or missing/deleted media: safe 404-style behavior.

Request:

- Required media reference.
- Optional `model_version_id`.
- Optional user-facing processing parameters:
  - `confidence_threshold`
  - `iou_threshold`
  - `tracker_type` for video media only
- No standard client field for `frame_stride`.
- Internal `image_size = 640` unless existing configuration is introduced for it.

Response:

- Safe job resource with queued status, no unsafe absolute paths, and no result/export path fields in Phase 9 create response.
- Must not expose password hashes, tokens, secrets, stored media absolute path, model resolved absolute path, or filesystem internals.

## Database impact

- Use existing `processing_jobs` table.
- No schema field planned.
- On successful create:
  - `user_id = current_user.id`
  - `media_file_id = validated media.id`
  - `model_version_id = resolved model id when available`
  - `status = queued`
  - `progress_percent = 0`
  - `retry_count = 0`
  - `input_params_json` includes documented defaults and validated values, including internal `frame_stride = 1`
  - result/export paths, lock fields, heartbeat, start/completion, and error fields remain null
- Roll back and create no row on validation failure.

## Frontend impact

- No frontend source changes in this phase.
- Future frontend upload page can call `POST /api/jobs` after this backend endpoint exists.
- `frame_stride` must remain hidden from standard UI; Phase 9 reinforces by not accepting it as user input.

## Security/privacy impact

Touched:

- JWT required.
- Inactive users rejected through existing active-user dependency.
- Ownership enforced before job creation.
- Cross-owner media hidden behind safe not-found behavior.
- Soft-deleted media cannot create jobs.
- Invalid requests do not create queued work.
- No absolute storage paths exposed.
- No secrets/tokens/password data in responses or logs.

Not touched:

- Upload validation internals.
- Downloads/path serving.
- Worker logs.
- CORS behavior.

## Test strategy

Relevant automated checks:

- From `backend/`: `python -m ruff check .`
- From `backend/`: `python -m pytest tests/test_jobs_api.py`
- From `backend/`: `python -m pytest tests/test_media_api.py tests/test_models_api.py tests/test_auth.py tests/test_settings.py`

Required Phase 9 test cases:

- Guest cannot create job.
- Inactive user token cannot create job.
- User can create queued job for own non-deleted media with defaults.
- Admin can create queued job for admin-owned media.
- User cannot create job for another user's media.
- User cannot create job for soft-deleted media.
- Missing media id is rejected safely.
- Explicit valid `model_version_id` wins over active DB model.
- Active DB model is used when explicit model is omitted.
- `ACTIVE_MODEL_ID` fallback is used only when no active DB model exists.
- `ACTIVE_MODEL_ID` does not override explicit model.
- `ACTIVE_MODEL_ID` does not override active DB model.
- Missing/invalid explicit model is rejected.
- No active DB model plus unset/invalid fallback is rejected.
- Invalid confidence threshold is rejected.
- Invalid IoU threshold is rejected.
- Invalid tracker type is rejected.
- Client-supplied `tracker_type` for image media is rejected, including the default value, because tracker selection is user-facing for video only.
- Video media can omit `tracker_type` and receive the documented default `bytetrack`.
- Client-supplied `frame_stride` is ignored or rejected; no user input can change stored internal `frame_stride = 1`.
- Explicit selection of an inactive registered model version succeeds by intended API policy.
- Successful job stores `status = queued`, `progress_percent = 0`, `retry_count = 0`, and documented `input_params_json`.
- Validation failures create no `processing_jobs` row.
- Response body contains no absolute paths, path-like result/export fields, password hashes, tokens, or secrets.

Skipped as out of scope:

- Job list/detail/delete endpoints.
- Worker queue claim tests.
- CV processing tests.
- Results/download/export tests.
- Frontend tests/build.
- Docker Compose smoke unless backend startup wiring changes.

## Ambiguities or conflicts

- WARNING: CONFLICT
  - `docs/index.md` and `README.md` current-state text lag actual backend implementation.
  - Phase selection comes from `docs/phase.md`; implementation-state facts come from actual backend source and `backend/index.md`.
- Ambiguity: exact request/response schema is not fully specified in API docs. Use documented parameter names and existing backend schema style only.
- Resolved from review: image requests with client-supplied `tracker_type` are rejected; tracker selection is user-facing for video only.
- Resolved from review: explicit selection of inactive registered model versions is intended Phase 9 API policy.
- Ambiguity: BoT-SORT support is optional. Do not add worker/runtime claims in Phase 9.
- Ambiguity: exact threshold bounds are not stated. Use 0-1 as conservative CV threshold validation.
