# Design - Phase 27

## Phase goal

Implement production frontend `/jobs` and `/jobs/:jobId` pages based on the static prototype look, using only documented backend REST APIs and preserving Ukrainian dashboard UX.

## Intended behavior from docs

Confirmed:

- `/jobs` is protected and shows processing jobs visible to the current user.
- Regular users see only their own jobs. Admin global job history belongs in admin routes/pages, not this phase.
- Jobs table must show status badge, media type, original filename, model version, created date, processing duration, detections count, average confidence, filters, and link to details.
- Recommended filters: status, media type, date, model where practical.
- `/jobs/:jobId` is protected and shows job status, original media metadata, processed media preview, summary cards, detection table, track summary table for video, download annotated media, download CSV, download JSON, failed-job error area, progress bar, and last heartbeat/update time when available.
- Queued/processing jobs should poll status and update UI.
- Completed no-detection jobs show Ukrainian empty state, not error, and keep downloads where backend marks outputs available.
- Processed video preview may be unavailable; UI must show Ukrainian notice and keep download.
- Detection table must include frame index, timestamp, class, confidence, bounding box, and track ID.
- Track table is for video jobs only and must not imply physical trajectory.
- Visible UI text must be Ukrainian. Technical labels such as `FPS`, `YOLO`, `CSV`, `JSON`, `Track ID`, and `Bounding box` may remain readable.
- UI must not display raw `null`, `undefined`, unsafe absolute paths, or `frame_stride`.
- API/file outputs stay CV-only: image-space detections, confidence, timestamps, track IDs, model data, and performance metrics only.

## Architecture decisions

- Keep frontend as REST client only. No PostgreSQL, shared storage, or direct CV inference access.
- Replace placeholder route components with real page modules imported by `App.tsx`.
- Add `frontend/src/api/jobs.ts` as focused Phase 27 API client for jobs, results, detections, tracks, and authenticated downloads.
- Extend `frontend/src/api/types.ts` with doc/backend-confirmed response types only:
  - job result references/metadata;
  - detection response/list;
  - track response/list;
  - optional query/filter parameter types.
- Reuse `apiRequest` for JSON. Add a local authenticated download helper that uses `fetch`, `Authorization: Bearer`, blob URLs, and safe generated filenames from job id/kind. Do not expose backend storage paths.
- Use the same authenticated blob pattern for processed media preview when backend marks image/video output available. Create object URLs only from protected backend responses, revoke them on cleanup/page change, and show a Ukrainian unavailable-preview notice when browser preview cannot be provided.
- Use TanStack Query for jobs list, job details, result metadata, detections, and tracks.
- Poll `/api/jobs/{job_id}` while status is `queued` or `processing`; include summary/result/detections refresh after completion where needed.
- Use existing Tailwind v3 and shadcn-style primitives. Use `@radix-ui/react-icons` because dependency exists. Do not add Framer Motion or Phosphor.
- Match prototype UI with production Tailwind: compact filter bar, status chips, scrollable data tables, no-detection empty state, failed error banner, preview panel, summary side column, download bar, and pagination.
- Keep design-taste constraints within existing app style:
  - no emojis;
  - no pure black or purple/blue glow;
  - dark neutral dashboard with single green accent already present;
  - grid layouts, no complex flex math;
  - `min-h-[100dvh]` stays in shell;
  - mobile collapses to single column with horizontal table scroll;
  - active/hover tactile feedback via transform/opacity only.

## Frontend impact

- `/jobs` becomes a functional protected route.
- `/jobs/:jobId` becomes a functional protected route.
- `App.tsx` imports real jobs pages instead of placeholders for these two routes.
- Jobs page adds:
  - status filter;
  - media type filter;
  - local filename search only across the currently loaded page of results, with UI wording that does not imply whole-history search;
  - optional date range filter if query params remain simple;
  - optional model filter only if backed by `/api/models`;
  - pagination via `limit`/`offset`;
  - loading skeleton;
  - Ukrainian empty and no-results states;
  - safe API error state with retry.
- Job details page adds:
  - breadcrumb/back action;
  - polling status panel;
  - failed safe error block that does not echo raw backend internals;
  - authenticated media preview via blob URL with object URL cleanup, or unavailable-preview notice;
  - summary cards;
  - parameter/metadata panel;
  - download buttons respecting backend `available`;
  - detections table with pagination-safe initial page;
  - tracks table for videos only;
  - no-detection and no-track empty states.

## Backend impact

- No backend code changes planned.
- Frontend consumes existing documented/backend-confirmed endpoints only.

## DB impact

- No database changes planned.

## API impact

- No API contract changes planned.
- Client must align with existing paths and response shapes from `backend/app/schemas/jobs.py`.
- Client query params must be limited to documented/backend-confirmed params:
  - jobs: `limit`, `offset`, `status`, `media_type`, `model_version_id`, `created_from`, `created_to`;
  - detections: `limit`, `offset`, `frame_index`, `min_confidence`, `max_confidence`, `track_id`.

## Security/privacy impact

- Backend remains authorization authority.
- Frontend must not reveal raw `error_message` if it contains internal paths or stack details. Show safe Ukrainian wording; optionally show generic failed-processing message.
- Downloads must use backend download endpoints and never display or construct storage paths.
- Download helper must not log tokens or response data.
- UI must not show `weights_path`, absolute paths, raw API tracebacks, tokens, passwords, or storage roots.
- Admin visibility is unchanged; Phase 27 should not add admin global history to `/jobs`.

## Test strategy

- Add frontend tests for `/jobs`:
  - protected route renders jobs table from `/api/jobs`;
  - status/media/date filters call confirmed query params;
  - table shows status badges in Ukrainian;
  - empty state and filtered-empty state render Ukrainian text;
  - raw `null`, `undefined`, storage paths, and `frame_stride` are absent;
  - detail link points to `/jobs/{id}`.
- Add frontend tests for `/jobs/:jobId`:
  - fetches detail/result/detections/tracks using confirmed endpoints;
  - queued/processing jobs show progress and polling behavior;
  - completed job shows summaries, detections, tracks, and download buttons;
  - no-detection completed job shows empty state, not error, with download actions when available;
  - failed job shows safe Ukrainian error and hides raw backend internals;
  - image job does not show track summary table as required data;
  - video preview-unavailable notice appears when relevant.
- Relevant gates for implementation phase:
  - `cd frontend; npm run lint`
  - `cd frontend; npm test`
  - `cd frontend; npm run build`
- Manual browser smoke, when implementation occurs:
  - `/jobs` desktop/narrow viewport visual check;
  - `/jobs/:jobId` completed/no-detection/failed/processing states;
  - authenticated downloads trigger without exposing absolute paths.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found among consulted docs and inspected implementation.
- Prompt used placeholders for phase and risk; this contract uses `docs/phase.md` for phase and records `MEDIUM` as an assumption.
- Prototype contains mock data and inline styles; it is a visual reference only. Product/API behavior comes from docs and backend schemas.
- Model filter is "where practical"; avoid a fake model filter if it requires extra behavior not already available.
- Result preview may require authenticated blob fetching because backend downloads require JWT. This is implementation detail, not API change.
