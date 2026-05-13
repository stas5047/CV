# Drone Computer Vision Subsystem ROADMAP.md

## Roadmap purpose

This roadmap breaks the Drone Computer Vision Subsystem into implementation phases for AI coding agents. It assumes the nine core documentation files are the current source of truth:

1. `PROJECT_CONTEXT.md`
2. `ARCHITECTURE.md`
3. `DATA_MODEL.md`
4. `API.md`
5. `AUTH_SECURITY.md`
6. `CV_PIPELINE.md`
7. `TRAINING_EXPERIMENTS.md`
8. `FRONTEND_UX.md`
9. `TESTING_QA.md`

The phases are intentionally small and ordered to reduce context overflow. Backend, database, API, security, worker, model/training utilities, and integration work are completed before frontend feature implementation. Frontend phases start only after the backend APIs, worker queue, result contracts, and demo runtime are available.

## Final product target

The final product is a local/demo-ready full-stack web application where:

- PostgreSQL, FastAPI backend, separate CV worker, and React frontend start through Docker Compose.
- Local/demo startup can run with `docker compose up --build` after documented `.env` setup and required local model artifacts.
- Backend startup applies Alembic migrations automatically in local/demo mode.
- Idempotent seed/setup logic creates the initial admin account from environment variables.
- Required storage folders are created or verified automatically.
- Large datasets, trained weights, uploads, processed videos, and generated results are stored in filesystem storage and are not committed to Git.
- Authenticated users can upload validated images/videos, create processing jobs, watch job status, view annotated results, inspect detections/tracks, and download annotated media, CSV exports, and JSON exports.
- Admin users can additionally view global history, manage model registry records, activate a model, import experiment metrics, view users, and run conservative storage cleanup.
- The CV worker processes queued jobs through PostgreSQL and shared storage, not through backend-to-worker HTTP calls.
- Image and video processing use a YOLO-based single-class `drone` detector.
- Video processing uses ByteTrack by default and may support BoT-SORT as an alternative tracker.
- No-detection jobs complete successfully and still produce usable result/export artifacts when possible.
- Training is performed outside the running web application; the app only imports/registers resulting model and experiment artifacts.
- Visible frontend UI text is Ukrainian; code, API fields, database identifiers, logs, and developer-facing comments are English.
- All API responses, UI displays, and exports remain inside the computer-vision-only boundary: image-space detections, bounding boxes, confidence, timestamps, track IDs, model data, and performance metrics only.

## Fixed implementation decisions

These decisions are frozen by the documentation and must not be deferred to research during implementation.

| Area | Decision |
|---|---|
| Product type | Dockerized full-stack web application for detecting and visually tracking drones in uploaded images and videos. |
| System boundary | Computer-vision-only subsystem; no physical interception, navigation, flight control, hardware control, targeting, aiming, payload, geolocation, or engagement logic. |
| Backend | Python, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL. |
| API base path | All API routes are prefixed with `/api`. |
| Auth | JWT access tokens; password hashing with bcrypt or Argon2; exactly two roles: `user` and `admin`. |
| Public registration | Controlled by `ALLOW_PUBLIC_REGISTRATION`; public registration always creates `user` accounts only. |
| Seeded admin | Created through setup/seed flow from `ADMIN_EMAIL` and `ADMIN_PASSWORD`. |
| Database | PostgreSQL stores structured records and metadata only. |
| Database tables | `users`, `media_files`, `processing_jobs`, `detections`, `tracks`, `model_versions`, `experiment_runs`, `experiment_metrics`. |
| Migrations | Alembic migrations; local/demo backend startup applies migrations automatically. |
| Seeds | Idempotent seed/setup logic; at minimum seeded admin; optional demo/model/experiment records only when documented and safe. |
| Storage | Shared filesystem storage mounted by backend and CV worker at `/app/storage`; database stores relative paths only. |
| Required storage folders | `uploads/`, `results/`, `reports/`, `models/`, `temp/`, `datasets/`. |
| Queue | PostgreSQL-based queue using `processing_jobs`; no Celery/Redis in first implementation. |
| Worker claim | Row-level locking with `FOR UPDATE SKIP LOCKED`; short claim transaction; processing outside transaction. |
| Runtime services | `postgres`, `backend`, `cv-worker`, `frontend`; optional reverse proxy is not required for first implementation. |
| CV stack | Python, PyTorch, Ultralytics YOLO, `opencv-python-headless`, NumPy, pandas. |
| Model family | YOLO26 primary; YOLO11 fallback only after YOLO26 unavailability is reported and documented. |
| Detection task | Single-class object detection: `drone`. |
| Tracking | ByteTrack default for video; BoT-SORT optional alternative when supported. |
| Device policy | CPU inference must work; optional GPU acceleration is isolated to `cv-worker` through `CV_DEVICE`. |
| Upload types | Images: `.jpg`, `.jpeg`, `.png`, `.webp`; videos: `.mp4`, `.avi`, `.mov`, `.mkv`. |
| Upload limits | Configurable through `MAX_IMAGE_SIZE_MB` and `MAX_VIDEO_SIZE_MB`. |
| Processing params | User-facing: model version, confidence threshold, IoU threshold, tracker type for video. Internal: `frame_stride = 1`. |
| Frontend | React, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Recharts. |
| Frontend language | Ukrainian for all visible UI text, errors, empty states, labels, toasts, table headings where practical. |
| Frontend charting | Recharts only; no Matplotlib in web UI. |
| Training | Kaggle/Colab or equivalent cloud notebook workflow; not launched from API or web UI. |
| Exports | CSV with one row per detection; JSON with job, media, model, parameters, summary, detections, and tracks. |
| Production deployment | Not required for MVP/educational project. |

## Scope and safety guardrails

The implementation must not add features outside the documented MVP.

Do not implement:

- physical drone interception;
- autopilot, navigation, motor, payload, aiming, or flight-control behavior;
- trajectory planning or real-world coordinate conversion;
- geospatial targeting data;
- autonomous engagement decisions;
- RTSP, webcam, or live camera processing;
- Streamlit, Flask, Celery, or Redis in the first implementation;
- model training from the web UI;
- binary media, result files, model weights, datasets, or report images in PostgreSQL;
- committing datasets, model weights, uploads, processed videos, or generated results to Git;
- GUI-dependent OpenCV calls inside containers;
- complex enterprise RBAC beyond `user` and `admin`;
- email confirmation, password reset email, OAuth, social login, CAPTCHA, account lockout, or two-factor auth unless explicitly approved later.

## Phase execution rules

Each medium/high-risk phase should be executed as two separate conversations:

1. **Planning / research / design chat:** inspect only the relevant docs and current code, identify edge cases, produce a precise implementation plan, and list validation commands.
2. **Implementation / verification chat:** implement the approved plan, run checks, fix failures, and provide a completion report.

