# Phase 25 Design

## Phase Goal

Implement Phase 25 only: responsive authenticated shell/navigation and `/dashboard` page for the Ukrainian React frontend, based on product docs and the static prototype visual reference.

## Intended Behavior From Docs

Confirmed behavior:

- Protected dashboard shell is visible only to authenticated users.
- Guests do not see authenticated dashboard navigation.
- Navigation includes:
  - Dashboard
  - Upload
  - Jobs
  - Models
  - Experiments
  - Admin only for admins
- Admin navigation must be hidden from regular users.
- `/dashboard` must show:
  - total processed files
  - total detections
  - average confidence
  - average FPS
  - active model
  - recent processing jobs
  - quick upload action
- Regular users see their own statistics.
- Admins can see global statistics where backend supports it.
- Missing data renders Ukrainian empty/placeholder states.
- No raw `null` appears in UI.
- Visible UI text is Ukrainian. Technical labels like `FPS`, `YOLO`, `CSV`, and `JSON` may stay English.
- Frontend must call only backend REST API.
- Backend authorization remains source of truth.

Prototype visual contract:

- Keep dark, compact, work-focused dashboard style.
- Keep 56px desktop icon sidebar, divider lines, active accent rail, tooltip behavior where practical, and mobile drawer.
- Use compact metric cards, dark bordered surfaces, 6-8px radii, muted grid/table borders, mono numeric values, and green accent.
- Dashboard layout should mirror prototype:
  - page header with quick upload action
  - 4 metric cards
  - active model panel plus activity/summary panel
  - recent jobs table with status badges
  - skeleton loading state
  - empty state with upload action
- Motion stays modest: CSS transitions, skeleton shimmer, status pulse. No `framer-motion` because package is not installed and Phase 25 does not require new dependency.

## Architecture Decisions

- Keep frontend-only scope. No backend, database, worker, or product-doc changes.
- Replace dashboard placeholder with a real dashboard page.
- Keep React Router route `/dashboard`; do not add routes.
- Use TanStack Query for dashboard data fetching.
- Use existing `apiRequest` and token storage for API calls.
- Add typed frontend API models matching existing backend schemas:
  - jobs list/detail fields used by dashboard
  - model list fields used for active model
  - admin stats fields used for admin dashboard
- Derive dashboard view model in frontend helpers:
  - regular user: use `GET /api/jobs` and `GET /api/models?is_active=true&limit=1`
  - admin: use `GET /api/admin/stats`, `GET /api/admin/jobs?limit=5`, and `GET /api/models?is_active=true&limit=1`
- Metric derivation rules:
  - total processed files means completed jobs only; use `jobs.by_status.completed` for admins when present, and count visible completed jobs for regular users;
  - total detections may use `admin.stats.detections.total` for admins and completed-job summaries for regular users when numeric summary data exists;
  - average confidence and average FPS must be derived only from available completed-job `summary_json` numeric values;
  - if a required value cannot be derived from available data, show a Ukrainian unavailable placeholder instead of substituting total jobs, total media, recent-row averages, or mock values.
- For regular users, use only available visible jobs. If exact aggregate cannot be known from returned data, show available data or Ukrainian placeholder; do not invent totals.
- Format all missing values through helpers: never render `null`, `undefined`, absolute paths, or raw JSON.
- Do not display `weights_path` or any storage-like model path from model API responses on the dashboard.
- Regular-user dashboard code must not call `/api/admin/*`; admin endpoints are used only after authenticated user role is admin.
- Use Radix icons only, because installed dependency matches design-skill allowed icon path.
- Keep Tailwind v3 syntax only.

## Frontend Impact

- `/dashboard` changes from placeholder to real page.
- Authenticated shell may be polished to better match prototype:
  - active state for nested `/jobs/:jobId`
  - compact sidebar icon tooltips
  - mobile drawer consistent with prototype
  - role-safe admin nav
- Dashboard adds loading, error, empty, and success states.
- Frontend tests add coverage for:
  - protected dashboard route
  - admin nav visibility
  - dashboard loading/empty/error states
  - dashboard uses mocked user/admin API data
  - no raw `null`

## Backend Impact

- None planned.
- Existing backend endpoints are consumed only.
- No route, schema, or auth behavior changes.

## DB Impact

- None.

## API Impact

- None planned.
- Frontend uses existing endpoints only:
  - `GET /api/jobs`
  - `GET /api/admin/jobs`
  - `GET /api/admin/stats`
  - `GET /api/models`

## Security/Privacy Impact

- Frontend must not weaken security:
  - no admin nav for regular users
  - no guest navigation
  - no backend authorization bypass assumptions
  - no display of tokens, secrets, absolute paths, password data, or unsafe backend internals
- API errors shown as safe Ukrainian messages.
- Logout continues to remove local token.

## Test Strategy

Relevant checks only:

- `cd frontend; npm run lint`
- `cd frontend; npm test`
- `cd frontend; npm run build`

Frontend test scenarios:

- Guest visiting `/dashboard` redirects to login.
- Regular authenticated user sees dashboard shell without admin nav.
- Admin authenticated user sees admin nav and admin/global dashboard data where mock API supports it.
- Dashboard renders metric cards, active model, quick upload action, recent jobs.
- Empty jobs/model data renders Ukrainian empty/placeholder states.
- Failed dashboard API request renders Ukrainian error state.
- Raw `null` does not appear.
- Active model UI does not display `weights_path` or storage paths.
- Regular-user dashboard fetch path does not call `/api/admin/*`.

Manual browser check, required during implementation unless tooling is genuinely unavailable:

- Start Vite dev server if needed.
- Check `/dashboard` on desktop and narrow viewport.
- Compare against `prototype/AeroVision.html` dashboard/shell reference.
- If skipped, record the exact unavailable tool or startup blocker.

## Ambiguities Or Conflicts

- No `WARNING: CONFLICT` found between current phase docs.
- Ambiguity: docs require user-scoped dashboard totals, but existing API has no dedicated user aggregate stats endpoint and admin stats does not include average confidence/FPS. Phase 25 should not invent backend API. Use visible jobs and placeholders for regular users; use `GET /api/admin/stats` only for exact admin count stats.
- Ambiguity: prototype nav labels differ slightly from docs wording. Product docs define routes and visibility; prototype defines visual treatment. Ukrainian labels can follow product meaning while staying visually prototype-aligned.
- Ambiguity: prototype includes mock activity chart data. Production dashboard must not copy mock numbers as real data. Activity panel can use available job data or show empty state.
