# Research - Phase 26 Frontend Upload and Processing Page

## Current Phase

Confirmed current phase from `docs/phase.md`:

- Phase 26 - Frontend upload and processing page
- Direction: Frontend
- Goal: Implement `/upload` page for media upload and processing-job creation UI

Risk level:

- Assumption: MEDIUM. User left risk placeholder unfilled; this phase connects frontend file upload, model selection, job creation, and status polling to protected backend APIs.

## Docs Consulted

Required first-read files:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase-relevant docs from `docs/phase.md`:

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

Implementation/prototype context consulted:

- `frontend/index.md`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/api/dashboard.ts`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/index.css`
- `frontend/src/test/auth-routes.test.tsx`
- `frontend/src/test/dashboard.test.tsx`
- `prototype/index.md`
- `prototype/upload.jsx`
- `prototype/styles.css`
- `backend/app/api/media.py`
- `backend/app/schemas/media.py`
- `backend/app/api/jobs.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/jobs.py`
- `backend/app/api/models.py`
- `backend/app/schemas/models.py`
- `backend/app/services/media.py`
- `backend/tests/test_jobs_api.py`
- `backend/tests/test_media_api.py`
- `backend/tests/test_media_validation.py`

## Confirmed Repository Facts

- Git checkout is dirty before this planning task. `git status --short` showed modified `.context/*` files and `docs/phase.md`.
- `.context/research.md`, `.context/design.md`, and `.context/plan.md` existed but were empty when inspected.
- `docs/phase.md` points to Phase 26 and lists only frontend/upload relevant docs.
- Production frontend exists under `frontend/` and is a Vite React TypeScript app.
- Prototype exists under `prototype/` and is a static mock UI reference only. Its `upload.jsx` shows the intended upload layout, file-selection behavior, controls, and status block.
- `frontend/package.json` confirms:
  - React 19, Vite 6, TypeScript, Tailwind CSS v3, shadcn baseline, React Router, TanStack Query.
  - `@radix-ui/react-icons` is installed.
  - `@phosphor-icons/react` and `framer-motion` are not installed.
- `frontend/src/App.tsx` routes `/upload` to placeholder `UploadPage` from `frontend/src/pages/placeholders.tsx`.
- `frontend/src/pages/DashboardPage.tsx` is implemented; `/upload`, `/jobs`, `/models`, `/experiments`, and `/admin` placeholders remain in `placeholders.tsx`.
- `frontend/src/api/client.ts` supports JSON and `FormData` requests with bearer token injection.
- Existing frontend tests cover auth routing and Phase 25 dashboard behavior. No upload-page test exists yet.
- Existing styling uses dark dashboard palette matching prototype: compact cards, `Space Grotesk`, `DM Sans`, `JetBrains Mono`, green accent, Tailwind utility classes, `av-card`, `av-input`, `av-label`, `av-skeleton`.

## Confirmed Backend/API Facts

- `POST /api/media` accepts multipart form data with key `file` and returns `MediaResponse`.
- `MediaResponse` fields include `id`, `user_id`, `original_filename`, `media_type`, `mime_type`, `file_size_bytes`, `width`, `height`, `frame_count`, `fps`, `duration_seconds`, `created_at`.
- Backend validates upload extension, MIME, size, filename safety, image/video metadata, generated storage path, and ownership.
- Accepted upload formats are:
  - Images: `.jpg`, `.jpeg`, `.png`, `.webp`
  - Videos: `.mp4`, `.avi`, `.mov`, `.mkv`
- Default documented size limits are 20 MB for images and 500 MB for videos; backend limits are configurable.
- `GET /api/models` lists authenticated-visible models and supports `limit`, `offset`, `is_active`, `model_family`, `variant`.
- `POST /api/jobs` accepts JSON `JobCreateRequest`:
  - `media_id`
  - optional `model_version_id`
  - optional `confidence_threshold`
  - optional `iou_threshold`
  - optional `tracker_type`
- `tracker_type` allowed values are `bytetrack` and `botsort`.
- Backend rejects `tracker_type` for image media.
- Backend default processing params are `confidence_threshold=0.25`, `iou_threshold=0.45`, `tracker_type=bytetrack`, `image_size=640`, `frame_stride=1`.
- `frame_stride` is internal. Backend rejects it in job-create payload because schema forbids extra fields.
- `GET /api/jobs/{job_id}` returns `JobDetailResponse` with `media`, `model`, and `result` references.
- Job statuses include `queued`, `processing`, `completed`, `failed`, and `cancelled`.

