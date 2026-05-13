## Phase 8 - Model registry backend API

**Direction:** Backend / Admin  
**Goal:** Implement model registry records, active model management, and model path validation.

### Scope

- Implement endpoints:
  - `GET /api/models`;
  - `GET /api/models/{model_id}`;
  - `POST /api/models`;
  - `PATCH /api/models/{model_id}/activate`.
- Allow all authenticated users to view model versions.
- Restrict model registration and activation to admins.
- Register existing relative weights paths under model storage.
- Validate model family: `YOLO26` or documented fallback `YOLO11`.
- Validate `weights_path` as relative and inside model storage.
- Store dataset, split, metrics, variant, and active state metadata.
- Ensure only one model version is active at a time.
- Do not implement large `.pt` upload through the web UI unless explicitly approved later.
- Add tests for role access, active-model uniqueness, and relative paths.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Authenticated users can list models.
- Regular users cannot register or activate models.
- Admin can register a model version using an existing relative path.
- Admin can activate exactly one model version.
- YOLO11 fallback metadata is represented accurately when used.
- Absolute or traversal paths are rejected.

### Commit

`feat(backend-models): add model registry and active model management`