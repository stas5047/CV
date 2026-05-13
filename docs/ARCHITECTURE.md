# ARCHITECTURE.md

## Purpose

This document defines the system architecture for the Drone Computer Vision Subsystem.

This document is canonical for:

- Docker services;
- service responsibilities;
- service communication;
- shared storage layout;
- backend and CV worker interaction;
- PostgreSQL job queue behavior;
- worker locking, heartbeat, and stale job recovery;
- CPU/GPU deployment policy;
- environment variable groups;
- repository layout guidance.

This document is not canonical for database field definitions, endpoint contracts, UI design, training experiments, or authentication details.

## Architecture Summary

The project is a containerized service-based client-server application. It is not a strict microservice system, but it contains multiple cooperating services packaged as containers.

Required services:

| Service | Responsibility |
|---|---|
| `frontend` | React application with Ukrainian UI. |
| `backend` | FastAPI REST API, authentication, upload validation, job creation, result serving, admin operations. |
| `cv-worker` | Separate Python service for queued image/video processing, detection, tracking, exports, and result updates. |
| `postgres` | PostgreSQL database for structured data and job state. |

Optional service:

| Service | Responsibility |
|---|---|
| `nginx` or another reverse proxy | Optional production-like routing. Not required for the first implementation. |

The base architecture is:

```text
User -> React Frontend -> FastAPI Backend <-> PostgreSQL <-> CV Worker
                                |                         |
                                +------ Shared Storage ----+
```

The backend and CV worker communicate indirectly through PostgreSQL and shared storage. They must not call each other over HTTP for the job loop.

## Service Responsibilities

### Frontend

The frontend is responsible for:

- Ukrainian-language UI;
- authentication screens;
- dashboards;
- upload and processing forms;
- job progress display;
- processed media preview;
- detection and track tables;
- model and experiment pages;
- admin page visibility for admins only;
- calling the backend REST API.

The frontend must not perform CV inference, direct database access, direct filesystem access, or model training.

### Backend

The backend is responsible for:

- REST API exposure under `/api`;
- JWT authentication;
- user and role checks;
- upload validation;
- storing uploaded files in shared storage;
- creating media records;
- creating processing jobs;
- exposing job status and results;
- serving safe download endpoints;
- managing model registry records;
- importing experiment results;
- admin statistics and cleanup actions;
- database migrations through Alembic.

The backend must not process long videos synchronously inside upload or job-creation requests.

### CV Worker

The CV worker is responsible for:

- polling PostgreSQL for queued jobs;
- claiming jobs using PostgreSQL row-level locking;
- loading the selected YOLO model;
- running image and video inference;
- applying ByteTrack by default for video tracking;
- writing annotated media files;
- writing CSV and JSON exports;
- saving detections, track summaries, and job summaries;
- updating progress and heartbeat;
- handling no-detection cases as successful results;
- handling failures safely.

The CV worker should process one GPU-heavy job at a time by default and avoid unnecessary repeated model loading.

### PostgreSQL

PostgreSQL stores:

- users;
- media metadata;
- processing jobs;
- detections;
- tracks;
- model versions;
- experiment runs;
- experiment metrics;
- job queue state.

PostgreSQL must not store binary media files, result files, reports, datasets, or model weights.

### Shared Storage

Shared storage stores:

- uploaded media;
- annotated result media;
- detection exports;
- job summaries;
- experiment reports;
- model weights and model cards;
- temporary files;
- datasets.

Both the backend and CV worker must mount the same shared storage volume at the same container path.

## Service Communication Rules

### Allowed Communication

- Frontend calls backend REST endpoints.
- Backend reads and writes PostgreSQL records.
- CV worker reads and writes PostgreSQL records.
- Backend writes uploaded files to shared storage.
- CV worker reads uploaded files from shared storage.
- CV worker writes results to shared storage.
- Backend serves downloads from shared storage using safe download endpoints.

### Disallowed Communication

- Backend must not call the CV worker over HTTP for the job loop.
- CV worker must not call the backend over HTTP for job polling.
- Frontend must not access PostgreSQL directly.
- Frontend must not access container filesystem paths directly.
- Any service must not expose absolute host filesystem paths in API responses.

## End-to-End Processing Flow

The required image/video processing flow is:

