# Plan - Phase 26 Frontend Upload and Processing Page

## Scope

Phase only:

- Implement production `/upload` page.
- Use existing backend REST APIs.
- Base frontend layout/interaction on `prototype/upload.jsx`.
- Keep all visible UI text Ukrainian.

Out of scope:

- Jobs history page.
- Job details page.
- Model registry management.
- Experiments page.
- Admin page.
- Backend, DB, CV worker, Docker, training, product docs.

## Ordered Atomic Plan

1. `@role/developer-frontend` Add upload API contract types.
   - Modify `frontend/src/api/types.ts`.
   - Add `MediaResponse`, `MediaListResponse`, `JobCreateRequest`, and any upload-page-only helper union types needed from existing backend schemas.
   - Verifiable: TypeScript knows media upload response and job-create payload fields; no `frame_stride` field exists in frontend job-create type.

2. `@role/developer-frontend` Add upload API helper module.
   - Create `frontend/src/api/upload.ts`.
   - Implement:
     - `uploadMedia(file: File)` -> `POST /media` with `FormData` key `file`.
     - `listModelsForUpload()` -> `GET /models?limit=100`.
     - `createProcessingJob(payload: JobCreateRequest)` -> `POST /jobs`.
     - `getProcessingJob(jobId: string)` -> `GET /jobs/{jobId}`.
   - Verifiable: mocked fetch sees exact paths and payload shapes.

3. `@role/developer-frontend` Add focused upload page tests before implementation.
   - Create `frontend/src/test/upload-page.test.tsx`.
   - Cover protected route render, file validation, valid image upload/job creation, valid video tracker payload, polling status block, Ukrainian errors, model empty/error behavior, safe API-error mapping, and absence of `frame_stride`/raw `null`.
   - Verifiable: tests fail against current placeholder because real controls/API calls do not exist.

4. `@role/developer-frontend` Replace route placeholder wiring.
   - Create `frontend/src/pages/UploadPage.tsx`.
   - Modify `frontend/src/App.tsx` to import `UploadPage` from new page file.
   - Remove only upload placeholder export/import from `frontend/src/pages/placeholders.tsx`; leave later-phase placeholders intact.
   - Verifiable: `/upload` route renders new page under existing `ProtectedRoute` and `AppShell`.

5. `@role/developer-frontend` Build upload page shell from prototype.
   - Implement page header, two-column desktop grid, mobile single-column collapse, drag/drop zone, hidden file input, and parameter panel.
   - Use current `av-card`, `av-label`, `Button`, `Input`, Tailwind v3, and `@radix-ui/react-icons`.
   - Verifiable: page resembles `prototype/upload.jsx` structure while fitting production shell.

6. `@role/developer-frontend` Implement client-side file selection validation.
   - Validate extension against `.jpg`, `.jpeg`, `.png`, `.webp`, `.mp4`, `.avi`, `.mov`, `.mkv`.
   - Show documented default size guidance: image <= 20 MB, video <= 500 MB.
   - Treat backend as canonical for size because `MAX_IMAGE_SIZE_MB` and `MAX_VIDEO_SIZE_MB` are configurable. Do not make default sizes an immutable blocking rule unless a documented frontend config source exists.
   - Show Ukrainian inline errors.
   - Clear existing job state when new file is selected.
   - Verifiable: invalid extension tests do not call upload API; backend too-large or client-configured too-large failures render Ukrainian errors.

7. `@role/developer-frontend` Implement selected-file metadata and practical preview.
   - Show sanitized browser filename, media type label, size, and available dimensions/duration after backend upload when known.
   - Use object URL preview only where safe and clean up URL on file change/unmount.
   - Show Ukrainian fallback when preview unavailable.
   - Verifiable: no raw `null`, `undefined`, or absolute path text appears.

8. `@role/developer-frontend` Implement model selector loading states.
   - Fetch models with TanStack Query.
   - Preselect active model when present, otherwise first listed model.
   - Render skeleton/loading, empty, and error states in Ukrainian.
   - If no valid model is selectable, do not send stale model IDs. On submit, omit `model_version_id` and let backend model-selection rules resolve the active/default model, while showing a safe Ukrainian notice. If model loading failed and implementation cannot prevent stale selection, block submit with a safe Ukrainian error.
   - Do not display `weights_path`.
   - Verifiable: tests cover loaded, empty, and failed model list; no-model job payload omits `model_version_id` or submit blocks safely; rendered UI does not show storage paths.

