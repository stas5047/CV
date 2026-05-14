# Status - Phase 27 Frontend Jobs History and Job Details Pages

## Current state

- Implemented production `/jobs` route with user-scoped job listing, status/media/date filters, current-page filename search, pagination, loading/error/empty states, and detail links.
- Implemented production `/jobs/:jobId` route with polling for queued/processing jobs, progress/heartbeat display, safe failed-job messaging, authenticated result preview blobs, summary cards, parameters, downloads, detection table, and video-only track table.
- Added focused jobs API helpers, result/detection/track types, and authenticated blob download helper.
- Added shared Phase 27 job formatters and page parts.
- Wired real Phase 27 pages into `frontend/src/App.tsx`; later `/models`, `/experiments`, and `/admin` placeholders remain unchanged.
- Added frontend tests for jobs list, route protection, documented filters, details, downloads, no-detection, failed-state safety, and video/image track visibility.
- Updated `frontend/index.md` to current Phase 27 state.
- Resolved Phase 27 code review fixes:
  - removed `docs/phase.md` trailing whitespace flagged by diff check;
  - added `/jobs` model filter backed by `/api/models` and `model_version_id`;
  - replaced English `backend API` visible error copy with Ukrainian wording;
  - restricted authenticated blob downloads/previews to API-relative or same API origin/path URLs before attaching bearer tokens;
  - added regression coverage for model filter query params and external download URL blocking.

## Scope notes

- No backend, database, CV worker, training, Docker, product docs, research/design/plan, or review files were modified by this implementation.
- Frontend uses documented backend REST endpoints only: `/jobs`, `/jobs/{id}`, `/jobs/{id}/result`, `/jobs/{id}/detections`, `/jobs/{id}/tracks`, and result download URLs.
- `/jobs` uses regular jobs API, not `/admin/jobs`.
- `frame_stride` is not displayed.
- Downloads and previews use authenticated fetch/blob flow; UI never constructs storage paths.

## Verification

- `npm run lint`: PASS.
- `npm test`: PASS, 33 tests passed.
- `npm run build`: PASS.
- `git diff --check`: PASS.
- Dev-server HTTP smoke: PASS, Vite started at `http://localhost:5175/` because ports 5173 and 5174 were already occupied; `Invoke-WebRequest http://localhost:5173` returned 200 from an existing Vite server.
- Manual browser smoke: not available in this session because the Browser plugin's required Node REPL JavaScript tool is not exposed, and local Playwright packages are not installed.

## Security / privacy

- Backend remains authorization authority; frontend route guards are only UX.
- Frontend does not show backend raw failed-job internals, absolute paths, storage roots, tokens, `weights_path`, `null`, `undefined`, or `frame_stride`.
- Result downloads use backend URLs with bearer token fetch.
- Bearer token fetch is blocked for absolute external download URLs.
- CV output wording remains detection/tracking/image-space data only.

## Deviations / remaining risks

- No product-doc, design, plan, or review-resolution deviations.
- Manual visual comparison with `prototype/jobs.jsx` and `prototype/job-detail.jsx` remains blocked by unavailable browser automation tooling in this session; automated route/state coverage and build gates passed.
