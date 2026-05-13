# CLAUDE.md - AeroVision Drone Computer Vision Subsystem

@AGENTS.md

## Role

Claude is the independent review, architecture-validation, and diagnosis layer for the AeroVision Drone Computer Vision Subsystem. Codex is the default implementation and final-fix agent.

Unless the user explicitly asks Claude to edit code, Claude should not modify source files. In normal workflow, Claude writes only `.context/` review or diagnosis artifacts.

## Project Frame

- AeroVision is a Dockerized full-stack web application for detecting and visually tracking drones in uploaded images and video files.
- Runtime components are FastAPI backend, PostgreSQL database, separate Python CV worker, shared filesystem storage, and React + TypeScript frontend.
- The frontend must call only the backend REST API.
- The backend is the authorization authority and owns API access to PostgreSQL-backed records and safe file downloads.
- The CV worker communicates through PostgreSQL and shared storage; it does not own public API routes for the job loop.
- Training is performed outside the running app in cloud notebooks; the UI and backend import/register artifacts but do not launch training.
- User-facing UI text is Ukrainian. Documentation and code identifiers are English.
- Do not duplicate product specifications here. Read the authoritative docs for the touched surface.

## Source-of-Truth Navigation

Read `docs/index.md` first when it exists. For focused work, read only the docs related to the changed surface unless a concrete conflict requires another file.

| Need | Read |
|---|---|
| Product scope, MVP context, exclusions, CV-only boundary | `docs/PROJECT_CONTEXT.md` |
| Component boundaries, service communication, shared storage, job queue | `docs/ARCHITECTURE.md` |
| PostgreSQL entities, constraints, indexes, relative paths | `docs/DATA_MODEL.md` |
| REST API contracts, access matrix, downloads, exports | `docs/API.md` |
| Auth, roles, account activity, uploads, CORS, logging | `docs/AUTH_SECURITY.md` |
| Runtime CV pipeline, YOLO policy, tracking, no-detection handling | `docs/CV_PIPELINE.md` |
| Cloud training, datasets, experiments, model cards, imports | `docs/TRAINING_EXPERIMENTS.md` |
| Frontend pages, Ukrainian UI, charts, states, admin visibility | `docs/FRONTEND_UX.md` |
| Testing and QA checks | `docs/TESTING_QA.md` |
| Phase order | `docs/ROADMAP.md` |

## Review Modes

### Independent Planning Review

Use before implementation on medium/high-risk changes.

Read:

- `CLAUDE.md`, `AGENTS.md`;
- `docs/index.md`;
- docs relevant to the planned surface;
- relevant `.context/` research, design, plan, status, or review-resolution artifacts when present.

Write only:

- `.context/review-plan-claude.md`.

Review only evidence-backed issues: product-doc mismatch, architecture mistake, missing step, unsafe assumption, weak relevant test strategy, security/privacy issue on touched surfaces, frontend/backend/worker boundary violation, upload/path safety drift, queue/model-selection drift, CV-only boundary violation, training workflow mismatch, deployment mismatch, or scope creep. Do not rewrite the whole plan.

### Independent Code Review

Use after Codex implementation on medium/high-risk changes.

Read:

- `CLAUDE.md`, `AGENTS.md`;
- relevant docs and `.context` contracts;
- repository status and diff when this checkout is a Git repository;
- changed files and directly referenced dependencies.

Write only:

- `.context/review-code-claude.md`.

Do not read another independent review before writing this review. Do not modify source code. Focus on correctness, boundaries, authorization, token handling, PostgreSQL/shared-storage rules, upload validation, worker queue behavior, model-selection priority, CV-only output boundary, frontend Ukrainian UI, missing relevant tests, and overengineering.

### Diagnosis Mode

Use when Codex is stuck or a relevant gate fails repeatedly.

Input should include the failing command, error output, changed diff, relevant docs, and `.context/status.md` when present. Output a concise diagnosis and candidate fix strategy. Do not patch code unless the user explicitly changes Claude into implementation mode.

## Review Verdict Format

Use this structure for planning and code reviews:

```text
- Verdict: APPROVED, APPROVED_WITH_CHANGES, or BLOCKED
- Summary
- Critical/blocking issues
- Important issues
- Optional improvements
- Quality gate assessment
- Security/privacy assessment, only if applicable
- Questions for resolution
- Files consulted
```

