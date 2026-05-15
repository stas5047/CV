# Phase 33 Design

## Phase Goal

Verify full MVP release readiness against documented acceptance criteria: runtime launch, backend/API/auth/security, CV worker queue and processing, frontend Ukrainian UX, training artifact readiness, downloads/exports, and CV-only boundary.

This phase is QA/release work, not feature design. Intended output is evidence: passing gates, documented failures, focused doc-backed fixes if needed, and final known limitations.

## Intended Behavior From Docs

Confirmed facts:

- App must launch through Docker Compose with `postgres`, `backend`, `cv-worker`, and `frontend`.
- Backend exposes all API routes under `/api`, enforces JWT auth, admin roles, ownership, upload validation, safe downloads, and path safety.
- PostgreSQL stores structured records only; filesystem storage stores uploads, results, reports, models, temp files, and datasets.
- Backend and worker coordinate through PostgreSQL and shared storage, not HTTP job-loop calls.
- Worker claims jobs with `FOR UPDATE SKIP LOCKED`, keeps claim transactions short, updates heartbeat/progress, handles stale jobs, and completes no-detection jobs successfully.
- Runtime CV outputs must remain image-space CV data only.
- YOLO26 is primary; YOLO11 is fallback only after documented unavailability.
- ByteTrack is default tracker for video.
- Frontend visible text must be Ukrainian; Recharts must be used for charts; raw `null`, absolute paths, `frame_stride`, targeting/navigation/interception language must not appear.
- Training is offline only; app imports/registers artifacts and must not launch training.

Assumptions:

- Final release readiness can be evaluated without real long training or large datasets.
- If no real model weights exist, QA should record model-dependent E2E as blocked or use documented placeholder/smoke routes only where docs allow.
- CPU mode is required baseline; GPU mode is optional and checked by Compose config/isolation unless host GPU is available.

## Architecture Decisions

- Treat Phase 33 as evidence-first release audit.
- Run narrow local gates first by component, then full runtime checks.
- Keep fixes scoped to failing documented acceptance criteria.
- Do not add new endpoints, schema fields, queues, services, UI flows, or product behavior during QA.
- Record blockers with exact command, status, and reason before any broader refactor.

## Backend Impact

- Verify backend tests, lint, health, migrations, seed, auth, ownership, path safety, downloads, model/experiment/admin APIs, and API contract boundaries.
- Any backend change must be a doc-backed defect fix only.

## Frontend Impact

- Verify lint, tests, build, protected/admin routes, Ukrainian text, no raw `null`, no absolute paths, no `frame_stride`, Recharts charts, download actions, loading/error/empty states.
- Any frontend change must preserve backend as authorization source.

## DB Impact

- Verify Alembic migration applies, seed is idempotent, required constraints/indexes are represented by tests or schema, and only relative paths are stored.
- No schema change unless a documented required field/constraint is missing and fix is scoped.

## API Impact

- Verify documented route groups, auth behavior, ownership/admin access, result downloads, CSV/JSON contract, safe errors, and CV-only output boundary.
- No new API contract may be invented.

## Security/Privacy Impact

- High security surface: auth, seeded admin, public registration toggle, CORS, upload validation, path traversal, ownership, downloads, logs, secrets.
- `.env` and real secrets must not be read, logged, committed, or copied into artifacts.
- Logs must be checked for absence of passwords, tokens, JWT secrets, DB passwords, and sensitive env values.

## Test Strategy

1. Static/repo audit: tracked files, ignored storage, safe env example, Compose service/mount/GPU isolation.
2. Dependency/setup preflight: confirm required local Python, Node, Docker, and install state or report `not available yet` / blocker before treating a gate as product failure.
3. Component gates: backend lint/tests, CV worker lint/tests, frontend lint/tests/build, training tests/artifact validation.
4. Docker config/build validation: use `.env.example` for config/build rendering only.
5. Clean-volume Docker runtime smoke: use configured `.env`, isolated Compose project name, detached startup, health/log checks, and controlled shutdown/removal of only the isolated project volumes.
6. Runtime smoke: backend health/db health, frontend reachable, worker startup/device log, migrations/seed/storage creation, seeded admin presence without reading/logging `.env` values.
7. Security checks: auth toggle, seeded admin, owner/admin access, CORS, log redaction, download guards, and complete upload-validation rejection coverage for unsupported extension, invalid MIME, oversized image/video, unsafe filename, path traversal, and user-submitted storage paths.
8. Functional E2E: user image, user video, no-detection, admin model, admin experiments, stale recovery where fixtures/model/runtime allow.
9. Frontend/manual download smoke: from job details, verify annotated media, CSV, and JSON download controls when completed artifacts exist; otherwise record exact blocker.
10. Boundary audit: API/export/UI/logs contain CV-only image-space data and no out-of-scope behavior.

Checks must be reported as command + `PASS`/`FAIL`/`not available`.

## Ambiguities Or Conflicts

- `docs/phase.md` says `all implementation docs`; interpreted as README and component indexes plus data/training implementation docs, not every source file.
- Real model weights and E2E media fixtures may be absent; plan records those as blockers or skipped/not available with exact reason.
- GPU validation may be config-only when host lacks NVIDIA runtime.
- Runtime smoke uses existing configured `.env`; if `.env` is missing, implementation records the runtime/admin-seed smoke as blocked or `not available` instead of committing a generated env file.
- Clean-volume smoke must not delete default Compose project volumes or user data. Use an isolated project name and remove only that project's resources after evidence is captured.
- No confirmed doc conflict.