Sizing rules:

- A phase should fit roughly 50-60% of the planning model context window.
- If a phase becomes too large, split it before coding.
- Do not combine frontend and backend product feature work in one phase.
- Backend and CV worker work may be coordinated only when the phase is specifically about their integration.
- Infrastructure, QA, and release phases may touch root files, but must not add mixed product functionality.
- A phase is complete only when validation passes or remaining failures are documented as blockers.
- If a phase changes commands, environment variables, seed behavior, Docker behavior, artifact layout, or credentials, update README or implementation notes in the same phase.

## Standard quality gate

Before marking any phase complete:

- Re-read the listed relevant docs for the phase.
- Keep the CV-only boundary intact.
- Enforce authentication, authorization, account activity, and ownership checks for protected actions.
- Keep frontend-visible text Ukrainian and internal/API/database identifiers English.
- Store only relative file paths in the database.
- Prevent path traversal and never expose unsafe absolute filesystem paths in API responses.
- Do not log passwords, password hashes, JWT tokens, JWT secrets, database passwords, or sensitive environment values.
- Keep no-detection processing as a successful completed result.
- Use `opencv-python-headless` inside containers and avoid GUI OpenCV calls.
- Ensure CPU mode still works even if GPU support is added.
- Run relevant formatting, linting, typing, test, build, and Docker commands.
- Document any blocker clearly with the failing command and exact reason.

## Target repository layout

The implementation should generally converge toward this structure:

```text
project-root/
  backend/
  frontend/
  cv/
  training/
  scripts/
  storage/
    uploads/
    results/
    reports/
    models/
    temp/
    datasets/
  docs/
  docker-compose.yml
  docker-compose.gpu.yml
  Makefile
  .env.example
  README.md
```

The exact internal structure may be refined during implementation, but service boundaries must remain clear.

---

# Implementation phases

## Phase 1 - Repository scaffold, environment, and Docker baseline

**Direction:** DevOps / Repository setup  
**Goal:** Create the project skeleton and a minimal Compose runtime without product business logic.

### Scope

- Create or normalize root structure: `backend/`, `frontend/`, `cv/`, `training/`, `scripts/`, `storage/`, `docs/` if not already present.
- Add `.gitignore` rules for `.env`, uploads, results, datasets, model weights, generated reports, temp files, Python caches, Node artifacts, and build outputs.
- Add `.env.example` with safe placeholders for database, auth, storage, backend, worker, and CV variables.
- Add initial `docker-compose.yml` with `postgres`, `backend`, `cv-worker`, and `frontend` services as buildable placeholders.
- Add optional `docker-compose.gpu.yml` or GPU profile placeholder for `cv-worker` only.
- Ensure backend and worker both mount shared storage at `/app/storage`.
- Add storage-directory bootstrap script or Makefile target.
- Add README section for initial setup and expected one-command local/demo launch.
- Avoid implementing frontend UI or backend product routes beyond placeholders.

### Relevant docs

- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- `docker compose config` succeeds.
- `.env.example` contains no real secrets.
- Storage directories can be created locally.
- Git status does not include generated storage contents.
- README documents the current state honestly.

### Commit

`chore(scaffold): add repository layout environment and compose baseline`

---

## Phase 2 - Backend FastAPI scaffold, settings, logging, and health

**Direction:** Backend  
**Goal:** Create the FastAPI backend foundation with configuration, logging, and health checks.

### Scope

- Scaffold `backend/` Python project.
- Add dependency management for FastAPI, Pydantic v2, Uvicorn/Gunicorn-Uvicorn, SQLAlchemy 2.x, Alembic, PostgreSQL driver, auth/security helpers, testing tools, and lint/format tools.
- Implement typed settings loaded from environment variables.
- Implement app factory or main app module.
- Implement structured logging baseline that does not log secrets.
- Implement public health endpoints:
  - `GET /api/health`;
  - `GET /api/health/db`.
- Add database connectivity layer skeleton.
- Add CORS configuration using explicit configured origins.
- Add backend Dockerfile and startup entrypoint placeholder.
- Add initial backend tests for health and settings.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Backend lint/format checks pass.
- Backend test suite passes.
- `GET /api/health` returns a safe status response.
- `GET /api/health/db` verifies PostgreSQL connectivity without leaking secrets.
- Backend container starts in Docker Compose.

### Commit

`feat(backend): scaffold FastAPI settings logging and health`

---

## Phase 3 - Database schema and initial Alembic migration

**Direction:** Backend / Database  
**Goal:** Implement the concrete PostgreSQL schema and initial migration.

### Scope

- Add SQLAlchemy models for:
  - `users`;
  - `media_files`;
  - `processing_jobs`;
  - `detections`;
  - `tracks`;
  - `model_versions`;
  - `experiment_runs`;
  - `experiment_metrics`.
- Use UUID primary keys where appropriate.
- Add required enums/checks for roles, media types, job statuses, and experiment types.
- Add required foreign keys, relationships, indexes, unique constraints, and soft-deletion fields.
- Enforce only one active model version at a time where feasible with PostgreSQL constraints/indexes.
- Enforce relative-path storage at service validation level, and add database checks where practical.
- Add Alembic configuration and generate initial migration.
- Add database smoke tests for constraints and relationships.
- Document limitations where cross-table rules cannot be expressed cleanly in the database.

### Relevant docs

- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Alembic migration applies successfully to a fresh PostgreSQL database.
- Alembic migration can be run inside the backend container.
- Representative invalid rows are rejected by database constraints or covered by service validation TODO/tests.
- Required indexes exist.
- Backend test suite still passes.

### Commit

`feat(backend-db): add SQLAlchemy models and initial Alembic migration`

---

## Phase 4 - Backend startup migrations, idempotent seed/setup, and storage bootstrap

**Direction:** Backend / DevOps  
**Goal:** Make local/demo backend startup prepare the database and minimal demo setup automatically.

### Scope

