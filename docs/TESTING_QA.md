# TESTING_QA.md

## Purpose

This document defines testing and QA expectations for the Drone Computer Vision Subsystem.

This document is canonical for:

- acceptance criteria;
- test coverage expectations;
- manual end-to-end scenarios;
- security verification;
- worker queue reliability checks;
- frontend UI state checks;
- CV output verification;
- Docker launch verification.

This document is not canonical for implementation order, code structure, or route details beyond what must be verified.

## Testing Philosophy

Testing should prove that the final product works as a full-stack application, not just as isolated scripts.

The system is considered ready only when:

- Docker Compose can launch the application after initial setup;
- authentication works;
- users can upload and process images and videos;
- the worker processes queued jobs reliably;
- detections and tracks are stored correctly;
- exports work;
- frontend UI states are complete;
- admin-only features are protected;
- the CV-only safety boundary is preserved.

## Acceptance Criteria Summary

The project is functionally complete when all of the following are true:

- frontend is accessible in the browser;
- backend API is accessible;
- PostgreSQL is running;
- CV worker is running;
- backend health endpoints work;
- worker logs selected device on startup;
- registration works when public registration is enabled;
- public registration can be disabled;
- login works;
- JWT authentication works;
- seeded admin account works;
- users can upload images and videos;
- users can create processing jobs;
- image processing works;
- video processing works;
- video tracking includes track IDs when available;
- progress updates during video processing;
- no-detection jobs complete successfully;
- detection records are stored;
- job summaries are generated;
- CSV export works;
- JSON export works;
- downloads work from UI;
- model comparison data can be displayed;
- threshold analysis data can be displayed;
- tracker behavior comparison data can be displayed;
- false-positive analysis can be displayed;
- experiment empty states work;
- UI is Ukrainian;
- UI uses polished dashboard components;
- system outputs only CV data.

## Test Layers

Testing should cover:

| Layer | Focus |
|---|---|
| Backend tests | Auth, API behavior, ownership, validation, job creation. |
| Data model tests | Constraints, relationships, indexes, soft deletion, active model rule. |
| Worker tests | Queue claiming, heartbeat, stale recovery, image/video processing. |
| CV tests | Detection output shape, bbox coordinates, tracking IDs, no-detection behavior. |
| Export tests | CSV and JSON contracts. |
| Frontend tests | Routes, forms, states, role visibility, Ukrainian text. |
| Security tests | Unauthorized access, ownership checks, upload validation, CORS, path safety. |
| Docker smoke tests | Full-stack launch and service health. |
| Manual E2E tests | Realistic user and admin workflows. |

## Docker and Launch Tests

Verify:

- `postgres` starts successfully;
- `backend` starts successfully;
- `cv-worker` starts successfully;
- `frontend` starts successfully;
- shared storage directories exist or are created by setup flow;
- backend health endpoint returns service status;
- backend database health endpoint verifies database connectivity;
- migrations run successfully;
- seeded admin account is created;
- base CPU launch works;
- GPU launch works when host GPU setup is available;
- only `cv-worker` requests GPU access;
- worker logs selected device.

The base application must work without GPU.

## Authentication Tests

Verify:

- user can register when `ALLOW_PUBLIC_REGISTRATION=true`;
- password shorter than 8 characters is rejected;
- user can log in with valid credentials;
- login fails with invalid credentials;
- JWT token allows access to protected routes;
- missing or invalid token blocks protected routes;
- seeded admin can log in;
- public registration returns forbidden behavior when disabled;
- public registration always creates `user` role;
- public registration cannot create an admin account.

## Authorization and Ownership Tests

Verify:

- regular user sees only own media;
- regular user sees only own jobs;
- regular user cannot access another user's job details;
- regular user cannot download another user's annotated media;
- regular user cannot download another user's CSV/JSON exports;
- regular user cannot register model versions;
- regular user cannot activate model versions;
- regular user cannot import experiments;
- regular user cannot access admin routes;
- admin can view global jobs;
- admin can view global media metadata;
- admin can access admin-only routes;
- admin can also perform regular user actions.

## Upload Validation Tests

Verify accepted image formats:

- `.jpg`;
- `.jpeg`;
- `.png`;
- `.webp`.

Verify accepted video formats:

- `.mp4`;
- `.avi`;
- `.mov`;
- `.mkv`.

Verify rejection of:

- unsupported extensions;
- invalid MIME types;
- files exceeding image size limit;
- files exceeding video size limit;
- unsafe filenames;
- path traversal attempts;
- user-submitted storage paths.

