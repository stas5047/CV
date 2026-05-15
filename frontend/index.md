# AeroVision - Frontend Index

## General Description

The `frontend/` folder contains the AeroVision React + TypeScript single-page application.

According to `../docs/`, this frontend will provide a Ukrainian-language dashboard-style interface for authentication, media upload, job creation, job status/results, detection and track tables, downloads, model registry views, experiment metrics, and admin-only pages. The frontend must call only the backend REST API and must not access PostgreSQL, shared storage paths, or CV inference directly.

## Current Files

| Path | Purpose |
|---|---|
| `.dockerignore` | Excludes local Node/build artifacts from frontend Docker build context. |
| `Dockerfile` | Frontend container build that installs dependencies, builds the Vite app with `VITE_API_BASE_URL`, and serves it through Vite preview on port 5173. |
| `package.json` / `package-lock.json` | npm dependency manifest and lockfile for the Vite React frontend. |
| `index.html` | Vite HTML entrypoint. |
| `vite.config.ts` / `vitest.config.ts` | Vite build/dev config and Vitest config. |
| `tsconfig*.json` | TypeScript project configuration. |
| `tailwind.config.ts` / `postcss.config.js` | Tailwind CSS v3 and PostCSS configuration. |
| `eslint.config.js` | ESLint flat config for TypeScript and React hooks. |
| `components.json` | shadcn/ui baseline configuration. |
| `src/` | React app source: API client, auth state, protected/admin routing, auth pages, authenticated shell, dashboard page, upload/jobs/models pages, UI primitives, tests, and styles. |
| `index.md` | Frontend folder summary, current contents, and frontend-local commands. |

The frontend currently implements Phase 31: Vite/React/TypeScript scaffold, Tailwind/shadcn baseline, typed auth API client, token-backed auth state, `/login`, `/register`, protected route wrapper, admin guard, authenticated shell, `/dashboard` metrics/recent-jobs page, `/upload` media upload and processing-job creation page, `/jobs` history/filter page, `/jobs/:jobId` details/results/download page, `/models` model registry page with admin registration/activation controls, `/experiments` experiment metrics page with Recharts charts and required empty states, `/admin` admin-only page with global stats, recent global jobs, model/experiment shortcuts, conservative storage cleanup, a basic users table, toast notifications for implemented success/error actions, and Phase 31 Ukrainian UX label/scope polish.

## Commands

| Command | Status |
|---|---|
| `npm install` | installs frontend dependencies |
| `npm run dev -- --port 5173` | starts Vite dev server |
| `npm run preview -- --host 0.0.0.0 --port 5173` | serves the built frontend locally after `npm run build` |
| `npm run lint` | runs ESLint |
| `npm test` | runs Vitest route/auth tests |
| `npm run build` | runs TypeScript build and Vite production build |
| Frontend Docker build | available through root `docker compose --env-file .env.example build frontend` |
