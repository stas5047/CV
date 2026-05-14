# AeroVision - Drone Computer Vision Subsystem Documentation Index

This is the current documentation index for the AeroVision Drone Computer Vision Subsystem.

The project is a Dockerized full-stack web application for detecting and visually tracking drones in uploaded image and video files. The documented system uses a FastAPI backend, PostgreSQL persistence, a separate Python CV worker, shared filesystem storage, YOLO-based inference, and a React + TypeScript Ukrainian-language frontend.

This file is a navigation map for agents and maintainers. Update it whenever documentation files or important component indexes are created, renamed, removed, or become sources of truth.

---

## Agent and Repository Navigation

| File | Description |
|---|---|
| [AGENTS.md](../AGENTS.md) | Shared implementation, verification, review-resolution, workflow, source-of-truth, command, and quality-gate rules for agents. |
| [CLAUDE.md](../CLAUDE.md) | Claude-specific independent review, architecture-validation, and diagnosis rules. |
| [README.md](../README.md) | Current local setup notes, implemented backend API notes, Compose validation commands, and storage bootstrap command. |
| [backend/index.md](../backend/index.md) | Backend folder summary, current contents, and backend-local commands. |
| [frontend/index.md](../frontend/index.md) | Frontend folder summary, current contents, and frontend-local commands. |
| [cv/index.md](../cv/index.md) | CV worker folder summary, current contents, and CV-worker-local commands. |
| [training/index.md](../training/index.md) | Training folder summary, current contents, and training-local commands. |
| [mistakes-codex.md](mistakes-codex.md) | Codex mistake log for real mistakes and near-misses. |
| [phase.md](phase.md) | Current phase/status notes when the project workflow uses this file. |

---

## Product, Architecture, and Roadmap

| File | Description |
|---|---|
| [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) | Top-level source of truth for product identity, MVP scope, non-goals, CV-only boundary, required stack, roles, key decisions, and documentation map. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Service responsibilities, communication boundaries, shared storage, PostgreSQL job queue, worker heartbeat/stale recovery, Docker requirements, and repository layout guidance. |
| [ROADMAP.md](ROADMAP.md) | Implementation phases, fixed decisions, quality gates, target layout, final acceptance definition, and recommended phase order. |

---

## Contracts, Data, Security, and CV Runtime

| File | Description |
|---|---|
| [API.md](API.md) | Backend REST API contract, authentication endpoints, media/jobs/results/models/experiments/admin endpoints, downloads, exports, errors, and access control matrix. |
| [DATA_MODEL.md](DATA_MODEL.md) | PostgreSQL entities, relationships, constraints, indexes, soft deletion, relative path rules, and no-detection/model-selection data rules. |
| [AUTH_SECURITY.md](AUTH_SECURITY.md) | JWT authentication, roles, account activity, public registration, seeded admin, ownership, upload validation, CORS, secret handling, and logging safety. |
| [CV_PIPELINE.md](CV_PIPELINE.md) | Runtime image/video processing, YOLO model policy, model selection priority, tracking, no-detection behavior, exports, metrics, and worker error handling. |

---

## Training, Frontend, and QA

| File | Description |
|---|---|
| [TRAINING_EXPERIMENTS.md](TRAINING_EXPERIMENTS.md) | Cloud-notebook training policy, dataset plan, YOLO26/YOLO11 fallback rules, artifact layout, model cards, experiment types, and import workflow. |
| [FRONTEND_UX.md](FRONTEND_UX.md) | React + TypeScript frontend stack, Ukrainian UI rules, routes, pages, loading/error/empty states, admin visibility, charts, and dashboard design expectations. |
| [TESTING_QA.md](TESTING_QA.md) | Acceptance criteria, automated test layers, security checks, worker queue checks, frontend state checks, Docker launch checks, and manual E2E scenarios. |

---

## Source-of-Truth Map

| Question | Primary file |
|---|---|
| What is the product, MVP scope, fixed stack, CV-only boundary, and what is out of scope? | [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) |
| How are frontend, backend, PostgreSQL, CV worker, and shared storage separated? | [ARCHITECTURE.md](ARCHITECTURE.md) |
| What phases should implementation follow? | [ROADMAP.md](ROADMAP.md) |
| What REST endpoints, access rules, downloads, CSV/JSON exports, and external output boundaries are required? | [API.md](API.md) |
| What data must PostgreSQL store and which paths must remain relative? | [DATA_MODEL.md](DATA_MODEL.md) |
| Who can access which features, and how are authentication, uploads, CORS, secrets, and logs protected? | [AUTH_SECURITY.md](AUTH_SECURITY.md) |
| How should runtime detection, tracking, model selection, no-detection handling, and exports work? | [CV_PIPELINE.md](CV_PIPELINE.md) |
| How should cloud training, datasets, model cards, and imported experiments be handled? | [TRAINING_EXPERIMENTS.md](TRAINING_EXPERIMENTS.md) |
| What pages, UI states, Ukrainian labels, charts, and role-based frontend views are required? | [FRONTEND_UX.md](FRONTEND_UX.md) |
| What automated checks, integration scenarios, and manual demo steps are expected? | [TESTING_QA.md](TESTING_QA.md) |

---

## Current Implementation State

The repository currently contains the project documentation set, Docker Compose scaffold, safe environment example, README setup notes, storage bootstrap helper, and component folders with index files.

The `backend/` folder contains the implemented FastAPI backend foundation, database schema/migration, startup setup, auth/security helpers, media/model/job/result/admin/experiment APIs, concrete result download routes, and backend tests through the Phase 13 API contract audit.

The `cv/` folder contains the Phase 14 worker scaffold with a Python package, dependency manifest, settings, secret-safe logging, device selection, database connectivity helpers, storage path safety, startup checks, Docker entrypoint, and worker tests. It does not yet contain queue claiming, inference, tracking, exports, or result writes.

The `frontend/` folder contains a buildable placeholder Dockerfile only. It does not yet contain product application scaffolds, dependency manifests, source packages, or UI.

The `training/` folder still contains only `index.md` and no training utilities.

Component index files should stay narrow: general folder description, files currently present in that folder, and commands that are run from that folder. If no commands exist yet, the component index should say that commands are not available yet.

---

## Update Rule

Update this file when a documentation file is created, renamed, removed, or becomes an important source of truth.

Do not duplicate full endpoint contracts, database schemas, permission matrices, upload rules, CV pipeline details, model/training rules, page specifications, or deployment procedures here. Keep this file as a navigation map.
