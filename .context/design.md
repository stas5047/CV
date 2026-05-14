# Design - Phase 26 Frontend Upload and Processing Page

## Phase Goal

Build the production `/upload` page in the existing React/Vite frontend, based on the static `prototype/upload.jsx` UI, using only documented/backend-existing REST APIs to upload media, create a queued processing job, and show status/progress after creation.

## Intended Behavior From Docs

Confirmed behavior:

- `/upload` is a protected route.
- Page includes drag-and-drop file upload.
- Page shows allowed file types and size guidance in Ukrainian.
- Page shows selected file preview or metadata where practical.
- Page includes model selector populated from backend.
- Page includes confidence threshold control.
- Page includes IoU threshold control.
- Page includes tracker selector for video jobs.
- Page does not expose `frame_stride`.
- Defaults are preselected so a user can process without changing settings.
- Page creates media upload request, then processing job request.
- After job creation, page shows:
  - status badge;
  - progress bar;
  - percentage when available;
  - last update time when available.
- Page includes Ukrainian loading, error, success, and validation messages.
- UI must not show raw `null`, unsafe absolute filesystem paths, targeting/navigation/interception wording, or backend internals.
- Backend remains authorization, ownership, upload validation, parameter validation, and path-safety authority.

Confirmed API behavior:

- Upload media with `POST /api/media` multipart `FormData` key `file`.
- Load models with `GET /api/models`.
- Create job with `POST /api/jobs`.
- Poll job detail with `GET /api/jobs/{job_id}` while job is `queued` or `processing`.
- Job-create payload may include `media_id`, optional `model_version_id`, optional `confidence_threshold`, optional `iou_threshold`, optional `tracker_type`.
- Never send `frame_stride`.
- Send `tracker_type` only for video jobs.

## Architecture Decisions

Frontend decisions:

- Replace `/upload` placeholder with a real `UploadPage` component.
- Keep implementation inside frontend only; no backend/doc/product changes.
- Add a narrow upload API module that wraps existing `apiRequest`:
  - media upload through `FormData`;
  - model listing;
  - job creation;
  - job detail polling.
- Extend existing TypeScript API types for media upload and job creation using backend schemas as source.
- Use TanStack Query for model loading and job polling.
- Use local component state for selected file, drag state, threshold values, tracker choice, submission state, and current job ID.
- Use existing `@radix-ui/react-icons`; no new icon library.
- Do not add Framer Motion because it is not installed and this phase does not require it.
- Keep visual treatment aligned with prototype/current dashboard:
  - dark dashboard shell;
  - asymmetric two-column layout on desktop;
  - one-column responsive collapse on mobile;
  - compact cards, borders, skeletons, status badge, progress bar;
  - green accent, no purple/blue glow, no emoji.
- Use Tailwind v3 syntax only.

Upload flow:

1. User selects or drops one file.
2. Client validates extension for fast Ukrainian feedback and shows documented default size guidance. Size limits are backend-configurable, so frontend must not treat 20 MB / 500 MB as immutable product limits unless a documented frontend config source exists.
3. UI shows file name, type, size, and metadata/preview where practical.
4. User keeps defaults or changes model/threshold/tracker.
5. Submit uploads file to `POST /api/media`.
6. On successful media response, submit `POST /api/jobs`.
7. UI stores returned job ID and renders status block.
8. Query polls `GET /api/jobs/{job_id}` while status is `queued` or `processing`.
9. UI stops polling on `completed`, `failed`, or `cancelled`.
10. Completed job shows Ukrainian success and link to `/jobs/{job_id}`.

Parameter decisions:

- Default confidence threshold: `0.25`.
- Default IoU threshold: `0.45`.
- Default tracker: `bytetrack`.
- For image jobs, omit `tracker_type`.
- For video jobs, send selected tracker.
- For model selector:
  - fetch `/api/models?limit=100`;
  - preselect active model when present;
  - otherwise use first listed model when present;
  - if no models are available, show Ukrainian empty/error state and submit without `model_version_id` only if user proceeds; backend then resolves active/fallback or returns safe error;
  - if model loading fails, do not send stale IDs. Allow submit without `model_version_id` only with a safe Ukrainian notice that backend default model selection will be used, or block with a safe Ukrainian error if implementation cannot prevent stale selection.

## Backend Impact

None expected.

The phase consumes existing backend routes only:

- `POST /api/media`
- `GET /api/models`
- `POST /api/jobs`
- `GET /api/jobs/{job_id}`

