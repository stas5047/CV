# Phase 23 Design

## Phase Goal

Verify backend-created processing jobs can move through worker processing and be observed through backend API result/download endpoints. This phase is QA/integration focused. It must not add new product behavior.

## Intended Behavior From Docs

Confirmed:

- User uploads valid image/video through backend API.
- Backend validates upload, stores file under shared storage, and creates `media_files`.
- Backend creates `processing_jobs` with status `queued`; no long processing in request path.
- Worker claims queued jobs through PostgreSQL/shared storage, not backend HTTP.
- Worker marks claimed jobs `processing`, writes heartbeat/progress, writes detections/tracks/summaries/result media/CSV/JSON, and marks jobs `completed` or `failed`.
- Backend returns job detail, summary, detections, tracks, result metadata, and downloads through documented `/api/jobs/*` endpoints.
- No-detection jobs complete successfully and keep CSV/JSON downloads.
- Corrupted media or missing model file become failed jobs with safe error message.
- Regular users cannot access another user's job details or downloads.
- CPU mode must work.
- Outputs remain CV-only: image-space boxes, confidence, class, frame/timestamp, track ID, model/performance data only.

Assumptions:

- Automated smoke can use synthetic fixtures and a deterministic fake model to prove integration wiring without committed weights.
- Manual/Docker smoke can require external real model weights; if absent, record blocker with exact command/log.

## Architecture Decisions

- Keep backend and worker decoupled. Integration test must coordinate through database rows and shared storage, not backend-to-worker HTTP calls.
- Smoke must start from a clean integration environment: isolated test database/schema and isolated temp/shared storage for automated tests, or an exact Docker/local blocker if that cannot be prepared.
- Prefer a deterministic automated integration smoke that exercises:
  - backend upload API;
  - backend job creation API;
  - worker `run_poll_iteration()` or equivalent worker entry point against same clean database/shared storage;
  - backend job/result/download APIs after worker completion.
- Use real backend routes and auth in the smoke. Do not seed database rows directly for main success flow except required model/admin setup when no API-safe setup exists.
- If a fake model is used, the smoke still must use real backend routes, real database queue rows, real worker dispatch/write path, real storage writes, and real backend export/download checks.
- Use PostgreSQL-backed smoke where available for queue semantics; if local automation uses SQLite for speed, keep PostgreSQL queue marker test as required companion coverage.
- A pytest smoke with real backend routes, PostgreSQL, isolated shared storage, and worker `run_poll_iteration()` is sufficient for Phase 23 when real model weights are unavailable. Docker-backed real-inference smoke remains optional/manual and should report exact blockers when weights, codecs, or runtime support are missing.
- Do not add frontend checks. Frontend is placeholder and not part of this phase.
- Do not commit media/model artifacts. Generate tiny fixtures during test/smoke runtime and write only under ignored temp/storage paths.

## Backend Impact

- Touched only if smoke exposes a backend bug in existing upload/job/result/download behavior.
- No new API routes, request fields, response fields, roles, status values, or product flows.
- Existing route contracts from `docs/API.md` remain unchanged.

## Frontend Impact

- None. No frontend source, routing, UI, text, or build changes in Phase 23.

## DB Impact

- No schema or migration changes expected.
- Integration smoke uses existing tables:
  - `users`
  - `media_files`
  - `model_versions`
  - `processing_jobs`
  - `detections`
  - `tracks`
- Any discovered schema mismatch must be reported as blocker before adding fields.

## API Impact

- No API contract changes.
- Smoke validates existing:
  - auth login/register or seeded user flow;
  - `POST /api/media`;
  - `POST /api/jobs`;
  - `GET /api/jobs/{job_id}`;
  - result summary/detections/tracks/result metadata;
  - CSV/JSON/media downloads.

## Security/Privacy Impact

- Smoke must verify owner-only access for job detail, summary, detections, tracks, result metadata, annotated media download, CSV download, and JSON download.
- Smoke must verify downloads never expose absolute storage paths.
- Test logs and artifacts must not include raw tokens, passwords, JWT secrets, database passwords, or absolute host paths in user-facing API responses.
- Missing-model/corrupt-media failures must return safe API-visible messages, not stack traces or absolute paths.

## Test Strategy

Relevant gates for this phase:

- `docker compose --env-file .env.example config` -> Compose contract.
- Backend targeted tests for jobs/media/results/downloads after any backend change.
- CV targeted tests for queue, image processing, video processing, and startup after any worker change.
- PostgreSQL queue integration marker when PostgreSQL is reachable: `python -m pytest -m postgres` from `cv/`.
- New/updated Phase 23 smoke command, if added, must cover:
  - clean database/schema and isolated shared storage setup/teardown;
  - image upload -> job -> worker -> completed -> summary/detections/result/downloads;
  - no-detection image -> completed -> zero detections -> CSV/JSON available -> annotated media result/download when output creation is possible;
  - video flow when fixture/codec/model support is feasible, otherwise documented blocker;
  - missing model or corrupted media -> failed job with safe error and no stack trace or absolute path in API payloads;
  - cross-owner access denied for job detail, summary, detections, tracks, result metadata, annotated media download, CSV download, and JSON download;
  - CPU worker mode.

Not relevant:

- Frontend lint/typecheck/build.
- Training artifact validation.
- Experiment UI checks.
- GPU smoke unless user explicitly requests GPU.

## Ambiguities Or Conflicts

WARNING: CONFLICT

- `docs/index.md` and `README.md` describe CV worker queue/inference/export as not yet available.
- `cv/index.md` and worker source/tests show those capabilities are implemented.
- This planning contract treats Phase 23 as integration verification of existing backend + worker capabilities, not implementation of missing worker feature work.

Ambiguities:

- Real YOLO weights are not confirmed, so full real-inference Docker smoke may be blocked.
- Phase docs allow image and video fixture checks, but video is "when feasible"; implementation must document exact blocker if codec/model/runtime prevents it.
- Docs do not mandate a specific smoke harness file path; implementation should use existing `scripts/`, `backend/tests/`, or `cv/tests/` areas only and avoid new top-level folders.
