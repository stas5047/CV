# AeroVision - Frontend Index

## General Description

The `frontend/` folder is reserved for the AeroVision React + TypeScript single-page application.

According to `../docs/`, this frontend will provide a Ukrainian-language dashboard-style interface for authentication, media upload, job creation, job status/results, detection and track tables, downloads, model registry views, experiment metrics, and admin-only pages. The frontend must call only the backend REST API and must not access PostgreSQL, shared storage paths, or CV inference directly.

## Current Files

| Path | Purpose |
|---|---|
| `Dockerfile` | Phase 1 buildable placeholder container; no React/Vite application or UI yet. |
| `index.md` | Frontend folder summary, current contents, and frontend-local commands. |

No frontend scaffold, dependency manifest, Vite app, source files, or tests exist yet in this checkout.

## Commands

| Command | Status |
|---|---|
| Frontend dependency install | not available yet |
| Frontend dev server | not available yet |
| Frontend lint/type checks | not available yet |
| Frontend tests | not available yet |
| Frontend build | not available yet |
| Frontend Docker build | available through root `docker compose --env-file .env.example build frontend` |

Update this section when frontend files and scripts are added.
