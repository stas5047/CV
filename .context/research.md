# Research - Phase 27

## Current phase

- Phase 27 - Frontend jobs history and job details pages.
- Direction: Frontend.
- Risk: MEDIUM assumption. Prompt risk value was placeholder only; phase touches protected user-owned results, polling, downloads, and CV-only display boundaries.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`
- Existing workflow context checked: `.context/status.md`, `.context/review-plan-resolution.md`, `.context/review-plan-claude.md` were present but empty in current checkout.

## Confirmed repository facts

- Git checkout is dirty before this planning work:
  - modified `.context/design.md`
  - modified `.context/plan.md`
  - modified `.context/research.md`
  - modified `.context/review-code-openai.md`
  - modified `.context/review-code-resolution.md`
  - modified `.context/review-plan-claude.md`
  - modified `.context/review-plan-resolution.md`
  - modified `.context/status.md`
  - modified `docs/phase.md`
- `docs/phase.md` exactly identifies Phase 27 and lists only `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/CV_PIPELINE.md`, and `docs/TESTING_QA.md` as relevant docs.
- `frontend/package.json` confirms React 19, Vite 6, TypeScript, Tailwind CSS v3, React Router 7, TanStack Query 5, Recharts, and `@radix-ui/react-icons`.
- `frontend/package.json` does not include `framer-motion` or `@phosphor-icons/react`; Phase 27 should use existing `@radix-ui/react-icons` unless a later approved change adds dependencies.
- `frontend/src/App.tsx` already routes `/jobs` and `/jobs/:jobId` but both use placeholder components from `frontend/src/pages/placeholders.tsx`.
- `frontend/src/pages/placeholders.tsx` still contains placeholders for `JobsPage` and `JobDetailsPage`.
- `frontend/src/api/types.ts` already defines `JobStatus`, `JobDetail`, `JobListResponse`, `MediaResponse`, `ModelVersion`, and admin stats types. It does not yet define frontend types for result metadata, detections, tracks, or paginated detection/track responses.
- `frontend/src/api/client.ts` centralizes authenticated API calls and safe `ApiError` behavior.
- `frontend/src/api/dashboard.ts` and `frontend/src/api/upload.ts` already call `/jobs`, `/jobs/{id}`, `/models`, `/admin/jobs`, and job creation APIs.
- `frontend/src/pages/DashboardPage.tsx` has useful existing formatting/status patterns and links recent jobs to `/jobs/{job.id}`.
- `frontend/src/pages/UploadPage.tsx` already polls created jobs while queued/processing and links completed jobs to `/jobs/{id}`.
- `frontend/src/layout/AppShell.tsx` already marks `/jobs` navigation active for `/jobs` and `/jobs/:jobId`.
- `prototype/index.md` states prototype is UI reference only, not product contract.
- `prototype/jobs.jsx` shows intended visual shape for jobs list: filter bar, search, status chips, table, empty/filter states, pagination, row/detail navigation.
- `prototype/job-detail.jsx` shows intended visual shape for details: breadcrumb, active progress, failed error banner, media preview placeholder, summary cards, parameters, downloads, detections table, tracks table, no-detection state.
- `frontend/index.md` says frontend currently implements through Phase 26 and later routes remain placeholders.
- Backend routes for Phase 27 are already implemented in `backend/app/api/jobs.py` and `backend/app/services/results.py`.
- Backend job/result endpoints available:
  - `GET /api/jobs`
  - `GET /api/jobs/{job_id}`
  - `GET /api/jobs/{job_id}/summary`
  - `GET /api/jobs/{job_id}/detections`
  - `GET /api/jobs/{job_id}/tracks`
  - `GET /api/jobs/{job_id}/result`
  - `GET /api/jobs/{job_id}/download/media`
  - `GET /api/jobs/{job_id}/download/csv`
  - `GET /api/jobs/{job_id}/download/json`
- Backend list filters confirmed in `backend/app/api/jobs.py`: `limit`, `offset`, `status`, `media_type`, `model_version_id`, `owner_id`, `created_from`, `created_to`.
- Backend detection filters confirmed in `backend/app/api/jobs.py`: `limit`, `offset`, `frame_index`, `min_confidence`, `max_confidence`, `track_id`.
- Backend job details include `result` references with availability flags and download URLs. Backend responses intentionally omit raw storage paths.

## Existing implementation state

- Production frontend has authenticated shell, protected routing, dashboard, upload/job creation, upload polling, safe error wording, and existing UI helpers.
- Phase 27 jobs list/detail are not implemented in production frontend; current pages are placeholders.
- Frontend API layer lacks job-history/result helpers beyond `getProcessingJob`.
- Frontend tests exist for auth routes, dashboard, and upload. There are no Phase 27 jobs/detail tests yet.
- Current production styling already mirrors prototype dark dashboard theme: compact cards, tables, Radix icons, Tailwind v3, Space Grotesk/DM Sans/JetBrains Mono, emerald-green accent, skeleton shimmer, `min-h-[100dvh]`.
- Backend/API contract for Phase 27 appears available and doc-consistent from inspected files.

## Unknowns and assumptions

- Assumption: Use only existing dependencies and `@radix-ui/react-icons`; no new package install for this phase.
- Assumption: Downloads can be implemented as authenticated `fetch` calls using bearer token, then browser blob download, because plain anchor navigation would not attach auth header.
- Assumption: Browser preview should use result metadata `download_url` for image/video only when available. If auth header is required for direct media `src`, implementation should fetch blob URLs rather than expose raw paths.
- Assumption: Jobs list can use backend pagination with `limit`/`offset`; filter UI can map to documented/backend filters without inventing new API behavior.
- Assumption: Model filter can be implemented with existing job `model_version_id` query only if models are fetched from `/api/models`; otherwise omit or defer model filter UI to avoid fake values.
- Assumption: Date filter should use `created_from`/`created_to` query params if implemented; keep it simple and optional because docs say filters are recommended/where practical.
- Unknown: Whether result media returned by backend has browser-preview-friendly content type. Docs allow video preview unavailable notice; design must keep download action available.
- Unknown: Exact `summary_json` keys are partly flexible. Existing frontend already reads multiple known names; Phase 27 should use defensive extraction and never display raw `null`.
- Unknown: Current shell output shows mojibake for Ukrainian strings; this may be console encoding rather than file content. Implementation should preserve source file encoding and visible Ukrainian text.
- Unknown: Prompt phase number/title and risk level were placeholders. Current phase and risk assumption are documented above.

## Files likely relevant for implementation

- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/UploadPage.tsx`
- `frontend/src/pages/upload/UploadPageParts.tsx`
- `frontend/src/api/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/dashboard.ts`
- `frontend/src/api/upload.ts`
- new likely file: `frontend/src/api/jobs.ts`
- new likely file: `frontend/src/pages/JobsPage.tsx`
- new likely file: `frontend/src/pages/JobDetailsPage.tsx`
- optional new likely file: `frontend/src/pages/jobs/jobFormatters.ts`
- optional new likely file: `frontend/src/pages/jobs/JobPageParts.tsx`
- optional new likely tests: `frontend/src/test/jobs-page.test.tsx`, `frontend/src/test/job-details-page.test.tsx`
- prototype reference: `prototype/jobs.jsx`
- prototype reference: `prototype/job-detail.jsx`
- prototype reference: `prototype/styles.css`
- backend contract reference only: `backend/app/schemas/jobs.py`
- backend contract reference only: `backend/app/api/jobs.py`
