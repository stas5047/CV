## Phase 28 - Frontend model registry page

**Direction:** Frontend  
**Goal:** Implement model list and admin model-management actions.

### Scope

- Implement `/models` page.
- Display registered model versions with:
  - model name;
  - family;
  - variant;
  - active status;
  - dataset description;
  - key metrics;
  - model size when known.
- Allow regular users to view models only.
- Show admin-only actions only to admins:
  - register model;
  - activate model.
- Add admin model registration form using existing relative storage paths.
- Add activation flow and active-status update.
- Render missing metric values as Ukrainian placeholders or empty states, not raw `null`.
- Represent YOLO26 and documented YOLO11 fallback accurately.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Authenticated users can view model list.
- Regular users do not see admin mutation actions.
- Admin can register and activate model versions.
- Active model is visually clear.
- Missing metrics do not show raw `null`.
- Frontend build passes.

### Commit

`feat(frontend-models): add model registry page and admin actions`