Verify that stored paths are generated and relative to `STORAGE_ROOT`.

## Media Metadata Tests

For image uploads, verify:

- `media_type = image`;
- width and height are detected when possible;
- `frame_count = 1`;
- `fps = null`;
- `duration_seconds = null`.

For video uploads, verify:

- `media_type = video`;
- frame count is detected when possible;
- FPS is detected when possible;
- duration is detected when possible;
- width and height are detected when possible.

## Job Creation Tests

Verify:

- job can be created for own uploaded media;
- job cannot be created for another user's media;
- invalid model version is rejected;
- inactive model can be selected only if intended by API policy;
- confidence threshold validation works;
- IoU threshold validation works;
- tracker type validation works;
- created job status is `queued`;
- job records store input parameters;
- `frame_stride` defaults internally to `1`.

## Queue Reliability Tests

Verify:

- worker claims queued jobs using PostgreSQL row-level locking;
- two workers do not claim the same job;
- claim transaction is short;
- worker does not hold transaction open during media processing;
- job moves from `queued` to `processing`;
- `locked_by` is set;
- `locked_at` is set;
- `started_at` is set;
- `last_heartbeat_at` is set;
- progress updates during video processing;
- worker marks successful jobs as `completed`;
- worker marks failed jobs as `failed` with error message.

## Heartbeat and Stale Recovery Tests

Verify:

- video jobs update heartbeat every configured frame/time interval;
- image jobs complete with final progress update;
- stale processing job is detected after configured timeout;
- stale job resets to `queued` when retry count is below max;
- retry count increments on stale reset;
- stale job becomes `failed` when retry count reaches max;
- worker restart does not leave jobs permanently stuck in `processing`.

## Image Processing Tests

Verify:

- image job completes successfully;
- annotated image is created;
- detections are stored when model finds drones;
- image detections have `frame_index = 0`;
- image detections have `timestamp_ms = 0`;
- image detections have `track_id = null`;
- bounding boxes are original-resolution pixel coordinates;
- result paths are relative;
- CSV and JSON exports are created.

## Video Processing Tests

Verify:

- video job completes successfully;
- annotated video is created or downloadable;
- progress updates during processing;
- detections are stored with frame indices;
- timestamps are stored in milliseconds;
- track IDs are stored when available;
- track IDs may be `null` when tracker does not provide them;
- track summaries are created;
- average FPS and processing duration are calculated;
- CSV and JSON exports are created.

## No-Detection Tests

Verify that a no-detection image or video:

- completes successfully;
- stores `status = completed`;
- has `total_detections = 0`;
- has `frames_with_detections = 0`;
- has `average_confidence = null`;
- has `maximum_confidence = null`;
- creates CSV export with headers only;
- creates JSON export with empty `detections` array;
- displays a Ukrainian-language empty state in the UI;
- does not display an error state.

## Export Tests

CSV export must verify:

- one row per detection;
- all required columns exist;
- no-detection CSV has headers only;
- bounding box corner columns exist;
- derived center-size columns exist;
- track ID column exists;
- model version and tracker type are included.

JSON export must verify:

- top-level `job` object exists;
- top-level `media` object exists;
- top-level `model` object exists;
- top-level `parameters` object exists;
- top-level `summary` object exists;
- top-level `detections` array exists;
- top-level `tracks` array exists;
- no-detection JSON has empty `detections` array;
- JSON does not include forbidden external output fields.

## Model Registry Tests

Verify:

- authenticated users can view models;
- regular users cannot register models;
- regular users cannot activate models;
- admins can register model versions;
- admins can activate one model version;
- only one model is active at a time;
- model family displays actual family used;
- YOLO11 fallback metadata is represented when fallback is used;
- model weights paths are relative.

## Model Selection Priority Tests

Verify model resolution priority:

1. job-specific `model_version_id` is used when present;
2. database active model is used when job-specific model is absent;
3. `ACTIVE_MODEL_ID` is used only when no active database model exists;
4. `ACTIVE_MODEL_ID` does not override job-specific selection;
5. `ACTIVE_MODEL_ID` does not override database active model.

## Experiment Tests

Verify:

- admin can import experiment results;
- regular users can view only published experiments;
- admins can view unpublished experiments;
- model comparison data displays;
- threshold analysis data displays;
- tracker behavior comparison data displays;
- false-positive analysis summary displays;
- confusion matrix image displays when available;
- missing experiment data shows empty state;
- `metric_value = null` does not crash UI;
- raw `null` is not displayed to users.

Required Ukrainian empty-state text for missing experiment data:

