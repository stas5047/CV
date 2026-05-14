# Phase 25 Research

## Current Phase

- Current phase: Phase 25 - Frontend dashboard and authenticated shell.
- Direction: Frontend.
- Goal from `docs/phase.md`: implement dashboard-style authenticated layout and main dashboard.
- Risk level: MEDIUM, inferred because user left risk placeholder and phase touches protected UI, role visibility, API integration, and prototype-based visual parity.

## Docs Consulted

Read first:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Relevant docs from current phase:

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

Additional user-required UI reference:

- `prototype/index.md`
- `prototype/dashboard.jsx`
- `prototype/sidebar.jsx`
- `prototype/ui.jsx`
- `prototype/styles.css`

## Confirmed Repository Facts

- Git checkout is dirty before this planning work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Frontend stack exists under `frontend/` with React 19, TypeScript, Vite, Tailwind CSS v3, shadcn baseline, React Router, TanStack Query, Recharts, and Radix icons.
- `@radix-ui/react-icons` is installed. `@phosphor-icons/react` and `framer-motion` are not installed.
- Tailwind config already uses dashboard-appropriate fonts: `Space Grotesk`, `DM Sans`, and `JetBrains Mono`.
- `frontend/src/index.css` already uses dark dashboard tokens aligned with prototype colors: off-black background, dark surfaces, muted borders, green accent, mono numeric styling.
- Existing frontend implements Phase 24 auth/routing scaffold:
  - `frontend/src/App.tsx`
  - `frontend/src/layout/AppShell.tsx`
  - auth context/provider/guards
  - login/register pages
  - placeholder protected pages
  - frontend auth/route tests
- Current `AppShell` already has a compact desktop sidebar, mobile top bar/drawer, user email display, logout, and admin-only nav visibility.
- Current dashboard route is a placeholder in `frontend/src/pages/placeholders.tsx`.
- Existing backend exposes the API needed for this phase:
  - `GET /api/jobs`
  - `GET /api/models`
  - `GET /api/admin/stats`
  - `GET /api/admin/jobs`
- `GET /api/jobs` returns user-visible jobs for regular users and broader jobs for admins where permissions allow; response includes media/model references, `summary_json`, status/progress, timestamps, and download refs.
- `GET /api/models?is_active=true` can identify the active model.
- `GET /api/admin/stats` gives exact global admin count stats for users, media, jobs by status, detections, tracks, models, and experiments. It does not expose average confidence or average FPS.
- `GET /api/admin/jobs` returns recent/detail job rows, but a limited recent list must not be used to invent global dashboard averages.
- `GET /api/models` responses include `weights_path`; the dashboard must not display this storage path.
- No dedicated user-scoped dashboard stats endpoint was found.
- Prototype is static UI reference only. It uses React UMD, Babel JSX, mock data, and CSS, not production contracts.

## Existing Implementation State

- Phase 24 frontend foundation is present.
- Auth state is token-backed and calls `GET /api/auth/me`.
- Protected route guard redirects guests to login.
- Admin route guard rejects non-admin users.
- Navigation already exists but route labels differ slightly from prototype/docs and may need Phase 25 polish.
- Dashboard content is not implemented yet.
- Shared dashboard primitives exist only partly:
  - `Button`
  - `Input`
  - `Alert`
  - `SkeletonPage`
  - `RoutePlaceholder`
  - `Logo`
- No production dashboard API wrapper exists yet for jobs/models/admin stats.
- No production reusable status badge/metric card/table empty state exists yet beyond prototype-only code.

## Unknowns And Assumptions

Confirmed facts:

- Frontend must call only backend REST API.
- Visible UI text must be Ukrainian.
- Admin nav must be visible only for admins.
- Guests must not see authenticated navigation.
- Dashboard must show processed files, detections, average confidence, average FPS, active model, recent jobs, and quick upload action.
- Missing values must not render raw `null`.
- Prototype visual language should drive production frontend UI.

Assumptions:

- Phase 25 must not add backend endpoints. Dashboard should use existing backend APIs only.
- For regular users, exact aggregate dashboard stats are limited by available job-list data because no user aggregate endpoint exists. The implementation should derive best available user-scoped metrics from visible jobs and clearly render placeholders when data is incomplete.
- For admins, global count stats can use `GET /api/admin/stats`; recent global jobs can use `GET /api/admin/jobs`.
- Total processed files must mean completed jobs when the available data can identify that status; it must not use total media or total jobs as a substitute.
- Total detections may use admin stats for admins and completed-job summaries for regular users when available.
- Average confidence and average FPS must be derived only from available completed-job `summary_json` numeric values; otherwise render Ukrainian unavailable placeholders.
- Active model can use `GET /api/models?is_active=true&limit=1`.
- The implementation can add frontend-only types/components under existing `frontend/src` structure as needed, but must not add new product routes or backend behavior.
- Prototype mock-only data values must not be copied as product behavior.
- Prototype visual verification is required during implementation unless dev-server or browser tooling is genuinely unavailable; record the exact blocker if skipped.

## Files Likely Relevant For Implementation

Existing files likely to modify:

- `frontend/src/App.tsx`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/api/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/index.css`
- `frontend/src/test/auth-routes.test.tsx`

Existing files likely to read/reference:

- `frontend/src/auth/useAuth.ts`
- `frontend/src/auth/AuthProvider.tsx`
- `frontend/src/auth/ProtectedRoute.tsx`
- `frontend/src/auth/AdminRoute.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/Logo.tsx`
- `frontend/tailwind.config.ts`
- `frontend/package.json`
- `prototype/dashboard.jsx`
- `prototype/sidebar.jsx`
- `prototype/ui.jsx`
- `prototype/styles.css`

Potential new frontend-only files under existing `frontend/src`:

- dashboard page module
- dashboard API/query helper module
- reusable dashboard/status/empty/skeleton components
- dashboard-focused frontend tests

These are implementation decomposition candidates, not product-contract sources.