- Add backend startup script that can run `alembic upgrade head` before starting the API in local/demo mode.
- Add an idempotent seed/setup command.
- Seed the initial admin account from `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
- Hash the seeded admin password before storage.
- Ensure public registration never creates admin accounts.
- Create or verify required storage directories under `STORAGE_ROOT`.
- Optionally seed documented placeholder model/experiment metadata only when corresponding relative artifacts exist.
- Add environment switches such as `RUN_MIGRATIONS_ON_START` and `RUN_SEED_ON_START` if useful.
- Document demo credentials policy and local-only warning.
- Ensure seed can run repeatedly without duplicating records.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Clean database startup applies migrations automatically in local/demo mode.
- Seed command creates exactly one admin account for the configured email.
- Re-running seed does not duplicate users or model/experiment placeholder records.
- Storage folders are created or verified.
- Seeded admin can authenticate once auth is implemented, or the seed output is testable at database level in this phase.

### Commit

`chore(backend-seed): add migrations seed setup and storage bootstrap`

---

## Phase 5 - Authentication and account activity

**Direction:** Backend / Security  
**Goal:** Implement registration, login, current-user, JWT, password hashing, and account activity checks.

### Scope

- Implement password hashing with bcrypt or Argon2.
- Implement JWT access-token creation and verification.
- Implement auth dependencies/middleware for protected routes.
- Implement endpoints:
  - `POST /api/auth/register`;
  - `POST /api/auth/login`;
  - `GET /api/auth/me`;
  - `POST /api/auth/logout` as optional consistency endpoint.
- Enforce `ALLOW_PUBLIC_REGISTRATION`.
- Enforce minimum password length of 8 characters.
- Ensure registration always creates `role = user`.
- Reject inactive users at login and on protected-route access.
- Ensure API responses never expose password hashes or tokens except login token response.
- Add tests for register/login/me/inactive/disabled-registration cases.

### Relevant docs

- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Registration works when public registration is enabled.
- Registration returns forbidden behavior when disabled.
- Public registration cannot create admin accounts.
- Login works with valid credentials and fails with invalid credentials.
- Inactive accounts cannot authenticate or access protected routes.
- Seeded admin can log in.
- Auth tests pass.

### Commit

`feat(backend-auth): add JWT auth registration login and account activity checks`

---

## Phase 6 - Authorization, ownership, CORS, path safety, and security utilities

**Direction:** Backend / Security  
**Goal:** Add reusable authorization and safety primitives before implementing protected product APIs.

### Scope

- Add role-check dependency for admin-only endpoints.
- Add reusable ownership-check helpers for user-owned resources.
- Add account-active enforcement for protected routes.
- Add safe path utilities:
  - relative path validation;
  - path traversal prevention;
  - safe join under `STORAGE_ROOT`;
  - safe download filename handling.
- Add upload filename sanitization helper.
- Add CORS validation using explicit configured origins.
- Add secure error response patterns that do not expose stack traces.
- Add logging helpers/events that omit secrets and tokens.
- Add security tests for unauthorized, forbidden, inactive, ownership, CORS, and path traversal cases.

### Relevant docs

- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Protected test route or existing auth route rejects missing/invalid tokens.
- Admin-only dependency rejects regular users.
- Path traversal attempts fail in utility tests.
- Absolute paths are rejected for database-facing path fields.
- Logs do not include passwords, tokens, secrets, or database passwords in tests or manual inspection.

### Commit

`feat(backend-security): add authorization ownership and path safety utilities`

---

## Phase 7 - Media upload API and metadata extraction

**Direction:** Backend  
**Goal:** Implement media upload, validation, storage, metadata extraction, listing, detail, and soft deletion.

### Scope

- Implement endpoints:
  - `POST /api/media`;
  - `GET /api/media`;
  - `GET /api/media/{media_id}`;
  - `DELETE /api/media/{media_id}`.
- Validate extension, MIME type, file category, size, and filename safety before storage.
- Accept required image and video formats only.
- Generate internal storage paths using user ID and media ID.
- Store original filename only as sanitized display metadata.
- Extract media metadata where feasible:
  - width;
  - height;
  - frame count;
  - FPS;
  - duration.
- Ensure image records use `frame_count = 1`, `fps = null`, and `duration_seconds = null`.
- Enforce user ownership and admin visibility rules.
- Implement soft deletion through `deleted_at` only.
- Add pagination/filtering where useful.
- Add tests for accepted/rejected uploads and ownership.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Valid images upload and create `media_files` records.
- Valid videos upload and create `media_files` records.
- Unsupported extensions, invalid MIME types, oversized files, unsafe filenames, and path traversal attempts are rejected.
- Users see only own media; admins can view broader media metadata.
- Stored paths are generated and relative.
- Soft-deleted media is hidden from normal user lists.

### Commit

`feat(backend-media): add validated media upload and metadata API`

---

## Phase 8 - Model registry backend API

**Direction:** Backend / Admin  
**Goal:** Implement model registry records, active model management, and model path validation.

### Scope

- Implement endpoints:
  - `GET /api/models`;
  - `GET /api/models/{model_id}`;
  - `POST /api/models`;
  - `PATCH /api/models/{model_id}/activate`.
- Allow all authenticated users to view model versions.
- Restrict model registration and activation to admins.
- Register existing relative weights paths under model storage.
- Validate model family: `YOLO26` or documented fallback `YOLO11`.
- Validate `weights_path` as relative and inside model storage.
- Store dataset, split, metrics, variant, and active state metadata.
- Ensure only one model version is active at a time.
- Do not implement large `.pt` upload through the web UI unless explicitly approved later.
- Add tests for role access, active-model uniqueness, and relative paths.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Authenticated users can list models.
- Regular users cannot register or activate models.
- Admin can register a model version using an existing relative path.
- Admin can activate exactly one model version.
- YOLO11 fallback metadata is represented accurately when used.
- Absolute or traversal paths are rejected.

### Commit

`feat(backend-models): add model registry and active model management`

---

## Phase 9 - Job creation API and model selection resolution

**Direction:** Backend  
**Goal:** Implement queued processing job creation with validated parameters and resolved model selection.

### Scope

- Implement `POST /api/jobs`.
- Validate that the media file exists, is not soft-deleted, and belongs to the requesting user.
- Validate processing parameters:
  - `model_version_id` when provided;
  - confidence threshold;
  - IoU threshold;
  - tracker type;
  - internal image size if configured;
  - internal `frame_stride = 1`.
- Resolve model selection priority:
  1. explicit job-specific model version;
  2. active model from `model_versions`;
  3. environment fallback only when no active database model exists.
- Store the resolved `model_version_id` on the job when possible.
- Create job with `status = queued`, input parameters, progress defaults, and ownership fields.
- Ensure long media processing does not happen inside the API request.
- Add tests for own media, another user's media, invalid params, missing active model, and model priority.

### Relevant docs

- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Users can create jobs for own uploaded media.
- Users cannot create jobs for another user's media.
- Invalid model, threshold, IoU, or tracker values are rejected.
- Created job status is `queued`.
- `frame_stride` is present internally but not exposed as a standard user-facing parameter.
- Model selection priority tests pass.

### Commit

`feat(backend-jobs): add queued job creation and model resolution`

---

## Phase 10 - Jobs, results, detections, tracks, and safe downloads API

**Direction:** Backend  
**Goal:** Implement job history, job details, result metadata, detections, tracks, summary, and download endpoints.

### Scope

- Implement endpoints:
  - `GET /api/jobs`;
  - `GET /api/jobs/{job_id}`;
  - `DELETE /api/jobs/{job_id}`;
  - `GET /api/jobs/{job_id}/summary`;
  - `GET /api/jobs/{job_id}/detections`;
  - `GET /api/jobs/{job_id}/tracks`;
  - `GET /api/jobs/{job_id}/result`;
  - `GET /api/jobs/{job_id}/download/media`;
  - `GET /api/jobs/{job_id}/download/csv`;
  - `GET /api/jobs/{job_id}/download/json`.
- Enforce ownership or admin access on every job/result/download route.
- Support pagination and filters for job lists.
- Hide soft-deleted jobs from normal user lists.
- Return status, progress, heartbeat, timestamps, summary, and safe download URLs/references.
- Serve downloads only after verifying that the file belongs to the requested job.
- Return clear missing-file errors without exposing internal paths.
- Treat no-detection completed jobs as successful results.
- Add tests for ownership, downloads, missing result files, and soft deletion/cancellation behavior.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Users list and view only own jobs.
- Admin can view all jobs through allowed permissions/routes.
- Result endpoints enforce ownership.
- Downloads enforce ownership and resource association.
- Absolute filesystem paths are not exposed.
- Completed no-detection jobs can still provide CSV/JSON downloads when files exist.
- Backend tests pass.

### Commit

`feat(backend-results): add jobs results detections tracks and downloads API`

---

## Phase 11 - Admin backend APIs and safe storage cleanup

**Direction:** Backend / Admin  
**Goal:** Implement admin-only global statistics, global history, basic user list, and conservative storage cleanup.

### Scope

- Implement endpoints:
  - `GET /api/admin/stats`;
  - `GET /api/admin/jobs`;
  - `GET /api/admin/users`;
  - `POST /api/admin/storage/cleanup`.
- Enforce admin role explicitly on all admin endpoints.
- Provide global processing statistics and recent global job history.
- Provide basic user list without password hashes or sensitive fields.
- Implement conservative cleanup rules.
- Cleanup must not remove:
  - active model weights;
  - model cards for active models;
  - files referenced by non-deleted records;
  - recent user results accidentally;
  - files needed by visible completed jobs.
- Log cleanup actions safely.
- Add admin/regular-user access tests and cleanup safety tests.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Regular users cannot access admin routes.
- Admin can view global stats, jobs, and basic users.
- Cleanup dry-run or conservative mode works if implemented.
- Cleanup does not delete referenced files or active model artifacts.
- Admin endpoint tests pass.

### Commit

`feat(backend-admin): add admin stats users jobs and safe storage cleanup`

---

## Phase 12 - Experiment import backend API

**Direction:** Backend / Admin / Experiments  
**Goal:** Implement imported experiment records and metrics without launching training from the app.

### Scope

- Implement endpoints:
  - `GET /api/experiments`;
  - `GET /api/experiments/{experiment_id}`;
  - `POST /api/experiments/import`.
- Restrict experiment import to admins.
- Regular users can view only published experiment runs.
- Admins can view all imported experiment runs.
- Support required experiment types:
  - model comparison;
  - confidence threshold analysis;
  - tracker behavior comparison;
  - false-positive analysis.
- Import structured metrics and artifact paths from existing files under storage.
- Allow `metric_value = null` for incomplete imports.
- Validate artifact paths as relative and safe.
- Ensure API and UI-facing data use tracker behavior wording, not absolute tracking accuracy.
- Add tests for import, published visibility, null metrics, role access, and path safety.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/FRONTEND_UX.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Admin can import experiment metadata and metrics.
- Regular users see only published experiments.
- Admins see unpublished experiments.
- Null metric values do not break API responses.
- Training cannot be launched from API routes.
- Experiment tests pass.

### Commit

`feat(backend-experiments): add experiment import and visibility API`

---

## Phase 13 - Backend contract, pagination, OpenAPI, and security test audit

**Direction:** Backend / QA  
**Goal:** Consolidate backend API behavior before worker and frontend implementation depend on it.

### Scope

- Audit all implemented endpoint paths against `API.md`.
- Ensure `/api` prefix is consistent.
- Ensure OpenAPI schemas are usable for frontend development.
- Normalize error response shapes for frontend Ukrainian localization.
- Ensure paginated list endpoints are consistent.
- Re-run auth, authorization, ownership, upload, model, job, result, admin, and experiment tests.
- Add missing tests for edge cases discovered during audit.
- Confirm API outputs do not expose absolute filesystem paths or forbidden CV-boundary fields.
- Update README/API notes with current commands and endpoint groups.

### Relevant docs

- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`

