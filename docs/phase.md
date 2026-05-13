## Phase 12 - Experiment import backend API

**Direction:** Backend / Admin / Experiments  
**Goal:** Implement imported experiment records and metrics without launching training from the app.

### Scope

- Implement endpoints:
  - `GET /api/experiments`;
  - `GET /api/experiments/{experiment_id}`;
  - `POST /api/experiments/import`.
- Restrict experiment import to admins.
- Regular users can view only published experiment runs.
- Admins can view all imported experiment runs.
- Support required experiment types:
  - model comparison;
  - confidence threshold analysis;
  - tracker behavior comparison;
  - false-positive analysis.
- Import structured metrics and artifact paths from existing files under storage.
- Allow `metric_value = null` for incomplete imports.
- Validate artifact paths as relative and safe.
- Ensure API and UI-facing data use tracker behavior wording, not absolute tracking accuracy.
- Add tests for import, published visibility, null metrics, role access, and path safety.

### Relevant docs

- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/FRONTEND_UX.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Admin can import experiment metadata and metrics.
- Regular users see only published experiments.
- Admins see unpublished experiments.
- Null metric values do not break API responses.
- Training cannot be launched from API routes.
- Experiment tests pass.

### Commit

`feat(backend-experiments): add experiment import and visibility API`