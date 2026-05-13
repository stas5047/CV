# PROJECT_CONTEXT.md

## Purpose

This document defines the product context for the Drone Computer Vision Subsystem. It is the first document a code agent should read before making implementation decisions.

This document is canonical for:

- product definition;
- MVP scope;
- explicit non-goals;
- required technology stack;
- high-level user roles;
- CV-only system boundary;
- documentation map.

This document is not canonical for database schema, endpoint details, security implementation, UI page requirements, worker internals, or training workflows. Those topics are defined in their dedicated documentation files.

## Product Summary

The project is a Dockerized full-stack web application for detecting and visually tracking drones in uploaded images and video files.

The application allows authenticated users to upload media, create processing jobs, process the media with a fine-tuned YOLO-based detector, visualize annotated results, inspect detection statistics, download processed media, and export structured detection data in CSV and JSON formats.

The system also includes an admin area for model registry management, active model selection, global processing history, experiment metric import, and safe storage cleanup.

## Final Product Definition

The final product is not a prototype. It must be implemented as a complete containerized web application with:

- FastAPI backend;
- React frontend;
- PostgreSQL database;
- separate CV worker service;
- shared filesystem storage;
- model integration;
- media processing;
- result storage;
- CSV and JSON exports;
- experiment and metrics visualization.

The project must not be reduced to a Streamlit app, CLI-only pipeline, local notebook, or temporary demo wrapper.

## MVP Scope

The MVP must support:

1. User registration and login using email and password.
2. JWT-based authentication.
3. Two roles: `user` and `admin`.
4. Upload of image and video files.
5. Image-based drone detection.
6. Video frame-by-frame drone detection.
7. Video tracking with ByteTrack by default.
8. Annotated output media generation.
9. Detection table display.
10. Per-job summary metrics.
11. CSV export with one row per detection.
12. JSON export containing job, media, model, parameter, summary, detection, and track data.
13. PostgreSQL persistence for structured records.
14. Filesystem storage for media, result files, reports, datasets, and model weights.
15. Model registry with active model selection.
16. Experiment metric import and display.
17. Ukrainian-language frontend UI.
18. Docker Compose launch after initial setup.
19. CPU inference support, with optional GPU acceleration isolated to the CV worker.

## Core Goals

The system must:

- detect drones in uploaded images;
- detect drones in uploaded video files frame by frame;
- track detected drone objects across video frames;
- display bounding boxes, class label, confidence score, and track ID when available;
- store media metadata, processing jobs, detections, tracks, model versions, and experiment metrics;
- provide measurable detection and performance metrics;
- support local inference and cloud-based model training workflows;
- keep the full application runnable through Docker Compose.

## System Boundary

This project is a computer vision subsystem only.

Allowed system outputs are limited to image-space computer vision data, including:

- detection status;
- frame index;
- timestamp;
- bounding box coordinates;
- image-space center point;
- confidence score;
- class label;
- track ID;
- FPS;
- model version;
- processing summary metrics.

The system must not produce or imply:

- physical interception instructions;
- navigation commands;
- autopilot commands;
- flight-control commands;
- motor commands;
- aiming commands;
- payload commands;
- geospatial targeting data;
- trajectory planning;
- autonomous engagement decisions;
- hardware-control behavior.

All coordinates are image-space pixel coordinates. The system does not convert detections into real-world coordinates.

Concrete API and export output boundaries are defined in `API.md`.

## Explicit Non-Goals

The following must not be implemented in the MVP:

- physical drone interception;
- weaponization or target engagement logic;
- autopilot, navigation, motor control, flight control, or hardware control;
- trajectory planning or interception path calculation;
- real-world geolocation or conversion from image coordinates to physical coordinates;
- RTSP stream processing;
- webcam or live camera processing;
- Streamlit application;
- Flask backend;
- Celery or Redis queue in the first implementation;
- model training from the web UI;
- storing image or video binary data directly in PostgreSQL;
- email delivery, email confirmation, password reset email, OAuth, or social login;
- complex enterprise RBAC beyond `user` and `admin` roles;
- committing datasets, model weights, processed videos, uploads, or generated results into Git;
- GUI-dependent OpenCV calls inside containers;
- CAPTCHA, registration rate limiting, account lockout, or two-factor authentication;
- manual ground-truth track annotation in the MVP;
- true tracking metrics requiring manually annotated track identities, such as MOTA, IDF1, or HOTA.

