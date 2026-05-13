# AeroVision - Backend Index

## General Description

The `backend/` folder is reserved for the AeroVision FastAPI backend application.

According to `../docs/`, this backend will expose the `/api` REST API, enforce JWT authentication and role/ownership rules, validate uploads and processing parameters, persist structured records in PostgreSQL, manage media/jobs/results/models/experiments/admin operations, and serve safe downloads from shared storage. The backend must not perform long-running image or video inference inside upload or job-creation requests.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | Phase 1 buildable placeholder container; no FastAPI application or product routes yet. |
| `index.md` | Backend folder summary, current contents, and backend-local commands. |

No backend scaffold, dependency manifest, application package, migrations, or tests exist yet in this checkout.

## Commands

| Command | Status |
|---|---|
| Backend dependency install | not available yet |
| Backend application start | not available yet |
| Backend lint/type checks | not available yet |
| Backend tests | not available yet |
| Backend Docker build | available through root `docker compose --env-file .env.example build backend` |
| Database migration and seed | not available yet |

Update this section when backend files and scripts are added.
