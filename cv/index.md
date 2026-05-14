# AeroVision - CV Worker Index

## General Description

The `cv/` folder contains the AeroVision Python CV worker service foundation.

According to `../docs/`, this worker will poll PostgreSQL for queued processing jobs, claim jobs with row-level locking, read uploaded media from shared storage, run YOLO-based image/video detection, apply ByteTrack by default for videos, write annotated media and CSV/JSON exports, store detections/tracks/summaries, update progress and heartbeat, and handle no-detection cases as successful results. The worker must not expose an API for the job loop and must coordinate with the backend through PostgreSQL and shared storage.

Current implementation covers settings, secret-safe logging, device selection, database connectivity helpers, storage path safety, startup checks, and an idle entrypoint. Queue claiming, inference, tracking, exports, and result writes are not implemented yet.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | CV worker image build and runtime entrypoint. |
| `pyproject.toml` | CV worker Python package metadata, runtime dependencies, dev dependencies, pytest config, and Ruff config. |
| `aerovision_worker/` | Worker package with settings, logging, device, database, storage path, and startup modules. |
| `tests/` | Worker tests for Phase 14 scaffold behavior. |
| `index.md` | CV worker folder summary, current contents, and CV-worker-local commands. |

## Commands

| Command | Status |
|---|---|
| `python -m pip install -e ".[dev]"` | installs CV worker dependencies |
| `python -m aerovision_worker.main --check-once` | runs worker startup smoke checks and exits |
| `python -m aerovision_worker.main` | starts worker and idles; queue processing not implemented yet |
| `python -m ruff check .` | runs CV worker lint checks |
| `python -m pytest` | runs CV worker tests |
| CV worker Docker build | available through root `docker compose --env-file .env.example build cv-worker` |
