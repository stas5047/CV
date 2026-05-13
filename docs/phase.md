## Phase 9 - Job creation API and model selection resolution

**Direction:** Backend  
**Goal:** Implement queued processing job creation with validated parameters and resolved model selection.

### Scope

- Implement `POST /api/jobs`.
- Validate that the media file exists, is not soft-deleted, and belongs to the requesting user.
- Validate processing parameters:
  - `model_version_id` when provided;
  - confidence threshold;
  - IoU threshold;
  - tracker type;
  - internal image size if configured;
  - internal `frame_stride = 1`.
- Resolve model selection priority:
  1. explicit job-specific model version;
  2. active model from `model_versions`;
  3. environment fallback only when no active database model exists.
- Store the resolved `model_version_id` on the job when possible.
- Create job with `status = queued`, input parameters, progress defaults, and ownership fields.
- Ensure long media processing does not happen inside the API request.
- Add tests for own media, another user's media, invalid params, missing active model, and model priority.

### Relevant docs

- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Users can create jobs for own uploaded media.
- Users cannot create jobs for another user's media.
- Invalid model, threshold, IoU, or tracker values are rejected.
- Created job status is `queued`.
- `frame_stride` is present internally but not exposed as a standard user-facing parameter.
- Model selection priority tests pass.

### Commit

`feat(backend-jobs): add queued job creation and model resolution`