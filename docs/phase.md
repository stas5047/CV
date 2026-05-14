## Phase 25 - Frontend dashboard and authenticated shell

**Direction:** Frontend
**Goal:** Implement the dashboard-style authenticated layout and main dashboard.

### Scope

- Implement responsive authenticated shell/navigation.
- Add navigation items:
  - Dashboard;
  - Upload;
  - Jobs;
  - Models;
  - Experiments;
  - Admin only for admins.
- Hide authenticated navigation from guests.
- Hide admin navigation from regular users.
- Implement `/dashboard`.
- Display:
  - total processed files;
  - total detections;
  - average confidence;
  - average FPS;
  - active model;
  - recent processing jobs;
  - quick upload action.
- Use cards, badges, tables, skeletons, and polished dashboard components.
- Handle missing data gracefully and never show raw `null`.
- Keep all visible UI text Ukrainian.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Dashboard route is protected.
- Regular user dashboard shows user-scoped data.
- Admin dashboard can show global statistics where backend supports it.
- Missing data renders Ukrainian empty/placeholder states.
- Admin navigation is visible only to admins.
- Frontend build passes.

### Commit

`feat(frontend-dashboard): add Ukrainian shell navigation and dashboard`
