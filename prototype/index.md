# AeroVision - Prototype Index

## General Description

The `prototype/` folder contains a static browser-loaded UX prototype for the AeroVision frontend.

According to `../docs/`, the production frontend must be a Ukrainian-language React + TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, and Recharts application that calls only the backend REST API. This prototype is a UI reference and interaction demo only. It uses React UMD, Babel-loaded JSX, CSS, and in-memory mock data to show the documented authentication, dashboard, upload, jobs, job detail, models, experiments, and admin screens.

This folder is not the production `frontend/` application, not a backend API client, not a CV worker, not a training workflow, and not part of the Docker Compose runtime. Prototype data and actions are mock/demo-only and must not be treated as product contracts; authoritative product behavior remains in `../docs/`.

## Current Files

| Path | Purpose |
|---|---|
| `AeroVision.html` | Static HTML entry point that loads CSS, React UMD, Babel, shared prototype modules, page modules, and `app.jsx` in dependency order. |
| `app.jsx` | Prototype application state, route switching, login state, role/empty-state/accent tweaks, and page composition. |
| `auth.jsx` | Mock login and registration screens with Ukrainian visible text, form validation states, and demo credential hints. |
| `sidebar.jsx` | Authenticated shell, desktop sidebar, mobile drawer navigation, role-based admin navigation visibility, and logout navigation. |
| `ui.jsx` | Shared prototype UI primitives such as status badges, metric cards, skeletons, empty states, headers, progress bars, tabs, tooltips, and toasts. |
| `icons.jsx` | Inline Lucide-style SVG icon components used by prototype pages and controls. |
| `tweaks-panel.jsx` | Reusable edit-mode/tweaks panel helpers for changing prototype role, accent color, empty-state mode, and route during visual review. |
| `styles.css` | Prototype-only CSS variables, layout, cards, buttons, forms, tables, badges, responsive rules, and visual styling. |
| `dashboard.jsx` | Mock dashboard page with summary metrics, active model card, activity chart, recent jobs, loading state, and empty state. |
| `upload.jsx` | Mock upload and processing page with file selection, validation hints, model/threshold/tracker controls, and simulated job progress. |
| `jobs.jsx` | Mock jobs/history page with filters, search, pagination, status badges, and empty/filter states. |
| `job-detail.jsx` | Mock job detail page with status/progress, safe error display, result preview placeholder, summaries, downloads, detections, tracks, and no-detection state. |
| `models.jsx` | Mock model registry page with model cards, YOLO26/YOLO11 fallback metadata display, admin-only registration form, and activation simulation. |
| `experiments.jsx` | Mock experiments and metrics page with model comparison, threshold analysis, tracker behavior comparison, false-positive analysis, and required missing-data empty state. |
| `admin.jsx` | Mock admin page with global stats, global recent jobs, model/experiment shortcuts, storage cleanup confirmation, and user table. |
| `index.md` | Prototype folder summary, current contents, and prototype-local commands. |

## Commands

| Command | Status |
|---|---|
| `Start-Process .\AeroVision.html` | opens the static prototype from `prototype/` on Windows |
| Prototype dependency install | not required; the prototype loads browser dependencies from CDN scripts in `AeroVision.html` |
| Prototype dev server | not available; the prototype is a static HTML/JSX reference |
| Prototype build | not available; production frontend build work belongs under `../frontend/` |
| Prototype tests | not available yet |

Do not add production frontend commands here until this folder is intentionally converted from a static prototype into a maintained application surface.