### Validation

- Backend lint/format/type-equivalent checks pass.
- Backend test suite passes.
- Manual OpenAPI route audit passes.
- Protected routes consistently reject missing/invalid tokens.
- Regular users cannot bypass ownership through filters or IDs.
- API/export boundary audit passes for implemented responses.

### Commit

`test(backend): audit API contract security and ownership coverage`

---

## Phase 14 - CV worker scaffold, settings, logging, and database access

**Direction:** CV Worker  
**Goal:** Create the separate worker service foundation without implementing full inference yet.

### Scope

- Scaffold `cv/` Python project.
- Add dependencies for SQLAlchemy, PostgreSQL driver, Pydantic settings, PyTorch/Ultralytics placeholder, OpenCV headless, NumPy, pandas, and tests.
- Implement worker settings for database, storage, device, polling, heartbeat, stale-job threshold, and max retries.
- Implement safe logging that does not expose secrets or absolute paths in user-facing messages.
- Implement database session layer for worker.
- Implement startup logs including selected/desired `CV_DEVICE` configuration.
- Implement storage path resolution under `/app/storage` using relative paths from the database.
- Add worker Dockerfile and Compose integration.
- Add basic worker health/startup smoke tests where practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Worker container starts in Docker Compose.
- Worker logs selected device configuration on startup.
- Worker can connect to PostgreSQL.
- Worker can resolve safe relative storage paths.
- Worker does not call backend over HTTP for job polling.
- Worker smoke tests pass.

### Commit

`feat(worker): scaffold CV worker settings logging and database access`

---

## Phase 15 - PostgreSQL queue claiming, heartbeat, and stale job recovery

**Direction:** CV Worker / Queue  
**Goal:** Implement reliable PostgreSQL job queue behavior before media processing.

### Scope

- Implement polling loop for queued jobs.
- Implement job claiming with `FOR UPDATE SKIP LOCKED`.
- Keep claim transaction short.
- Set `status = processing`, `locked_by`, `locked_at`, `started_at`, and `last_heartbeat_at` during claim.
- Ensure processing happens outside the claim transaction.
- Implement heartbeat/progress update helpers.
- Implement stale job recovery:
  - detect stale `processing` jobs;
  - reset to `queued` and increment `retry_count` when retry count is below max;
  - mark as `failed` when retry count reaches max.