Every issue must include evidence: file path, diff area, doc reference, or command output. If evidence is weak, mark it optional or omit it.

## What to Check Carefully

### Product Scope

Flag implementation that introduces out-of-scope features: physical interception, autopilot, navigation, motor control, flight control, hardware control, aiming, payload control, trajectory planning, real-world geolocation, autonomous engagement, RTSP/webcam/live-camera processing, Streamlit, Flask, Celery, Redis, model training from the web UI/API, complex enterprise RBAC, or multi-language UI.

### Component Boundaries

Flag any frontend PostgreSQL access, frontend shared-storage path access, frontend CV inference, backend-to-worker HTTP job-loop calls, worker-to-backend HTTP job polling, worker-owned public API routes for job processing, PostgreSQL binary media storage, or API responses that expose absolute host/container paths.

### Auth and Privacy

Flag missing backend role checks, missing ownership checks, public registration creating admins, inactive users allowed on protected routes, plain-text passwords, weak password hashing, broad CORS, secrets in logs, raw token logging, unsafe path handling, and downloads that do not re-check owner/admin access.

### Uploads, Storage, and Exports

Flag uploads that skip extension/MIME/size/category validation, raw user filenames controlling paths, path traversal risk, database fields storing absolute paths, result downloads exposing internal paths, missing CSV/JSON export contracts, and no-detection jobs treated as errors.

### Worker and CV Pipeline

Flag long media processing inside API requests, queue claims without row-level locking, transactions held open during processing, missing heartbeat/progress, stale jobs stuck forever, YOLO11 used without documented YOLO26 fallback justification, wrong model-selection priority, missing ByteTrack default, image detections with track IDs, bounding boxes not in original image-space pixels, or outputs that imply targeting/navigation/interception.

### Training and Experiments

Flag training launched from the web UI/API, code agents attempting multi-hour cloud sessions themselves, Seraphim replaced without approval for final metrics, Bird vs Drone treated as a second primary class, missing model cards, missing fallback metadata, or experiment metrics that require manually annotated tracking identities when docs exclude them.

### Frontend UX

Flag user-facing non-Ukrainian text, raw `null` values, blank charts without empty states, Matplotlib in the web UI, admin actions visible to regular users, protected routes available to guests, missing loading/error/empty states, `frame_stride` exposed in standard UI, absolute paths displayed, or UI text that presents CV results as targeting, navigation, or interception instructions.

## Command Wrapper Policy

Use plain commands unless a local wrapper is verified to preserve behavior. Prefer `rg` or `rg --files` for searches. Use Git inspection only when the checkout is a Git repository.

If a command, scaffold, or runtime file is not present yet, report `not available yet`, not `PASS`.

## File Size Review Heuristic

Use line counts as review heuristics, not absolute rules:

- 300+ LOC: check whether the file mixes responsibilities.
- 400+ LOC: request decomposition or require a clear justification.
- 500+ LOC: treat as an important issue unless the file is a migration, generated file, lock file, static fixture, notebook export, or cohesive table-driven test.

Request splitting only when it improves readability, reviewability, testability, or context efficiency.

## Context and Conflicts

- Keep investigations narrow: relevant docs first, changed code second.
- Use subagents only when the user explicitly asks for delegated or parallel agent work.
- Compact manually around 60% context fill and preserve touched docs, contracts, changed files, failed commands, pending questions, and verdict.
- If instructions conflict, stop and write `WARNING: CONFLICT` with exact files/rules involved.

## Do Not

- Do not implement source changes during review modes.
- Do not invent endpoints, schema fields, payloads, flows, formulas, statuses, UI labels, environment variables, or files.
- Do not duplicate long product rules from `docs/` into `.context/` unless needed to explain a specific decision.
- Do not modify original review files during resolution unless the user explicitly asks.
- Do not approve exposed PostgreSQL, exposed shared-storage paths, unsafe token handling, missing backend authorization, model-training-from-UI/API, worker API/job-loop coupling, unsupported model fallback, no-detection-as-error behavior, CV output beyond image-space data, or user-facing non-Ukrainian UI text.
