# AGENTS.md - AeroVision Drone Computer Vision Subsystem

## Role

Codex is the primary implementation, verification, review-resolution, and final-fix agent for the AeroVision Drone Computer Vision Subsystem. Work from the documentation in `docs/` and do not redesign the product during implementation.

This file is agent operating guidance, not product specification. Product details stay in `docs/`; this file defines workflow, source-of-truth order, command policy, quality gates, and repeated engineering rules.

## Project Frame

- AeroVision is a Dockerized full-stack web application for detecting and visually tracking drones in uploaded images and video files.
- The system is a computer-vision-only subsystem. It must output image-space detections, tracking IDs, model data, exports, and performance metrics only.
- The backend exposes the REST API, enforces auth/roles/ownership, validates uploads and processing parameters, persists structured records in PostgreSQL, and serves safe downloads.
- The CV worker processes queued jobs through PostgreSQL and shared storage, writes annotated media and CSV/JSON exports, and records detections, tracks, summaries, progress, and errors.
- The frontend is a Ukrainian-language React + TypeScript interface that calls only the backend REST API.
- Training is performed outside the running app in cloud notebooks such as Kaggle or Google Colab. The app imports or registers resulting artifacts; it does not launch training.
- The system must be runnable locally through Docker Compose after documented setup and required local model artifacts.
- The project is not an interception, targeting, navigation, autopilot, hardware-control, RTSP/live-camera, Streamlit, Flask, Celery, or Redis project in the MVP.

## Repository Shape and Stack

Expected project areas:

```text
backend/
frontend/
cv/
training/
docs/
AGENTS.md
CLAUDE.md
```

Deployment files may live at the repository root or in a documented deployment folder when implemented. Do not create new top-level folders unless the docs or the user explicitly require them.

Fixed stack:

- Backend: Python, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL, JWT access tokens, bcrypt or Argon2 password hashing.
- Frontend: React, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Recharts.
- CV worker: Python, PyTorch, Ultralytics YOLO, `opencv-python-headless`, NumPy, pandas, ByteTrack by default for video tracking.
- Training utilities: Python scripts/notebooks/configs for cloud-notebook training, dataset preparation, model cards, metrics, and artifact import.
- Runtime: Docker Compose with `postgres`, `backend`, `cv-worker`, and `frontend`.
- Persistence: PostgreSQL for structured records only; filesystem shared storage for uploads, results, reports, models, temp files, and datasets.

Do not replace the stack without an explicit user-approved architecture decision.

## Source of Truth and Conflicts

Use `docs/index.md` for navigation. Do not copy endpoint contracts, schema details, permission matrices, upload rules, CV pipeline details, training policies, page specs, or deployment procedures into implementation files. Read the authoritative document when work touches that surface.

Precedence:

1. Current user instruction.
2. Product docs in `docs/`.
3. `.context/` contracts and resolutions when doc-consistent.
4. `AGENTS.md` and `CLAUDE.md`.
5. Existing code patterns when doc-consistent.

If `.context/` or current code conflicts with product docs, stop and report `WARNING: CONFLICT` with exact files and rules.

## Source-of-Truth Map

| Need | Read |
|---|---|
| Product identity, MVP scope, non-goals, stack, CV-only boundary, documentation map | `docs/PROJECT_CONTEXT.md` |
| Component boundaries, data flow, state ownership, shared storage, job queue, deployment topology | `docs/ARCHITECTURE.md` |
| PostgreSQL entities, constraints, indexes, soft deletion, path rules, model-selection data | `docs/DATA_MODEL.md` |
| REST endpoints, access matrix, errors, downloads, CSV/JSON exports, output boundary | `docs/API.md` |
| Auth, roles, account activity, public registration, seeded admin, uploads, CORS, logging | `docs/AUTH_SECURITY.md` |
| Runtime image/video processing, YOLO policy, tracking, no-detection behavior, worker errors | `docs/CV_PIPELINE.md` |
| Cloud training, datasets, model cards, experiment metrics, artifact import | `docs/TRAINING_EXPERIMENTS.md` |
| Frontend routes, Ukrainian UI, dashboard, charts, role-based views, empty/loading/error states | `docs/FRONTEND_UX.md` |
| Test strategy, integration checks, security checks, manual E2E scenarios | `docs/TESTING_QA.md` |
| Phase order and implementation checkpoints | `docs/ROADMAP.md` |

## Workflow Contract

Before implementation:

1. Read `AGENTS.md`, `CLAUDE.md`, and `docs/index.md`.
2. Read the docs relevant to the touched surface.
3. Read relevant `.context/` planning, design, status, and review-resolution artifacts if present.
4. Check repository state with `git status --short` when this checkout is a Git repository.
5. Keep the change scoped to the requested surface and current documentation.

During implementation:

- Follow the roadmap phase order unless the user explicitly scopes a different task.
- Announce meaningful steps as `[@role/name] Step N - description` when following a phase plan that assigns roles.
- Keep changes minimal and documentation-consistent.
- Do not implement later or unrelated functionality.
- Do not commit unless the user explicitly asks.
- Do not overwrite user changes.
- Keep the backend as the authorization authority.
- Keep the frontend away from PostgreSQL, shared storage internals, and direct CV inference.
- Keep the CV worker free of REST API ownership and frontend responsibilities.
- Keep training outside the running web application.

When resolving reviews:

- Resolve every issue as `accepted`, `rejected`, `duplicate`, or `needs user decision`.
- Apply only accepted fixes.
- Reject items that conflict with product docs.
- Stop before source changes when a blocking issue needs a user decision.
- Update `.context/review-code-resolution.md` and `.context/status.md` when those files are part of the workflow.

## Command Policy

Use plain project commands unless a local wrapper is verified to preserve behavior.

Prefer `rg` or `rg --files` for searches. Use plain Git commands only when this checkout is a Git repository. If a command or scaffold does not exist yet, report `not available yet`, not `PASS`.

Do not run formatters, generators, migrations, or codegen that rewrite repo-tracked files unless the task explicitly requires it.

## Agent Roles

Plan steps should use one or more of these roles.

### `@role/developer-backend`

FastAPI application, REST routes, request/response schemas, job creation, result/download routes, model and experiment APIs, admin APIs, auth integration, backend tests, and backend runtime wiring.

- Keep route handlers thin; put business rules in services/domain helpers.
- Backend is the public API and authorization authority.
- API paths, error shapes, auth behavior, downloads, and export responses must match `docs/API.md`.
- Long media processing must not run inside upload or job-creation requests.
- Do not let malformed, unauthorized, or cross-owner requests create jobs or expose results.

### `@role/developer-db`

PostgreSQL schema, Alembic migrations, seed/setup logic, database constraints, indexes, persistence helpers, and database tests.

- PostgreSQL stores structured records and metadata only.
- Store media files, result media, exports, reports, datasets, and model weights in filesystem storage, not PostgreSQL.
- Store database file references as relative paths only.
- Use documented entities from `docs/DATA_MODEL.md`.
- Do not add Celery, Redis, or another queue service in the first implementation.

### `@role/developer-auth-security`

Registration, login, JWT validation, password hashing, role checks, account activity, ownership checks, upload validation, CORS, secrets, path traversal prevention, and logging safety.

- Passwords must be hashed with bcrypt or Argon2.
- Public registration creates only `user` accounts and respects `ALLOW_PUBLIC_REGISTRATION`.
- Admin accounts are seeded from environment variables, not public registration.
- Never log secrets, raw tokens, passwords, password hashes, database passwords, or sensitive environment values.
- Enforce `user` and `admin` permissions in the backend.

### `@role/developer-cv-worker`

Python CV worker, PostgreSQL job polling/claiming, heartbeat, stale recovery, model loading/cache, device selection, image/video processing, tracking, exports, summaries, and worker tests.

- Worker coordinates with the backend through PostgreSQL and shared storage, not direct HTTP job-loop calls.
- Claim queued jobs with row-level locking and process media outside the claim transaction.
- Keep YOLO26 as primary; use YOLO11 only as the documented fallback after reporting and documenting unavailability.
- Use ByteTrack by default for video tracking.
- No-detection jobs complete successfully and still produce exports when possible.
- Do not output targeting, navigation, geospatial, interception, or hardware-control data.

### `@role/developer-training`

Training scripts, cloud notebooks, dataset preparation, split manifests, model cards, metrics files, artifact schemas, and import utilities.

- Training is not launched from the web UI or API.
- Code agents create scripts/notebooks/helpers; humans run long Kaggle/Colab training sessions.
- Seraphim is the primary dataset plan; Bird vs Drone is for false-positive analysis only.
- Large datasets, weights, generated media, reports, and results must not be committed.
- Model cards and experiment metadata must reflect the actual model family used.

### `@role/developer-frontend`

React routes, Ukrainian UI, auth state, API client, dashboard, upload/job flows, results, downloads, models, experiments, admin pages, charts, and frontend build/test setup.

- Frontend calls only backend REST API endpoints.
- Visible UI text is Ukrainian; code identifiers and developer-facing docs stay English.
- Use Recharts for frontend charts, not Matplotlib.
- Do not expose `frame_stride` in the standard UI.
- Do not show raw `null` values or unsafe absolute filesystem paths.
- Backend authorization remains the source of truth even when frontend hides controls.

### `@role/developer-devops`

Dockerfiles, Compose runtime, environment examples, healthchecks, shared storage mounts, startup scripts, Makefile/script shortcuts, README command updates, and runtime smoke checks.

- Use `docker compose`, not legacy `docker-compose`.
- Runtime services are `postgres`, `backend`, `cv-worker`, and `frontend`.
- Backend and CV worker must mount the same shared storage path.
- GPU acceleration is optional and isolated to `cv-worker`.
- No real secrets in code, Dockerfiles, docs, logs, commits, or screenshots.