1. User uploads media through the frontend.
2. Backend validates file type, MIME type, size, filename safety, and user permissions.
3. Backend stores the file in shared storage using generated internal paths.
4. Backend creates a `media_files` record.
5. User starts processing.
6. Backend validates processing parameters and model selection.
7. Backend creates a `processing_jobs` record with status `queued`.
8. CV worker polls PostgreSQL for queued jobs.
9. CV worker claims one job with row-level locking.
10. CV worker marks the job as `processing` and commits the claim transaction.
11. CV worker processes media outside the claim transaction.
12. CV worker writes progress and heartbeat updates.
13. CV worker saves detections, track summaries, exports, result media, and summary data.
14. CV worker marks the job as `completed` or `failed`.
15. Frontend polls job status and displays progress or results.

No long-running media processing must happen inside the upload request or job-creation request.

## PostgreSQL Job Queue

The first implementation uses PostgreSQL as the job queue. Celery and Redis must not be added unless explicitly approved later.

Required job statuses:

| Status | Meaning |
|---|---|
| `queued` | Job is waiting for a worker. |
| `processing` | Worker has claimed the job and is processing it. |
| `completed` | Processing finished successfully, including no-detection cases. |
| `failed` | Processing failed and stored an error message. |
| `cancelled` | Cancellation state exists in the data model; hard interruption can be deferred. |

### Job Claiming

The worker must claim jobs with PostgreSQL row-level locking using `FOR UPDATE SKIP LOCKED`.

The job claim transaction must be short:

1. Start transaction.
2. Select the oldest queued job with row-level locking.
3. Update the job to `processing`.
4. Set `locked_by`, `locked_at`, `started_at`, and `last_heartbeat_at`.
5. Commit transaction.
6. Process media outside the transaction.

The worker must not hold a database transaction open while processing media.

### Queue Polling

Default queue polling interval when no job is available:

- 2 seconds.

The interval must be configurable through worker environment variables.

## Worker Heartbeat and Progress

For video jobs, the worker must update:

- `progress_percent`;
- `last_heartbeat_at`.

Default update rule:

- every 30 frames or every 2 seconds, whichever comes first.

For image jobs, progress may move from 0 to 100 at completion.

Progress is calculated from processed frame count and total frame count for video jobs.

## Stale Job Recovery

A job in `processing` state is considered stale when `last_heartbeat_at` is older than the configured stale-job threshold.

Default stale threshold:

- 10 minutes.

Recovery behavior:

1. If `retry_count` is lower than the configured maximum retry count, reset the job to `queued`, increment `retry_count`, and clear lock fields.
2. If `retry_count` reached the configured maximum, mark the job as `failed` with a worker-timeout error message.

Default maximum retries:

- 2.

Stale job recovery may run on worker startup, on a periodic worker timer, or through an admin action. Worker restart must not leave jobs permanently stuck in `processing`.

## Shared Storage

### Required Mount Rule

The backend and CV worker must mount the same shared storage volume at the same container path:

| Component | Path |
|---|---|
| Container path | `/app/storage` |
| Default host path | `./storage` or configured equivalent |

This is a hard requirement. If one of the two services does not mount the shared volume, media processing or result serving will break.

### Required Storage Folders

Paths are relative to `STORAGE_ROOT`:

| Folder | Purpose |
|---|---|
| `uploads/` | Original uploaded images and videos. |
| `results/` | Annotated media, detection exports, job summaries. |
| `reports/` | Imported experiment reports and generated evaluation artifacts. |
| `models/` | Model weights, model cards, model metrics. |
| `temp/` | Temporary processing files. |
| `datasets/` | Local dataset subsets for training preparation and smoke tests. |

### Recommended Logical Layout

The implementation should use generated IDs for paths and avoid raw user filenames:

| Logical path pattern | Purpose |
|---|---|
| `uploads/{user_id}/{media_id}/original.{ext}` | Original uploaded file. |
| `results/{job_id}/annotated.{ext}` | Annotated image. |
| `results/{job_id}/annotated.mp4` | Annotated video when MP4 output is possible. |
| `results/{job_id}/detections.csv` | CSV detection export. |
| `results/{job_id}/detections.json` | JSON detection export. |
| `results/{job_id}/summary.json` | Job summary file. |
| `reports/{experiment_id}/metrics.json` | Imported experiment metrics. |
| `reports/{experiment_id}/confusion_matrix.png` | Confusion matrix image when available. |
| `models/{model_version_id}/weights.pt` | Model weights. |
| `models/{model_version_id}/model_card.json` | Model card. |

