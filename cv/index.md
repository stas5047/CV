# AeroVision - CV Worker Index

## General Description

The `cv/` folder is reserved for the AeroVision Python CV worker service.

According to `../docs/`, this worker will poll PostgreSQL for queued processing jobs, claim jobs with row-level locking, read uploaded media from shared storage, run YOLO-based image/video detection, apply ByteTrack by default for videos, write annotated media and CSV/JSON exports, store detections/tracks/summaries, update progress and heartbeat, and handle no-detection cases as successful results. The worker must not expose an API for the job loop and must coordinate with the backend through PostgreSQL and shared storage.

## Current Files

| Path | Purpose |
|---|---|
| `index.md` | CV worker folder summary, current contents, and CV-worker-local commands. |

No CV worker scaffold, dependency manifest, Dockerfile, application package, model-loading code, processing code, or tests exist yet in this checkout.

## Commands

| Command | Status |
|---|---|
| CV worker dependency install | not available yet |
| CV worker start | not available yet |
| CV worker lint/type checks | not available yet |
| CV worker tests | not available yet |
| CV worker Docker build | not available yet |

Update this section when CV worker files and scripts are added.