## Required Technology Stack

### Backend

Required backend technologies:

- Python;
- FastAPI;
- Pydantic v2;
- SQLAlchemy 2.x;
- Alembic migrations;
- PostgreSQL;
- JWT authentication;
- bcrypt or Argon2 password hashing;
- Uvicorn or Gunicorn/Uvicorn.

### Computer Vision

Required CV technologies:

- Python;
- PyTorch;
- Ultralytics YOLO;
- OpenCV using `opencv-python-headless`;
- NumPy;
- pandas;
- Matplotlib for saved backend/training-side artifacts only.

Frontend charts must use Recharts, not Matplotlib.

### Frontend

Required frontend technologies:

- React;
- TypeScript;
- Vite;
- Tailwind CSS;
- shadcn/ui;
- React Router;
- TanStack Query;
- Recharts.

Visible UI text must be Ukrainian. Code identifiers, route names, database names, API fields, logs, and developer-facing comments must be English.

### Database and Storage

Required database:

- PostgreSQL.

PostgreSQL stores structured records and metadata only. Media files, result media, CSV files, JSON files, reports, datasets, and model weights are stored in filesystem volumes.

### Containerization

Required containerization:

- Docker;
- Docker Compose.

GPU acceleration is optional and must be requested only by the `cv-worker` service. The base application must still support CPU inference.

## User Roles Summary

The system has exactly two authenticated roles:

| Role | Summary |
|---|---|
| `user` | Can upload media, process own files, view own jobs, inspect own results, and download own exports. |
| `admin` | Inherits user capabilities and can additionally view global history, manage models, import experiments, run safe storage cleanup, and view a basic user list. |

Unauthenticated guests may only access login, registration, and minimal public landing information if a landing page exists.

Detailed permissions and access control rules are defined in `AUTH_SECURITY.md` and `API.md`.

## Key Product Decisions

These decisions are part of the product definition and must not be changed without explicit approval:

- The backend framework is FastAPI.
- The frontend framework is React.
- The database is PostgreSQL.
- The detector is Ultralytics YOLO.
- The primary model family is YOLO26.
- YOLO11 is a documented fallback only when YOLO26 is unavailable after the issue is explicitly reported and documented.
- The CV worker is a separate service.
- Backend and CV worker coordinate through PostgreSQL and shared storage, not through direct HTTP job-loop calls.
- The queue is PostgreSQL-based in the first implementation.
- The UI language is Ukrainian.
- The system is CV-only and does not implement control, targeting, navigation, or physical interception behavior.

## Documentation Map

Read the core documentation in this order:

1. `PROJECT_CONTEXT.md` — product scope, non-goals, stack, boundary, documentation map.
2. `ARCHITECTURE.md` — services, storage, Docker, worker queue, service communication.
3. `DATA_MODEL.md` — PostgreSQL tables, relationships, constraints, indexes, soft deletion.
4. `API.md` — endpoints, access matrix, downloads, external output boundary.
5. `AUTH_SECURITY.md` — authentication, authorization, ownership, uploads, CORS, secrets.
6. `CV_PIPELINE.md` — runtime detection, tracking, model selection, exports, no-detection handling.
7. `TRAINING_EXPERIMENTS.md` — offline training, datasets, experiments, artifacts, import flow.
8. `FRONTEND_UX.md` — Ukrainian UI, routes, pages, states, design rules.
9. `TESTING_QA.md` — acceptance criteria, testing coverage, manual scenarios.

Separate project files that may exist outside this core documentation:

- `AGENTS.md` — code-agent operating rules.
- `CLAUDE.md` — Claude-specific agent instructions.
- `ROADMAP.md` — implementation order and priority cut decisions.
- `index.md` — optional documentation landing page.

## Scope Ownership Rules

To avoid duplicated or conflicting instructions:

- Product scope lives here.
- Service architecture lives in `ARCHITECTURE.md`.
- Database fields live in `DATA_MODEL.md`.
- Endpoint contracts live in `API.md`.
- Upload validation lives in `AUTH_SECURITY.md`.
- Runtime inference and tracking live in `CV_PIPELINE.md`.
- Training and experiment artifacts live in `TRAINING_EXPERIMENTS.md`.
- Visible UI requirements live in `FRONTEND_UX.md`.
- Verification requirements live in `TESTING_QA.md`.

When a topic belongs to another file, this document should reference that file instead of restating detailed rules.