- Add tests or integration tests showing two workers cannot claim the same job.
- Add worker shutdown behavior as practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Worker claims oldest queued job.
- Two workers do not claim the same job.
- Claim transaction is not held during simulated processing.
- Heartbeat/progress updates work.
- Stale jobs reset or fail according to retry count.
- Worker restart does not leave jobs permanently stuck in `processing`.

### Commit

`feat(worker-queue): add Postgres job claiming heartbeat and stale recovery`

---

## Phase 16 - CV model loading, device selection, and model cache

**Direction:** CV Worker / CV Runtime  
**Goal:** Implement model selection, model loading, device selection, and safe fallback/error behavior.

### Scope

- Implement runtime model selection using the resolved `processing_jobs.model_version_id`.
- Load weights from relative model storage paths.
- Implement in-memory model cache when practical.
- Reload or switch models when a job requires a different model version.
- Implement `CV_DEVICE` handling:
  - `auto` uses CUDA when available, otherwise CPU;
  - `cpu` forces CPU;
  - `cuda` fails clearly when CUDA is unavailable.
- Log model loading and selected runtime device.
- Fail jobs safely when weights file is missing.
- Preserve YOLO26 as primary and YOLO11 as documented fallback only.
- Add tests for path validation, missing weights, device selection, and model priority assumptions.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Worker loads a configured model from a relative path when weights exist.
- Missing model file marks job failed with safe error message.
- `CV_DEVICE=cpu` works.
- `CV_DEVICE=auto` falls back to CPU if CUDA is unavailable.
- `CV_DEVICE=cuda` fails clearly if CUDA is unavailable.
- Model loading logs do not expose unsafe paths or secrets.

### Commit

`feat(worker-models): add model loading device selection and cache`

---

## Phase 17 - Image processing pipeline

**Direction:** CV Worker / Image Processing  
**Goal:** Implement end-to-end image job processing.

### Scope

- Read uploaded image from shared storage.
- Validate readable image/decode result at worker level.
- Run YOLO inference on the image.
- Convert detections to original-resolution pixel coordinates.
- Store detection rows with:
  - `frame_index = 0`;
  - `timestamp_ms = 0`;
  - `track_id = null`.
- Write annotated image output under `results/{job_id}/`.
- Calculate image processing summary metrics.
- Update job result path, summary, progress, and status.
- Handle corrupted images, missing files, and failed output creation.
- Complete no-detection image jobs successfully.
- Add image processing tests using mocks or small fixtures.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Image job completes successfully.
- Annotated image is created when possible.
- Detection rows use original-resolution pixel coordinates.
- Image detections use `frame_index = 0`, `timestamp_ms = 0`, and `track_id = null`.
- No-detection image job completes with zero detections.
- Result paths are relative.
- Worker tests pass.

### Commit

`feat(worker-image): add image detection processing pipeline`

---

## Phase 18 - Video processing and tracking pipeline

**Direction:** CV Worker / Video Processing  
**Goal:** Implement end-to-end video job processing with progress updates and tracking.

### Scope

- Read uploaded video from shared storage.
- Validate readable video/decode result at worker level.
- Read or verify video metadata: frame count, FPS, width, height, duration when available.
- Process frames in order.
- Run YOLO detection frame by frame.
- Apply ByteTrack by default for video tracking.
- Support BoT-SORT as an alternative when runtime support is available.
- Write annotated frames to output video, preferably MP4.
- Update progress and heartbeat every configured frame/time interval.
- Store detection rows with frame indices and timestamps in milliseconds.
- Store track IDs when the tracker provides them.
- Create track summary rows per job/track ID.
- Calculate average FPS, processing duration, confidence summaries, and video metrics.
- Handle missing/corrupted videos and failed output media creation safely.
- Complete no-detection video jobs successfully.
- Add video processing tests using small fixtures, mocks, or smoke assets.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Video job completes successfully.
- Progress and heartbeat update during processing.
- Annotated video is created or a safe downloadable result is available.
- Detections include frame indices and timestamps.
- Track IDs are stored when available and may be null when not associated.
- Track summaries are created for video jobs with tracks.
- Average FPS and processing duration are calculated.
- No-detection video job completes successfully.

### Commit

`feat(worker-video): add video detection tracking and progress pipeline`

---

## Phase 19 - Worker CSV/JSON exports and no-detection contracts

**Direction:** CV Worker / Exports  
**Goal:** Generate CSV and JSON exports exactly according to API/export contracts.

### Scope

- Generate CSV export with one row per detection.
- Include required CSV columns:
  - job/media/frame/timestamp fields;
  - class/confidence fields;
  - bounding box corner fields;
  - derived center-size fields;
  - frame dimensions;
  - track ID;
  - model version;
  - tracker type.
- Generate JSON export with top-level:
  - `job`;
  - `media`;
  - `model`;
  - `parameters`;
  - `summary`;
  - `detections`;
  - `tracks`.
- Generate headers-only CSV for no-detection jobs.
- Generate JSON with empty `detections` array for no-detection jobs.
- Store `csv_path` and `json_path` as relative paths.
- Keep exports inside allowed CV output boundary only.
- Add export contract tests.

### Relevant docs

- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/TESTING_QA.md`

### Validation

- CSV export contains all required columns.
- JSON export contains all required top-level objects/arrays.
- Derived values are computed correctly from corner coordinates.
- No-detection CSV has headers only.
- No-detection JSON has empty `detections` array.
- Exports do not include forbidden physical-control, targeting, geolocation, or engagement fields.
- Export tests pass.

### Commit

`feat(worker-exports): add CSV JSON exports and no-detection contracts`

---

## Phase 20 - Worker error handling, logging, and integration hardening

**Direction:** CV Worker / QA  
**Goal:** Harden worker behavior before connecting frontend flows.

### Scope

- Audit worker failure handling for:
  - missing uploaded file;
  - corrupted image;
  - corrupted video;
  - unsupported decode result;
  - missing model file;
  - CUDA unavailable;
  - failed annotated output write;
  - failed export generation;
  - database write failures.
- Store safe `error_message` for failed jobs.
- Keep stack traces in worker logs only, not unsafe API responses.
- Ensure successful jobs set `completed_at` and final progress.
- Ensure failed jobs set `status = failed` and updated timestamp.
- Ensure no-detection jobs are never marked failed solely because no detections were found.
- Add logging tests or manual log audit checklist.
- Add worker integration tests with backend-created jobs where practical.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Failure cases produce safe job error messages.
- No-detection jobs still complete.
- Worker logs include device selection, job claim, model loading, processing start/end, exports, and errors.
- Worker logs do not include secrets or unsafe user-facing absolute paths.
- Worker test suite passes.

### Commit

`test(worker): harden CV worker errors logging and integration behavior`

---

## Phase 21 - Training pipeline scripts, notebooks, dataset preparation, and model cards

**Direction:** Training / Offline CV  
**Goal:** Create the offline training workflow artifacts without launching training from the web application.

### Scope

- Create training scripts for dataset preparation and YOLO-compatible structure.
- Create deterministic split script with seed `42`.
- Prefer group-based splitting when source/sequence/video grouping metadata exists.
- Generate `split_manifest.csv` with required columns.
- Create `data.yaml` for one class: `drone`.
- Create Kaggle/Colab notebooks or notebook templates for YOLO26n and YOLO26s fine-tuning.
- Add local smoke training option for tiny subset only.
- Add model card schema and metrics schema.
- Save expected artifacts layout under `storage/models/`.
- Document human responsibilities for running cloud training and placing artifacts.
- Document YOLO11 fallback procedure and required metadata if YOLO26 is unavailable.
- Ensure scripts do not commit datasets or weights.

### Relevant docs

- `docs/TRAINING_EXPERIMENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`

### Validation

- Dataset split script runs on a small fixture.
- Split manifest includes required columns.
- `data.yaml` defines exactly one class: `drone`.
- Model card schema validates placeholder/null metrics.
- Training README clearly states that web UI/API do not launch training.
- Large datasets and weights remain ignored by Git.

### Commit

`feat(training): add dataset split notebooks and model card workflow`

---

## Phase 22 - Model artifact registration and experiment artifact import utilities

**Direction:** Backend / Training Integration  
**Goal:** Bridge offline training artifacts into backend model registry and experiment import flows.

### Scope

- Add script or CLI helper to register a model version from `model_card.json` and relative weights path.
- Add script or CLI helper to import experiment metrics/artifacts from structured files.
- Validate model cards and metrics schemas before insertion.
- Ensure imported model paths and report artifact paths are relative.
- Support placeholder/null metric values for pre-training or incomplete imports.
- Ensure YOLO11 fallback is recorded accurately when used.
- Add documentation for the artifact registration workflow:
  1. human trains in Kaggle/Colab;
  2. human downloads weights/metrics/model card;
  3. human places artifacts under storage;
  4. admin or helper registers model;
  5. admin activates model;
  6. admin imports experiments.
- Add tests for CLI/helper validation and idempotent imports if supported.

### Relevant docs

- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Valid model card registers a model version.
- Invalid or absolute weights paths are rejected.
- Valid experiment artifact imports run and metrics are queryable.
- Re-running idempotent import does not create unintended duplicates when idempotency is documented.
- README/training docs clearly describe the offline-to-app workflow.

### Commit

`feat(training-import): add model and experiment artifact registration helpers`

---

## Phase 23 - Backend-worker end-to-end integration smoke

**Direction:** Backend / CV Worker / QA  
**Goal:** Verify that backend-created jobs are processed by the worker and returned through the API.

### Scope

- Run clean database and shared storage with backend and worker.
- Upload a valid image through backend API.
- Create a processing job through backend API.
- Let worker claim and process the job.
- Verify job details, summary, detections, tracks, result metadata, and downloads through backend API.
- Repeat for a valid video fixture when feasible.
- Verify no-detection fixture behavior.
- Verify failed-job behavior for corrupted media or missing model file.
- Verify ownership restrictions for results and downloads.
- Add integration smoke scripts or pytest markers as practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Image upload -> job -> worker -> result -> download flow works.
- Video upload -> job -> worker -> result -> download flow works or blocker is documented with exact command/log.
- No-detection flow completes successfully.
- Another user cannot access job details or downloads.
- CSV and JSON exports are downloadable.
- CPU mode works.

### Commit

`test(integration): verify backend worker media processing flow`

---

## Phase 24 - Frontend scaffold, API client, auth, and protected routing

**Direction:** Frontend  
**Goal:** Create the React frontend foundation after backend contracts are stable.

### Scope

- Scaffold `frontend/` with Vite, React, TypeScript.
- Add Tailwind CSS and shadcn/ui baseline.
- Add React Router, TanStack Query, React Hook Form/Zod if used for forms, Recharts, and supporting UI libraries.
- Add frontend folder structure for app shell, routes, features, shared components, API client, and utilities.
- Add typed API client for `/api` endpoints.
- Add auth token storage strategy and logout behavior.
- Implement current-user query and auth state.
- Implement protected route wrapper.
- Implement admin route guard.
- Implement `/login` and `/register` pages.
- Map backend errors to Ukrainian UI messages.
- Ensure public registration disabled state redirects or shows Ukrainian notice.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Frontend install succeeds.
- Frontend lint/typecheck/build pass.
- Login page renders in Ukrainian.
- Registration page renders in Ukrainian and handles disabled-registration behavior.
- Protected routes redirect guests to login.
- Non-admin users cannot access `/admin` route.
- Auth smoke flow works against backend.

### Commit

`feat(frontend): scaffold React app auth and protected routing`

---

## Phase 25 - Frontend dashboard and authenticated shell

**Direction:** Frontend  
**Goal:** Implement the dashboard-style authenticated layout and main dashboard.

### Scope

- Implement responsive authenticated shell/navigation.
- Add navigation items:
  - Dashboard;
  - Upload;
  - Jobs;
  - Models;
  - Experiments;
  - Admin only for admins.
- Hide authenticated navigation from guests.
- Hide admin navigation from regular users.
- Implement `/dashboard`.
- Display:
  - total processed files;
  - total detections;
  - average confidence;
  - average FPS;
  - active model;
  - recent processing jobs;
  - quick upload action.
- Use cards, badges, tables, skeletons, and polished dashboard components.
- Handle missing data gracefully and never show raw `null`.
- Keep all visible UI text Ukrainian.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Dashboard route is protected.
- Regular user dashboard shows user-scoped data.
- Admin dashboard can show global statistics where backend supports it.
- Missing data renders Ukrainian empty/placeholder states.
- Admin navigation is visible only to admins.
- Frontend build passes.

### Commit

`feat(frontend-dashboard): add Ukrainian shell navigation and dashboard`

---

## Phase 26 - Frontend upload and processing page

**Direction:** Frontend  
**Goal:** Implement media upload and processing-job creation UI.

### Scope

- Implement `/upload` page.
- Add drag-and-drop file upload.
- Show allowed file types and size guidance in Ukrainian.
- Show selected file preview or metadata where practical.
- Add model selector populated from backend.
- Add confidence threshold control.
- Add IoU threshold control.
- Add tracker selector for video jobs.
- Do not expose `frame_stride` in standard UI.
- Preselect defaults so users can process without changing settings.
- Create media upload request.
- Create processing job request.
- Show job status/progress block after job creation:
  - status badge;
  - progress bar;
  - percentage when available;
  - last update time when available.
- Add Ukrainian loading, error, success, and validation messages.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Upload page route is protected.
- Valid file can be uploaded.
- Job can be created with defaults.
- Invalid file, too-large file, unsupported type, and failed job creation show Ukrainian errors.
- `frame_stride` is not visible.
- Status block renders queued/processing/completed/failed states.
- Frontend build passes.

### Commit

`feat(frontend-upload): add media upload and processing creation flow`

---

## Phase 27 - Frontend jobs history and job details pages

**Direction:** Frontend  
**Goal:** Implement job list, filters, status polling, details, detections/tracks, previews, and downloads.

### Scope

- Implement `/jobs` page.
- Add jobs table with:
  - status badge;
  - media type;
  - original filename;
  - model version;
  - created date;
  - processing duration;
  - detections count;
  - average confidence;
  - link to details.
- Add filters for status, media type, date, and model where practical.
- Implement `/jobs/:jobId` page.
- Show job status, media metadata, summary cards, progress, heartbeat/update time, and failed-job error area.
- Poll job status while queued or processing.
- Show processed media preview when possible.
- If processed video preview is unavailable, show Ukrainian notice and keep download button.
- Add detection table with frame index, timestamp, class, confidence, bounding box, and track ID.
- Add track summary table for videos.
- Add download buttons for annotated media, CSV, and JSON.
- Handle completed no-detection jobs with Ukrainian empty state, not error.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Jobs page shows only current user's jobs for regular users.
- Status badges use Ukrainian visible text.
- Queued/processing jobs poll and update UI.
- Completed jobs show summaries and tables.
- Failed jobs show safe Ukrainian error messages.
- No-detection jobs show empty state and keep downloads when available.
- Downloads work from UI.
- Frontend build passes.

### Commit

`feat(frontend-jobs): add jobs history details polling and downloads`

---

## Phase 28 - Frontend model registry page

**Direction:** Frontend  
**Goal:** Implement model list and admin model-management actions.

### Scope

- Implement `/models` page.
- Display registered model versions with:
  - model name;
  - family;
  - variant;
  - active status;
  - dataset description;
  - key metrics;
  - model size when known.
- Allow regular users to view models only.
- Show admin-only actions only to admins:
  - register model;
  - activate model.
- Add admin model registration form using existing relative storage paths.
- Add activation flow and active-status update.
- Render missing metric values as Ukrainian placeholders or empty states, not raw `null`.
- Represent YOLO26 and documented YOLO11 fallback accurately.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Authenticated users can view model list.
- Regular users do not see admin mutation actions.
- Admin can register and activate model versions.
- Active model is visually clear.
- Missing metrics do not show raw `null`.
- Frontend build passes.

### Commit

`feat(frontend-models): add model registry page and admin actions`

---

## Phase 29 - Frontend experiments and metrics page

**Direction:** Frontend  
**Goal:** Implement experiment visualization with robust empty states.

### Scope

- Implement `/experiments` page.
- Display:
  - model comparison table;
  - confidence threshold analysis chart;
  - tracker behavior comparison table;
  - false-positive analysis summary;
  - precision/recall/mAP cards;
  - FPS/latency chart;
  - confusion matrix image if available.
- Use Recharts for frontend charts.
- Do not use Matplotlib in frontend UI.
- Use the exact Ukrainian empty-state text for missing experiment sections:

```text
Дані експерименту ще не завантажено
```

- Do not render blank chart canvases without explanation.
- Do not show raw `null` values.
- Regular users see published experiments only.
- Admins can see all experiments where backend allows it.
- Use wording `tracker behavior comparison`, not absolute tracking accuracy.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`