```text
Дані експерименту ще не завантажено
```

## Frontend Route Tests

Verify:

- `/login` renders login form;
- `/register` renders registration form when enabled;
- `/register` redirects or shows notice when registration disabled;
- protected routes require authentication;
- `/dashboard` shows user or admin statistics appropriately;
- `/upload` supports upload and job creation flow;
- `/jobs` lists user jobs;
- `/jobs/:jobId` shows job details;
- `/models` lists registered models;
- `/experiments` handles data and empty states;
- `/admin` is admin-only.

## Frontend UI Quality Tests

Verify:

- UI text is Ukrainian;
- technical labels such as FPS, mAP, YOLO, CSV, JSON are acceptable;
- layout uses shadcn/ui and Tailwind styling;
- cards, tables, badges, and charts are used appropriately;
- loading states exist;
- error states exist;
- empty states exist;
- UI does not look like a raw debug panel;
- admin navigation appears only for admins;
- `frame_stride` is not visible in standard UI;
- absolute paths are not shown.

## Security Tests

Verify:

- passwords are hashed;
- JWT secret is not exposed;
- tokens are not logged;
- password values are not logged;
- CORS uses configured explicit origins;
- wildcard CORS is not used in non-local configuration;
- path traversal attempts fail;
- user-uploaded files are not executed;
- unsupported file types fail;
- admin endpoints reject regular users;
- result downloads enforce ownership;
- API responses do not expose absolute filesystem paths.

## Logging Tests

Verify that logs include:

- login/register events without passwords;
- media upload events;
- job creation;
- job status transitions;
- worker job claim events;
- stale job recovery events;
- model loading;
- selected CV device on startup;
- processing start/end with duration;
- export generation;
- processing errors in worker logs.

Verify that logs do not include:

- plain passwords;
- JWT tokens;
- JWT secrets;
- database passwords;
- sensitive environment values.

## Safety Boundary Tests

Verify that API responses and JSON exports include only allowed CV data:

- detection status;
- frame index;
- timestamp;
- bounding box;
- image-space center point;
- confidence;
- class label;
- track ID;
- FPS;
- model version.

Verify that API responses and exports do not include:

- interception course;
- flight control commands;
- motor commands;
- aiming commands;
- weapon or payload commands;
- geospatial targeting data;
- autonomous engagement decisions.

Verify that all coordinates are image-space coordinates only.

## Manual End-to-End Scenarios

### Scenario 1: Regular User Image Processing

1. Register a new user.
2. Log in.
3. Upload a valid image.
4. Create a processing job with defaults.
5. Wait for completion.
6. View annotated image.
7. Inspect detection table.
8. Download CSV.
9. Download JSON.
10. Confirm user cannot access admin page.

### Scenario 2: Regular User Video Processing

1. Log in as regular user.
2. Upload valid video.
3. Create processing job with defaults.
4. Observe queued/processing status.
5. Observe progress updates.
6. Wait for completion.
7. View or download annotated video.
8. Inspect detections and track summaries.
9. Download CSV and JSON.

### Scenario 3: No-Detection Result

1. Upload media expected to contain no drones.
2. Create processing job.
3. Confirm job completes successfully.
4. Confirm empty detection state appears in Ukrainian.
5. Confirm CSV and JSON exports exist.

### Scenario 4: Admin Model Management

1. Log in as seeded admin.
2. Open models page.
3. Register a model version using existing storage paths.
4. Activate the model.
5. Confirm active model appears on dashboard or upload page.
6. Confirm regular user cannot activate models.

### Scenario 5: Admin Experiments

1. Log in as admin.
2. Import experiment metrics.
3. Open experiments page.
4. Confirm model comparison displays.
5. Confirm threshold analysis displays.
6. Confirm tracker behavior comparison displays.
7. Confirm false-positive analysis displays.
8. Confirm regular user sees only published experiment results.

### Scenario 6: Stale Job Recovery

1. Create a job.
2. Force or simulate worker crash during processing.
3. Confirm job becomes stale after configured timeout.
4. Confirm stale job is reset or failed according to retry count.
5. Restart worker.
6. Confirm no job stays permanently stuck.

## Regression Checklist

Before considering a change complete, verify that it does not break:

- Docker Compose launch;
- authentication;
- seeded admin login;
- media upload;
- job creation;
- worker queue claiming;
- image processing;
- video processing;
- CSV export;
- JSON export;
- model selection priority;
- user ownership checks;
- admin route protection;
- experiment empty states;
- Ukrainian UI text;
- CV-only safety boundary.