### `@role/code-reviewer`

Review modified files after meaningful implementation steps and before final output.

- Compare implementation against relevant docs and `.context` contracts.
- Flag product-doc mismatch, scope creep, boundary violations, unsafe auth, upload/path safety drift, queue/model-selection drift, CV-only boundary violations, weak tests, debug logs, broad exception swallowing, generated artifacts, and user-facing non-Ukrainian UI text.

### `@role/tester`

Run relevant gates and interpret failures. Use targeted checks first and broader gates when shared infrastructure or release readiness is touched.

Expected checks when scaffolds exist:

- Backend: dependency install, lint/type checks, unit tests, integration tests, build/start smoke.
- Database: migration validation, seed smoke, affected backend tests.
- CV worker: dependency install, unit tests, worker queue tests, image/video processing smoke.
- Training: script/notebook smoke checks, config validation, artifact schema validation.
- Frontend: dependency install, typecheck, lint, build, route/component tests, manual browser flow.
- Runtime: Docker Compose config/build/start, health/log check, API/storage/worker smoke.

If a command is unavailable because the area is not scaffolded yet, report `not available yet`.

### `@role/docs-maintainer`

README, docs index files, component indexes, implementation notes, and mistake logs.

- Update docs only when the task changes commands, structure, env variables, seed data, demo credentials, artifact layout, or documented file paths.
- Update existing `index.md` files when files are created, renamed, deleted, or commands change.
- Do not create new documentation files unless the current task requires them.
- Append to mistake logs only for real mistakes or near-misses that occurred.

## Quality Gate Selection

Run relevant gates by touched surface; do not run every possible check for every change.

| Touched surface | Required checks when available |
|---|---|
| Backend REST/auth | Backend lint/type checks, targeted backend tests, integration smoke when shared behavior changed |
| PostgreSQL schema/migrations/seed | Migration validation, seed smoke, affected backend/database tests |
| Uploads/path safety/downloads | Backend security tests, path traversal tests, ownership/download tests |
| Job queue/model selection | Backend job tests, CV worker queue tests, model-selection priority tests |
| CV worker image/video/tracking | Worker unit tests, processing smoke, export/no-detection checks |
| Training utilities | Script smoke checks, artifact schema validation, generated example validation |
| Frontend route/page/control | Typecheck, lint, build, route/component tests, manual browser flow when available |
| Docker/env/startup | Compose config/build/start, health/log check, storage persistence smoke |
| Final release | Backend tests, CV worker tests, frontend typecheck/build, Compose smoke, manual E2E checklist |

## File Size and Decomposition

Keep source files compact and cohesive. Optimize for clear responsibility and low context noise, not mechanical splitting.

Soft targets:

- FastAPI route modules: 150-250 LOC.
- Backend service/domain modules: 200-350 LOC.
- Database migration/seed helpers: 150-300 LOC.
- CV worker modules: 200-350 LOC.
- Training scripts: 150-300 LOC.
- React pages: 200-250 LOC.
- React components: 120-200 LOC.
- Hooks/client/state modules: 150-250 LOC.

Review thresholds:

- 300+ LOC: check for mixed responsibilities.
- 400+ LOC: split by responsibility or explain in `.context/status.md`.
- 500+ LOC: avoid unless it is a migration, generated file, lock file, static fixture, notebook export, or cohesive table-driven test.

Prefer domain modules over generic `utils`. Avoid circular imports and unnecessary abstraction layers.

## Final Response Format

End implementation or fix tasks with:

- files changed;
- steps completed;
- quality gate results as command + `PASS`/`FAIL`/`not available`;
- security/privacy result;
- index/docs updates made or skipped;
- deviations from documented plans or `.context` contracts if applicable;
- remaining risks/blockers;
- final verdict.

## Do Not

- Do not implement outside the requested scope or current documentation.
- Do not invent product behavior absent from docs.
- Do not add physical interception, autopilot, navigation, motor control, flight control, hardware control, aiming, payload control, geospatial targeting, trajectory planning, autonomous engagement, RTSP streams, webcam/live-camera processing, Streamlit, Flask, Celery, Redis, model training from the UI/API, separate unsupported runtime services, unrelated business features, or multi-language UI unless docs change.
- Do not expose PostgreSQL or shared storage internals to the frontend.
- Do not let frontend-only checks replace backend authorization.
- Do not store media binaries, result files, reports, datasets, or model weights in PostgreSQL.
- Do not store unsafe absolute host or container paths in database fields or API responses.
- Do not log secrets, raw tokens, passwords, password hashes, database passwords, or sensitive cookies.
- Do not treat no-detection jobs as failures.
- Do not use YOLO11 as the primary plan unless YOLO26 unavailability is reported and documented.
- Do not launch training from the web UI or backend API.
- Do not mark a task complete with failing relevant gates unless the failure is documented as a blocker.