### Validation

- Experiments route is protected.
- Missing data shows required Ukrainian text.
- Null metric values do not crash the UI.
- Recharts render when data exists.
- Regular user/admin visibility matches backend.
- Frontend build passes.

### Commit

`feat(frontend-experiments): add experiment metrics and empty states`

---

## Phase 30 - Frontend admin page

**Direction:** Frontend / Admin  
**Goal:** Implement admin-only UI for global stats, global jobs, users, shortcuts, and cleanup.

### Scope

- Implement `/admin` page.
- Restrict route to admin users in frontend routing.
- Display global processing statistics.
- Display recent jobs from all users.
- Display model management shortcuts.
- Display safe storage cleanup action.
- Display basic users table.
- Do not implement complex user management unless explicitly approved later.
- Add Ukrainian loading, error, empty, and success states.
- Ensure backend remains the source of truth for authorization.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Admin navigation appears only for admins.
- Regular users cannot access `/admin`.
- Admin page loads global stats/jobs/users.
- Cleanup action is clear and conservative in UI wording.
- Empty lists show Ukrainian empty states.
- Frontend build passes.

### Commit

`feat(frontend-admin): add admin dashboard and cleanup UI`

---

## Phase 31 - Frontend Ukrainian UX, responsive polish, and scope audit

**Direction:** Frontend / QA  
**Goal:** Make the frontend coherent, Ukrainian, polished, responsive, and within documented scope.

### Scope

- Audit all user-facing text for Ukrainian language.
- Ensure accepted technical labels such as `FPS`, `mAP`, `YOLO`, `CSV`, and `JSON` remain readable.
- Standardize status badges, buttons, forms, tables, cards, charts, skeletons, toasts, and empty states.
- Standardize date, duration, confidence, percentage, and bounding-box formatting.
- Ensure raw `null` is never displayed.
- Ensure absolute filesystem paths are never displayed.
- Ensure `frame_stride` is not visible in standard UI.
- Ensure admin buttons and navigation are hidden from regular users.
- Ensure no frontend text presents CV outputs as targeting, navigation, or interception instructions.
- Verify responsiveness for desktop and laptop screens, and reasonable behavior on narrower screens.
- Add or update frontend tests where practical.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Frontend lint/typecheck/build pass.
- Manual route smoke passes for login, registration, dashboard, upload, jobs, job details, models, experiments, and admin.
- Ukrainian UX audit passes.
- No out-of-scope UI actions are visible.
- Empty, loading, error, forbidden, and no-detection states are clear.

### Commit

`style(frontend): polish Ukrainian dashboard UX and scope boundaries`

---

## Phase 32 - Final Docker runtime, GPU override, README, and first-launch flow

**Direction:** DevOps / Documentation  
**Goal:** Make the complete application launchable and understandable from a clean local setup.

### Scope

- Finalize `docker-compose.yml` for:
  - `postgres`;
  - `backend`;
  - `cv-worker`;
  - `frontend`.
- Finalize optional GPU override/profile for `cv-worker` only.
- Ensure backend startup can run migrations and seed/setup in local/demo mode.
- Ensure storage directories are created or verified.
- Ensure frontend connects to backend through Docker/local configuration.
- Ensure backend and worker share the same storage mount path.
- Ensure worker waits for or retries database availability.
- Add service health checks where practical.
- Add Makefile or script shortcuts for:
  - local setup;
  - migration;
  - seed;
  - logs;
  - tests;
  - CPU launch;
  - optional GPU launch.