### Relative Path Rule

All stored paths in PostgreSQL must be relative to `STORAGE_ROOT`.

Correct examples:

- `uploads/{user_id}/{media_id}/original.mp4`
- `results/{job_id}/annotated.mp4`
- `models/{model_version_id}/weights.pt`

Incorrect examples:

- `/home/user/project/storage/uploads/...`
- `/app/storage/uploads/...`

API responses must expose download URLs or logical references, not unsafe internal filesystem paths.

## Docker Requirements

Docker Compose must define at least:

- `postgres`;
- `backend`;
- `cv-worker`;
- `frontend`.

Health checks should be defined where practical, especially for PostgreSQL and backend health endpoints.

After initial setup, the application must support a one-command local launch in CPU mode.

GPU mode may use an additional Compose override or profile. GPU access must be requested only by `cv-worker`.

## CPU and GPU Policy

The application must support CPU inference for images and short videos.

GPU acceleration is optional but recommended for longer videos and demonstrations. GPU access must not be required by frontend, backend, or PostgreSQL.

The CV worker must select its device through configuration:

| Value | Meaning |
|---|---|
| `auto` | Use CUDA when available, otherwise CPU. |
| `cpu` | Force CPU inference. |
| `cuda` | Force CUDA inference. |

The worker must log the selected device at startup.

The documentation must not promise fixed FPS numbers because performance depends on hardware, media resolution, codec, image size, and rendering overhead.

## OpenCV Policy

The project must use `opencv-python-headless` inside containers.

The implementation must not use GUI-dependent OpenCV calls such as window display functions inside Docker containers.

## Environment Variable Groups

Required environment variable groups:

| Group | Variables |
|---|---|
| Database | `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` |
| Auth | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ALLOW_PUBLIC_REGISTRATION` |
| Storage | `STORAGE_ROOT`, `MODELS_ROOT` |
| CV | `CV_DEVICE`, `ACTIVE_MODEL_ID` |
| Backend | `BACKEND_CORS_ORIGINS`, `MAX_IMAGE_SIZE_MB`, `MAX_VIDEO_SIZE_MB` |
| Worker | `WORKER_POLL_INTERVAL_SECONDS`, `WORKER_HEARTBEAT_FRAMES`, `WORKER_HEARTBEAT_SECONDS`, `WORKER_STALE_JOB_MINUTES`, `WORKER_MAX_RETRIES` |

Secrets must not be committed to Git. A `.env.example` file must contain safe placeholders.

## Initial Setup Expectations

Before first launch, the user must be able to:

1. Install Docker and Docker Compose.
2. Configure NVIDIA host dependencies if GPU mode is needed.
3. Create `.env` from `.env.example`.
4. Create required storage directories or run a helper script that creates them.
5. Place model weights under `storage/models/` or register a model through a helper script.
6. Run database migrations.
7. Seed the initial admin account from environment variables.

Recommended helpers include setup script, migration command, admin seeding command, model registration script, and Makefile targets. The exact implementation is left to the code agent.

## Repository Layout Guidance

The implementation should generally follow this structure:

```text
project-root/
  backend/
  frontend/
  cv/
  training/
  scripts/
  storage/
  docker-compose.yml
  docker-compose.gpu.yml
  Makefile
  .env.example
  README.md
```

The exact internal structure can be refined during implementation, but the service boundaries must remain clear.

## Architecture Invariants

The following architecture rules must remain true:

- The system is a full-stack Dockerized web application.
- The CV worker is separate from the backend API process.
- Long video processing is never done synchronously inside upload requests.
- Backend and worker coordinate through PostgreSQL and shared storage.
- Backend and worker do not call each other over HTTP for the job loop.
- PostgreSQL stores structured data only, not binary media.
- Storage paths in the database are relative to `STORAGE_ROOT`.
- Backend and worker mount the same shared storage volume.
- CPU inference must be possible.
- GPU usage is isolated to `cv-worker`.
- Celery and Redis are not part of the first implementation.
- The application must remain runnable through Docker Compose after initial setup.