## Existing Implementation State

- Phase 24 auth scaffold and protected/admin route guards exist.
- Phase 25 authenticated shell and dashboard exist.
- Phase 26 upload page is not implemented yet; current route is a placeholder.
- There are no frontend API helpers for media upload or job creation yet.
- Existing `frontend/src/api/types.ts` already contains model/job list/detail types used by dashboard, but not `MediaResponse`, `MediaListResponse`, or job-create payload types.
- Existing `Button` and `Input` shadcn-style primitives exist.
- No select, slider, progress, toast, or alert-dialog shadcn primitives exist beyond current custom components, `Alert`, and CSS helpers.
- Prototype upload flow uses mock state and `alert`; production implementation must replace this with backend API calls and inline Ukrainian UI states.

## Unknowns And Assumptions

Confirmed facts:

- Backend is authorization authority.
- Frontend must call backend REST API only.
- Visible UI text must be Ukrainian.
- Frontend must not expose `frame_stride`.
- Frontend must not show raw `null` or unsafe absolute filesystem paths.

Assumptions:

- Risk level is MEDIUM because user did not specify a concrete value.
- Upload page should use existing `@radix-ui/react-icons`, not add new icon dependencies.
- No new third-party frontend dependency is needed for this phase.
- Client-side upload validation should mirror documented extension guidance for UX only; backend remains canonical validation.
- Default size guidance is image 20 MB and video 500 MB, but backend limits are configurable through `MAX_IMAGE_SIZE_MB` and `MAX_VIDEO_SIZE_MB`. Without a documented frontend config source, frontend may display these defaults as guidance and may surface backend "too large" failures safely in Ukrainian, but must not treat them as immutable product limits.
- Model selector should use `/api/models?limit=100`, preselect active model when present, and otherwise allow backend model-resolution error to surface safely in Ukrainian.
- After job creation, `/upload` should poll `GET /api/jobs/{job_id}` while status is `queued` or `processing`.
- If selected file is image, frontend should omit `tracker_type` from `POST /api/jobs`.
- If selected file is video, frontend should send `tracker_type` with lowercase API value (`bytetrack` or `botsort`).
- Selected file preview can be metadata and object URL preview where browser-safe; docs say preview or metadata "where practical."

Unknowns:

- Backend error `detail` values are English; upload page must map common status/detail values to Ukrainian without leaking raw unsafe backend text.
- Upload/job API failure tests must include an English/path-like backend `detail` and assert the raw detail is not rendered.
- No current frontend toast component exists; phase can use inline success/error state unless implementation adds a narrow local notification pattern.
- Whether browser preview should use `URL.createObjectURL` for video is not specified; safe metadata display plus optional preview is acceptable.
- `docs/phase.md` is modified in the worktree; current contents still identify Phase 26.

## Files Likely Relevant For Implementation

Likely frontend files to modify:

- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/api/types.ts`
- `frontend/src/index.css`

Likely frontend files to create:

- `frontend/src/pages/UploadPage.tsx`
- `frontend/src/api/upload.ts`
- `frontend/src/test/upload-page.test.tsx`

Reference-only files:

- `prototype/upload.jsx`
- `prototype/styles.css`

Likely verification files/commands:

- `frontend/package.json`
- `frontend/src/test/auth-routes.test.tsx`
- `frontend/src/test/dashboard.test.tsx`
- `npm run lint`
- `npm test`
- `npm run build`

Planning review resolution notes:

- Accepted Claude issue 1: size limits are configurable, so frontend must not make default 20 MB / 500 MB guidance an unqualified hard product rule unless backed by config.
- Accepted Claude issue 2: empty or failed model list must have explicit behavior. If no valid model is selectable, job creation should omit `model_version_id` and let backend model-resolution rules apply, while showing a safe Ukrainian notice.
- Accepted Claude issue 3: tests must prove raw backend error details are not displayed.
- Accepted Claude optional prototype check: manual smoke should compare production `/upload` against `prototype/upload.jsx` at desktop and narrow viewport.

No backend, database, CV worker, training, Docker, or product-doc source files are expected to change in this phase.