- Update README with:
  - prerequisites;
  - `.env` setup;
  - model artifact placement/registration;
  - one-command startup;
  - seeded admin credentials policy;
  - CPU/GPU notes;
  - troubleshooting;
  - large-file/Git policy.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`
- all implementation docs

### Validation

- `docker compose config` succeeds.
- `docker compose up --build` starts all base services in CPU mode after documented setup.
- Backend migrations apply automatically in local/demo mode.
- Idempotent seed/setup runs automatically in local/demo mode.
- Seeded admin exists.
- Frontend is reachable in the browser.
- Backend health endpoints work.
- Worker logs selected device.
- Only `cv-worker` requests GPU in GPU configuration.
- README startup instructions are accurate.

### Commit

`chore(runtime): finalize Docker Compose startup and first-launch docs`

---

## Phase 33 - Final full-stack QA, security audit, and release readiness

**Direction:** QA / Release  
**Goal:** Verify the complete MVP against documented acceptance criteria.

### Scope

- Run backend tests.
- Run worker tests.
- Run frontend lint/typecheck/build/tests where configured.
- Run clean-volume Docker startup smoke.
- Execute manual E2E scenarios:
  - regular user image processing;
  - regular user video processing;
  - no-detection result;
  - admin model management;
  - admin experiments;
  - stale job recovery.
- Verify authentication and public registration toggle.
- Verify seeded admin login.
- Verify authorization and ownership for media, jobs, results, and downloads.
- Verify upload validation and path traversal rejection.
- Verify model selection priority.
- Verify CSV and JSON export contracts.
- Verify frontend Ukrainian text, loading states, error states, and empty states.
- Verify admin-only features are protected.
- Verify logs do not contain secrets or tokens.
- Verify API responses and exports remain inside the CV-only boundary.
- Audit absent out-of-scope features.
- Update final README and known limitations.

### Relevant docs

- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/FRONTEND_UX.md`
- all implementation docs

### Validation

- `docker compose up --build` reaches a usable app after documented setup.
- PostgreSQL, backend, CV worker, frontend, migrations, seed/setup, and storage initialization work together.
- Seeded admin can log in.
- Public registration works when enabled and is forbidden when disabled.
- User can upload and process image and video files.
- Worker reliably moves jobs from queued to processing to completed/failed.
- Progress updates during video processing.
- No-detection jobs complete successfully.
- Result media, CSV, and JSON downloads work.
- Admin model and experiment flows work.
- Ukrainian UI audit passes.
- Security and safety boundary audits pass.
- Remaining failures, if any, are documented as blockers with exact commands/logs.

### Commit

`chore(release): complete full-stack QA and release readiness audit`

---

# Final acceptance definition

The Drone Computer Vision Subsystem is complete when:

- The app starts with `docker compose up --build` after documented `.env` setup and required local model artifacts.
- PostgreSQL, FastAPI backend, CV worker, React frontend, migrations, seed/setup, and storage initialization work together.
- The base app supports CPU inference; optional GPU mode is isolated to `cv-worker`.
- Backend health and database health endpoints work.
- Worker starts, connects to PostgreSQL, and logs selected device.
- Backend and worker mount the same shared storage volume at `/app/storage`.
- Alembic migrations run automatically in local/demo startup when enabled.
- Idempotent setup creates the seeded admin from environment variables.
- Public registration works when enabled and is forbidden when disabled.
- Registration always creates `user` accounts only.
- Seeded admin can log in.
- JWT authentication protects required routes.
- Inactive accounts cannot authenticate or use protected routes.
- Regular users can upload only validated image/video files.
- Upload validation rejects unsupported extension, invalid MIME, oversized file, unsafe filename, path traversal, and user-submitted storage path attempts.
- Users can create queued jobs only for their own media.
- Job creation validates model version, confidence threshold, IoU threshold, and tracker type.
- `frame_stride` defaults internally to `1` and is not exposed in the standard UI.
- Model selection priority is respected: job-specific model, then database active model, then environment fallback only when no active database model exists.
- CV worker claims queued jobs using PostgreSQL row-level locking and does not hold transactions open during media processing.
- Worker heartbeat, progress updates, retry count, and stale job recovery work.
- Image processing creates annotated output, detection rows, summary metrics, CSV export, and JSON export.
- Video processing creates annotated/downloadable output, detection rows, track summaries when available, progress updates, summary metrics, CSV export, and JSON export.
- Bounding boxes are stored and exported in original-resolution image-space pixel coordinates.
- Image detections have `frame_index = 0`, `timestamp_ms = 0`, and `track_id = null`.
- Video detections include frame indices, timestamps in milliseconds, and track IDs when the tracker provides them.
- No-detection jobs complete successfully with zero detections, headers-only CSV, JSON with empty `detections`, and Ukrainian empty states in the UI.
- Result downloads enforce ownership or admin access and never expose absolute filesystem paths.
- Regular users see only their own media, jobs, results, downloads, and user-scoped statistics.
- Admins can view global history/statistics, basic users list, all imported experiments, and admin-only model/storage actions.
- Regular users cannot register/activate models, import experiments, access admin routes, or download another user's results.
- Model registry supports registered model versions, active model selection, YOLO26 metadata, and documented YOLO11 fallback metadata when used.
- Experiment import supports model comparison, threshold analysis, tracker behavior comparison, and false-positive analysis.
- Training is never launched from the web UI or API.
- Frontend routes exist for `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`.
- Protected frontend routes redirect unauthenticated users to login.
- Admin frontend navigation and actions are visible only to admins.
- Frontend UI is Ukrainian for visible labels, buttons, validation messages, statuses, empty states, errors, table headings where practical, and toasts.
- Recharts are used for frontend charts.
- Experiment sections with no data show exactly: `Дані експерименту ще не завантажено`.
- The UI does not display raw `null` values or absolute filesystem paths.
- The UI looks like a polished dashboard application, not a raw debug panel.
- Passwords are hashed and never stored or logged in plain text.
- JWT secrets, tokens, database passwords, admin password, and sensitive environment values are not logged or exposed.
- CORS uses configured explicit origins and does not use wildcard origins in non-local configurations.
- User-uploaded files are never executed.
- Large datasets, weights, uploads, processed media, generated results, and reports are not committed to Git.
- API responses, CSV exports, JSON exports, frontend screens, and logs remain within the CV-only boundary.
- The system does not implement physical interception, flight control, navigation, hardware control, aiming, payload, engagement decisions, trajectory planning, geospatial targeting, RTSP/webcam/live processing, Celery/Redis queue, Streamlit app, Flask backend, model training from UI, or complex RBAC beyond `user` and `admin`.