No backend route, schema, authorization, upload validation, or job creation behavior should change.

## Frontend Impact

Touched surface:

- `/upload` route
- frontend API client types/helpers
- upload-specific component state and tests

Expected implementation files:

- Create `frontend/src/pages/UploadPage.tsx`
- Create `frontend/src/api/upload.ts`
- Create `frontend/src/test/upload-page.test.tsx`
- Modify `frontend/src/App.tsx`
- Modify `frontend/src/pages/placeholders.tsx`
- Modify `frontend/src/api/types.ts`
- Modify `frontend/src/index.css` only for reusable upload/progress helpers if existing utilities are insufficient

Visible UI text:

- Ukrainian only, except accepted technical labels: `YOLO`, `IoU`, `ByteTrack`, `BoT-SORT`, `FPS`, `CSV`, `JSON`.

## DB Impact

None expected.

Frontend never accesses PostgreSQL or shared storage internals.

## API Impact

No API contract changes.

Frontend request bodies must match existing backend schemas:

- `POST /api/media`: `FormData` with field `file`.
- `POST /api/jobs`: JSON using existing `JobCreateRequest` fields only.

Frontend response handling must not depend on internal storage paths.

## Security/Privacy Impact

Touched security/privacy concerns:

- Frontend route remains protected by existing `ProtectedRoute`.
- Upload validation in frontend is advisory only; backend remains canonical.
- Do not expose or accept client-provided storage paths.
- Do not display `weights_path`, stored paths, absolute host/container paths, tokens, or backend stack traces.
- Do not log selected file contents, tokens, passwords, or API error bodies.
- Do not display raw backend English errors directly when they may contain unsafe internals; map common failures to Ukrainian messages.
- Add negative tests for English/path-like backend `detail` values so raw internals are not rendered.
- Do not send `frame_stride`.
- Do not provide any UI text implying targeting, navigation, interception, aiming, or hardware control.

## Test Strategy

Frontend automated tests:

- Add upload route test rendering protected `/upload` with mocked auth and fetch.
- Verify allowed file guidance renders in Ukrainian.
- Verify unsupported extension shows Ukrainian error and does not call `/api/media`.
- Verify default size guidance is visible in Ukrainian. If implementation applies client-side size blocking, verify the source is documented/configured; otherwise verify backend too-large failures map to safe Ukrainian errors.
- Verify valid image:
  - sends `POST /api/media` with `FormData` key `file`;
  - sends `POST /api/jobs` with `media_id`, thresholds, optional model ID;
  - does not send `tracker_type`;
  - does not send `frame_stride`.
- Verify valid video:
  - tracker selector appears;
  - `tracker_type` sends lowercase API value (`bytetrack` or `botsort`).
- Verify model list loading/empty/error states render Ukrainian UI.
- Verify no-model selection creates a job payload without `model_version_id` when user proceeds, or shows a safe Ukrainian blocker without stale IDs.
- Verify failed model loading cannot send stale/invalid model IDs.
- Verify failed media upload/job creation with English/path-like backend `detail` renders a safe Ukrainian message and not the raw detail.
- Verify queued/processing/completed/failed job statuses render status block/progress in Ukrainian.
- Verify raw `null`, `undefined`, absolute paths, and `frame_stride` are absent from rendered UI.

Relevant quality gates:

- `npm run lint`
- `npm test`
- `npm run build`

Manual browser flow when implementation happens:

- Start frontend with `npm run dev -- --port 5173` and verify `/upload` at desktop and narrow viewport.
- Compare `/upload` desktop and narrow viewport against `prototype/upload.jsx` structure: two-column desktop layout, mobile single-column collapse, drag/drop zone, parameter panel, and status/progress block.
- If backend is running, perform one happy-path upload/job creation smoke.

## Ambiguities Or Conflicts

Conflicts:

- None found between Phase 26 docs and current backend/frontend implementation.

Ambiguities:

- User did not replace risk placeholder. Assumed MEDIUM.
- Docs require selected file preview or metadata "where practical"; implementation may choose metadata and safe object URL preview without guaranteeing browser video playback.
- Docs do not specify exact polling interval. Use conservative TanStack Query polling while status is `queued`/`processing`.
- Docs do not specify exact Ukrainian copy for upload errors. Copy should be concise, safe, and aligned with existing dashboard language.
- No current toast primitive exists. Inline states are acceptable unless implementation adds a small reusable toast pattern within this phase.