9. `@role/developer-frontend` Implement processing controls.
   - Confidence slider/input default `0.25`, range `0` to `1`.
   - IoU slider/input default `0.45`, range `0` to `1`.
   - Video-only tracker selector with `bytetrack` default and `botsort` alternative.
   - Hide tracker selector for image files.
   - Verifiable: image job payload omits `tracker_type`; video job payload includes selected lowercase tracker.

10. `@role/developer-frontend` Implement submit flow.
    - Disable submit when no file, extension validation error, upload/job request pending, or current job is queued/processing. Model query loading may disable submit, but empty model list must not force stale model selection.
    - On submit: upload media first, then create job.
    - Job payload includes only documented fields.
    - Map common backend errors to safe Ukrainian messages.
    - Never display raw backend `detail` values directly when they are English, stack-like, token-like, or path-like.
    - Verifiable: mocked valid file sends `POST /api/media`, then `POST /api/jobs`; no `frame_stride` in request body; English/path-like backend errors are not rendered raw.

11. `@role/developer-frontend` Implement status/progress block.
    - After job creation, show job ID, Ukrainian status badge, progress bar, percentage, and last update time when available.
    - Poll `GET /api/jobs/{jobId}` while status is `queued` or `processing`.
    - Stop polling for `completed`, `failed`, or `cancelled`.
    - Completed state links to `/jobs/{jobId}`.
    - Failed/cancelled state shows safe Ukrainian message.
    - Verifiable: tests transition queued -> processing -> completed/failed.

12. `@role/developer-frontend` Add narrow styling only if needed.
    - Modify `frontend/src/index.css` only for reusable upload/progress helpers not expressible cleanly with current utilities.
    - Keep palette aligned with prototype/current app: dark neutral surfaces, green accent, compact cards, no neon/purple/glow, no emoji.
    - Verifiable: CSS remains Tailwind v3-compatible and no `h-screen` full-height section is introduced.

13. `@role/tester` Run focused frontend checks.
    - From `frontend/`, run `npm run lint`.
    - From `frontend/`, run `npm test`.
    - From `frontend/`, run `npm run build`.
    - Verifiable: each command returns PASS or documented FAIL with exact cause.

14. `@role/tester` Do manual responsive/upload smoke when runtime is available.
    - Start frontend with `npm run dev -- --port 5173`.
    - Open `/upload` as authenticated user.
    - Check desktop and narrow viewport layout.
    - Compare against `prototype/upload.jsx` for intended upload layout, controls, and status block.
    - If backend is running, upload a small valid image and create a job.
    - Verifiable: route protected, layout usable, job status block appears.

15. `@role/code-reviewer` Audit final diff against docs.
    - Check `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/AUTH_SECURITY.md`, `docs/CV_PIPELINE.md`, and `docs/TESTING_QA.md`.
    - Verify Ukrainian visible text, no `frame_stride`, no raw `null`, no unsafe paths, no frontend storage/DB/CV access, no out-of-scope CV wording, and backend auth remains source of truth.
    - Verifiable: review notes no product-doc mismatch or lists exact required fixes.

## Quality Gates For This Phase

- `cd frontend; npm run lint`
- `cd frontend; npm test`
- `cd frontend; npm run build`

Manual gate when backend/dev server available:

- authenticated `/upload` browser smoke with valid image upload/job creation

## Security/Privacy Checks

- Frontend does not send or expose `frame_stride`.
- Frontend does not display `weights_path`, internal stored paths, absolute filesystem paths, tokens, or raw backend internals.
- Frontend does not let client-side validation replace backend validation.
- Frontend does not hard-code backend-configurable upload size limits as immutable product rules unless backed by documented frontend config.
- Frontend maps raw backend error details to safe Ukrainian messages before display.
- Frontend uses existing bearer-token API client only.
- Frontend does not add targeting, navigation, interception, aiming, payload, or hardware-control wording.

## Docs/Index Updates

Skip product docs. This phase does not change documented commands, env vars, file paths, product behavior, or setup flow.

Update `frontend/index.md` only if implementation creates/renames frontend files and workflow rules require component index freshness. This planning-only task does not update it.

## Remaining Risks

- Backend may return English `detail` strings; upload page must map them to safe Ukrainian messages.
- Model list can be empty or fail to load; implementation must omit `model_version_id` safely or block without stale IDs.
- Browser preview support differs by codec/container; metadata plus fallback notice is acceptable.
- Full upload smoke requires running backend with auth and model setup; automated frontend tests should mock APIs when backend is unavailable.
