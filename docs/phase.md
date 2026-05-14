## Phase 26 - Frontend upload and processing page

**Direction:** Frontend
**Goal:** Implement media upload and processing-job creation UI.

### Scope

- Implement `/upload` page.
- Add drag-and-drop file upload.
- Show allowed file types and size guidance in Ukrainian.
- Show selected file preview or metadata where practical.
- Add model selector populated from backend.
- Add confidence threshold control.
- Add IoU threshold control.
- Add tracker selector for video jobs.
- Do not expose `frame_stride` in standard UI.
- Preselect defaults so users can process without changing settings.
- Create media upload request.
- Create processing job request.
- Show job status/progress block after job creation:
  - status badge;
  - progress bar;
  - percentage when available;
  - last update time when available.
- Add Ukrainian loading, error, success, and validation messages.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Upload page route is protected.
- Valid file can be uploaded.
- Job can be created with defaults.
- Invalid file, too-large file, unsupported type, and failed job creation show Ukrainian errors.
- `frame_stride` is not visible.
- Status block renders queued/processing/completed/failed states.
- Frontend build passes.

### Commit

`feat(frontend-upload): add media upload and processing creation flow`
