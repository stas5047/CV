# AeroVision - CV Worker Index

## General Description

The `cv/` folder contains the AeroVision Python CV worker service foundation.

According to `../docs/`, this worker will poll PostgreSQL for queued processing jobs, claim jobs with row-level locking, read uploaded media from shared storage, run YOLO-based image/video detection, apply ByteTrack by default for videos, write annotated media and CSV/JSON exports, store detections/tracks/summaries, update progress and heartbeat, and handle no-detection cases as successful results. The worker must not expose an API for the job loop and must coordinate with the backend through PostgreSQL and shared storage.

Current implementation covers settings, secret-safe logging, device selection, database connectivity helpers, storage path safety, startup checks, PostgreSQL queue claiming, heartbeat/progress helpers, stale-job recovery, queue polling, model metadata resolution, safe model weights path handling, lazy Ultralytics model loading, in-memory model caching, and image-job processing. Image jobs read uploaded images from shared storage, run YOLO inference through the resolved model, store image-space detection rows, write annotated images, create CSV/JSON exports, update summaries/status/progress, and complete no-detection images successfully. Video inference, tracking, and track summaries are not implemented yet.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | CV worker image build and runtime entrypoint. |
| `pyproject.toml` | CV worker Python package metadata, runtime dependencies, dev dependencies, pytest config, and Ruff config. |
| `aerovision_worker/` | Worker package with settings, logging, device, database, storage path, model runtime, startup, queue, and image processing modules. |
| `tests/` | Worker tests for startup, settings, logging, storage, database, model runtime, queue helpers, PostgreSQL queue behavior, and image processing/export behavior. |
| `index.md` | CV worker folder summary, current contents, and CV-worker-local commands. |

## Commands

| Command | Status |
|---|---|
| `python -m pip install -e ".[dev]"` | installs CV worker dependencies |
| `python -m aerovision_worker.main --check-once` | runs worker startup smoke checks and exits |
| `python -m aerovision_worker.main` | starts worker polling; image jobs are claimed and processed, while later-phase video jobs remain queued |
| `python -m ruff check .` | runs CV worker lint checks |
| `python -m pytest` | runs CV worker tests |
| `python -m pytest -m postgres` | runs PostgreSQL queue integration tests when PostgreSQL is reachable |
| CV worker Docker build | available through root `docker compose --env-file .env.example build cv-worker` |
