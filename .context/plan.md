# Plan - Phase 14

## Scope guard

This plan covers only Phase 14 - CV worker scaffold, settings, logging, and database access. No source code was modified while writing this contract. Future implementation must not add inference, tracking, exports, queue claiming, stale recovery, frontend UI, backend REST routes, or database migrations unless a later phase requires them.

## Ordered atomic steps

1. [@role/developer-cv-worker] Inspect `cv/`, root Compose files, and backend reference helpers before coding.
   - Verify current worker is placeholder-only.
   - Verify Compose already passes worker env vars and mounts `./storage:/app/storage`.
   - Verifiable by: `rg --files cv`, `docker compose --env-file .env.example config`.

2. [@role/developer-cv-worker] Scaffold worker Python project under `cv/`.
   - Add worker dependency manifest with phase-required runtime/test dependencies: SQLAlchemy, PostgreSQL driver, Pydantic settings, PyTorch/Ultralytics placeholder dependencies, `opencv-python-headless`, NumPy, pandas, pytest, and lint tooling.
   - Do not add Flask, Streamlit, Celery, Redis, or frontend dependencies.
   - Keep tests import-safe and avoid loading real YOLO models or requiring model artifacts in Phase 14.
   - Verifiable by: dependency manifest exists and contains only phase-relevant packages.

3. [@role/developer-cv-worker] Add worker settings module.
   - Read existing env vars: `DATABASE_URL`, `STORAGE_ROOT`, `MODELS_ROOT`, `CV_DEVICE`, `ACTIVE_MODEL_ID`, `WORKER_POLL_INTERVAL_SECONDS`, `WORKER_HEARTBEAT_FRAMES`, `WORKER_HEARTBEAT_SECONDS`, `WORKER_STALE_JOB_MINUTES`, `WORKER_MAX_RETRIES`.
   - Validate `CV_DEVICE` against `auto`, `cpu`, `cuda`.
   - Validate numeric worker settings are positive where required.
   - Redact sensitive values from repr/log-safe output.
   - Verifiable by targeted settings tests.

4. [@role/developer-cv-worker] Add worker safe logging baseline.
   - Configure structured console logging.
   - Redact secret-like keys and raw sensitive setting values.
   - Allow safe startup events, including selected device.
   - Do not log raw database URL or absolute storage paths in user-facing messages.
   - Verifiable by logging redaction tests.

5. [@role/developer-cv-worker] Add device selection helper.
   - Preserve documented `CV_DEVICE` semantics.
   - For Phase 14, log desired/selected configuration without requiring real inference or model loading.
   - `auto` must fall back to CPU when CUDA probe is unavailable.
   - `cuda` must fail clearly when CUDA is unavailable and must never log CPU-only state as selected CUDA.
   - Verifiable by unit tests with mocked CUDA availability when implemented.

6. [@role/developer-cv-worker] Add database session/access layer.
   - Create SQLAlchemy engine/session factory from worker settings.
   - Add minimal connectivity check helper.
   - Add bounded PostgreSQL readiness retry or equivalent startup-safe connectivity handling for Compose startup.
   - Log retry/failure state without exposing `DATABASE_URL`, database password, or absolute paths.
   - Do not mutate job rows in this phase.
   - Do not call backend over HTTP.
   - Verifiable by session helper tests or smoke using configured PostgreSQL.

7. [@role/developer-cv-worker] Add storage path resolver.
   - Accept only relative paths from database fields.
   - Resolve paths under `STORAGE_ROOT` or `MODELS_ROOT`.
   - Reject empty paths, NUL bytes, absolute POSIX paths, Windows absolute/drive paths, traversal segments, and UNC-like paths.
   - Return filesystem paths for worker internal use only.
   - Verifiable by path safety tests.

8. [@role/developer-cv-worker] Add worker startup entrypoint.
   - Load settings.
   - Configure logging.
   - Log safe worker startup and selected device.
   - Verify database connectivity through bounded readiness retry or equivalent startup-safe handling.
   - Idle without claiming jobs or processing media in normal mode.
   - Provide smoke/test mode that exits after settings, device, and database checks for deterministic validation.
   - Verifiable by running startup smoke command and inspecting safe logs.

9. [@role/developer-devops] Replace placeholder `cv/Dockerfile` with worker image build.
   - Install worker dependencies.
   - Use `opencv-python-headless`, no GUI OpenCV dependency.
   - Run worker entrypoint.
   - Preserve CPU-default operation.
   - Verifiable by `docker compose --env-file .env.example build cv-worker`.

10. [@role/developer-devops] Review Compose and env wiring.
    - Keep only required `cv-worker` env vars.
    - Keep shared storage mount at `/app/storage`.
    - Keep GPU override isolated to `cv-worker`.
    - Do not add new services.
    - Verifiable by `docker compose --env-file .env.example config` and GPU config command if GPU file touched.

11. [@role/developer-cv-worker] Add worker tests.
   - Cover settings validation.
   - Cover logging redaction.
   - Cover storage path safety.
   - Cover database helper import/session construction.
   - Cover startup/device logging without real inference or real model loading.
   - Cover `CV_DEVICE=auto` CPU fallback when CUDA is unavailable.
   - Cover `CV_DEVICE=cuda` clear failure when CUDA is unavailable.
   - Cover bounded database readiness retry behavior with mocked connection failures.
   - Do not add inference, queue, export, or no-detection tests yet.
   - Verifiable by worker test command from `cv/`.

12. [@role/docs-maintainer] Update component/runtime notes only if implementation changes commands or file inventory.
    - Update `cv/index.md` after scaffold files and commands exist.
    - Update README/Makefile only if new worker commands are part of the phase workflow.
    - Do not modify product docs under `docs/`.
    - Verifiable by checking docs diff contains only implementation-state/command updates.

13. [@role/tester] Run Phase 14 gates.
    - `docker compose --env-file .env.example config` -> expected PASS.
    - Worker dependency install command from `cv/` -> expected PASS once manifest exists.
    - Worker lint command from `cv/` -> expected PASS once configured.
    - Worker test command from `cv/` -> expected PASS once tests exist.
   - `docker compose --env-file .env.example build cv-worker` -> expected PASS.
   - Worker startup smoke/test-mode command -> expected PASS or documented blocker with exact command/output.
   - Worker startup smoke must prove selected-device logging and PostgreSQL connectivity without leaking secrets.
   - Do not run frontend gates.
   - Do not run backend full suite unless backend files changed.

14. [@role/code-reviewer] Review implementation against Phase 14 docs and this contract.
    - Confirm no backend-worker HTTP job loop.
    - Confirm no inference/tracking/export/queue-claim implementation slipped in.
    - Confirm no new services.
    - Confirm no schema/API changes.
    - Confirm storage paths stay relative at database boundary.
    - Confirm logs do not expose secrets or unsafe absolute paths.
    - Confirm GPU remains isolated to `cv-worker`.

15. [@role/developer-cv-worker] Fix accepted review/test issues only within Phase 14 scope.
    - Apply only fixes tied to failed Phase 14 checks or documented review findings.
    - Defer later-phase requests.
    - Verifiable by rerunning failed targeted gates.
