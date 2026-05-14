# Design - Phase 14

## Phase goal

Create CV worker foundation only: Python project scaffold, settings, safe logging, database access, safe storage path resolution, startup behavior, Docker wiring, and smoke tests. Do not implement full job polling, job claiming, inference, tracking, exports, stale recovery, or result writes in this phase.

## Intended behavior from docs

Confirmed:

- `cv-worker` is separate from backend API process.
- Worker coordinates with backend through PostgreSQL and shared storage, not backend HTTP calls.
- PostgreSQL stores structured data and job state only.
- Shared storage stores uploads, results, reports, models, temp files, datasets.
- Backend and worker must mount same storage path at `/app/storage`.
- Worker settings must cover database, storage, device, polling, heartbeat, stale-job threshold, and max retries.
- `CV_DEVICE` allowed behavior:
  - `auto`: CUDA if available, else CPU.
  - `cpu`: force CPU.
  - `cuda`: force CUDA.
- Worker must log selected device at startup.
- Worker logs must not expose secrets, tokens, database passwords, or unsafe absolute paths in user-facing messages.
- Worker storage resolver must accept database relative paths only and resolve under storage root.
- Worker must not use OpenCV GUI APIs in Docker.
- CPU mode must work.
- GPU access is optional and isolated to `cv-worker`.

Out of scope for this phase:

- Inference with YOLO.
- ByteTrack or BoT-SORT integration.
- Queue claim with `FOR UPDATE SKIP LOCKED`.
- Heartbeat/progress updates during jobs.
- Stale job recovery behavior.
- Detections/tracks/result/export writes.
- Frontend behavior.
- New backend REST API.

## Architecture decisions

- Build worker as independent Python project under `cv/`.
- Keep service boundary clear: worker imports its own modules and talks to PostgreSQL directly. No backend HTTP client.
- Use environment-driven settings matching already documented Compose variables.
- Use SQLAlchemy engine/session layer for database access.
- Use either worker-local ORM mappings or a verified non-invasive import strategy. Contract preference: worker-local minimal mappings or shared-code extraction only if it does not require backend runtime coupling. No schema change.
- Implement storage resolver as worker-local path safety code if no shared package exists.
- Implement startup path:
  - load settings;
  - configure redacted logging;
  - select/log device;
  - verify database connectivity with bounded readiness retry or equivalent startup-safe handling;
  - idle without processing jobs until later phase in normal mode;
  - support a deterministic smoke/test mode that exits after settings, device, and database checks.
- Dockerfile should install worker dependencies and run worker entrypoint, replacing placeholder infinite Python command.
- Compose env and storage mounts already exist; only adjust if implementation needs command/package wiring.

## Backend impact

- No backend API changes planned.
- No backend service logic changes planned.
- Backend ORM files are reference material only unless implementation chooses a shared-code extraction, which would need extra review because it touches backend.

## Frontend impact

- None.

## Database impact

- No schema or migration change planned.
- Worker database access must use existing tables and fields:
  - `processing_jobs`
  - `media_files`
  - `model_versions`
  - later phases will also use `detections` and `tracks`.
- Phase 14 database check is connectivity/session smoke only, not queue mutation.

## API impact

- None.

## Security/privacy impact

- Worker must redact sensitive settings in repr/log output.
- Worker must not log raw `DATABASE_URL` or database password.
- Worker must not log JWT/auth values if present in inherited env.
- Worker must not expose absolute host/container paths in user-facing messages.
- Worker must reject absolute paths, traversal segments, empty paths, drive-letter paths, and UNC-style paths before joining with `STORAGE_ROOT` or `MODELS_ROOT`.
- Worker must not execute uploaded files; Phase 14 does not decode/process uploaded media yet.
- `CV_DEVICE=auto` may fall back to CPU when CUDA probe reports unavailable.
- `CV_DEVICE=cuda` must fail clearly when CUDA is unavailable and must not log CPU-only state as selected CUDA.

## Test strategy

Relevant checks only:

- Worker unit tests:
  - settings parse defaults and env overrides;
  - `CV_DEVICE` accepts documented values and rejects invalid value;
  - sensitive settings are redacted from repr/log helper output;
  - storage path resolver accepts relative safe paths;
  - storage path resolver rejects absolute, traversal, drive-letter, empty, and UNC-like paths;
  - database session/health helper can be tested with mocked or configured engine where practical.
- Worker lint:
  - run worker lint command once scaffold defines it.
- Worker smoke:
  - worker startup command imports app, loads settings, configures logging, checks selected device semantics, verifies database connectivity through bounded readiness retry, and exits in smoke/test mode.
- Dependency/import safety:
  - tests must not load real YOLO models;
  - heavy PyTorch/Ultralytics imports should be avoided or mocked in tests where practical;
  - dependency install may be heavy, but Phase 14 tests must stay deterministic without model artifacts.
- Docker/Compose:
  - `docker compose --env-file .env.example config`
  - `docker compose --env-file .env.example build cv-worker`
  - startup smoke for `cv-worker` when practical.

Avoid generic gates:

- No frontend build/tests.
- No backend full test suite unless backend files change.
- No CV inference smoke.
- No export/no-detection tests.
- No queue claiming/stale recovery tests.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found in consulted docs for Phase 14.
- Ambiguity: prompt did not provide actual risk level.
- Ambiguity: docs require PyTorch/Ultralytics placeholder dependencies but do not define exact versions or install strategy.
- Ambiguity: docs do not specify worker package/file names.
- Ambiguity: docs say worker should log selected device, but Phase 14 does not require loading torch or proving CUDA availability beyond configuration/startup logging.
