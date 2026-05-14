# Phase 31 Research

## Current Phase

- Phase: `Phase 31 - Frontend Ukrainian UX, responsive polish, and scope audit`
- Direction: Frontend / QA
- Phase source: `docs/phase.md`
- ROADMAP match: `docs/ROADMAP.md` contains same Phase 31 title, goal, scope, relevant docs, validation, and commit message.
- Risk level: user input contained placeholder only. Assumption: `MEDIUM`, because phase touches all frontend routes, UX consistency, responsive behavior, role visibility, and scope/security boundary display rules.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `frontend/index.md`
- `prototype/index.md`

## Confirmed Repository Facts

- `git status --short` before writing context files showed modified `.context/*` files and modified `docs/phase.md`.
- `docs/phase.md` working-tree diff advances current phase from Phase 30 to Phase 31.
- Existing `.context/research.md`, `.context/design.md`, and `.context/plan.md` were empty before this write.
- `frontend/package.json` contains React, TypeScript, Vite, Tailwind CSS v3, React Router, TanStack Query, Recharts, `@radix-ui/react-icons`, and shadcn-related primitives.
- `frontend/package.json` does not contain Framer Motion, GSAP, Three.js, or `@phosphor-icons/react`.
- Tailwind config is v3 style in `frontend/tailwind.config.ts`.
- Production frontend routes in `frontend/src/App.tsx` include `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`.
- `/admin` is wrapped by `AdminRoute`.
- Authenticated shell navigation is in `frontend/src/layout/AppShell.tsx`; admin navigation item is appended only when `user?.role === "admin"`.
- Shared styling tokens and core component classes are in `frontend/src/index.css`.
- `prototype/` contains static UI reference files for auth, shell, dashboard, upload, jobs, job detail, models, experiments, and admin.
- `prototype/index.md` says prototype is UI reference only, with mock data/actions not product contracts.
- `frontend/index.md` says frontend currently implements through Phase 30.
- Static scan found `frame_stride` only in tests and API type/test data, not visible route labels.
- Existing frontend tests include guards against visible `frame_stride`, raw `null`, `undefined`, `C:\`, `/app/storage`, and unsafe storage strings on key pages.
- Baseline command `npm run lint` in `frontend/` passed.
- Baseline command `npm test` in `frontend/` passed: 8 test files, 50 tests.
- Baseline command `npm run build` in `frontend/` passed, with Vite chunk-size warning for one generated JS chunk over 500 kB.

## Existing Implementation State

- Frontend scaffold is complete and route set exists.
- Pages implemented:
  - `LoginPage`
  - `RegisterPage`
  - `DashboardPage`
  - `UploadPage`
  - `JobsPage`
  - `JobDetailsPage`
  - `ModelsPage`
  - `ExperimentsPage`
  - `AdminPage`
  - `ForbiddenPage`
  - `NotFoundPage`
- Shared page parts exist for upload, jobs, models, experiments, and admin.
- Existing styling already resembles prototype in broad tokens: dark surface palette, green accent, compact sidebar, metric cards, tables, badges, skeletons, and dashboard spacing.
- Some shared UI behavior is duplicated across page-local components, especially status badges, empty states, skeletons, metric cards, and formatting helpers.
- Existing visible UI text appears mostly Ukrainian from `rg` output, with accepted technical labels present (`FPS`, `mAP`, `YOLO`, `CSV`, `JSON`).
- Potential audit targets found:
  - `frontend/src/components/Logo.tsx` displays `CV subsystem`, which may violate Ukrainian visible-text rule unless treated as brand/technical subtitle.
  - `frontend/src/pages/ExperimentsPage.tsx` displays `tracker behavior comparison`, which is explicitly required by roadmap/docs wording for tracker comparison.
  - `frontend/src/pages/DashboardPage.tsx` displays `Precision` and `Recall`; docs name those metric concepts but Phase 31 should decide whether to keep as accepted metric labels or localize labels while preserving technical clarity.
  - `frontend/src/pages/JobDetailsPage.tsx` displays `Bounding box` and `Track ID`; docs require those data fields, but Phase 31 should check consistency with Ukrainian table heading expectations.
  - `frontend/src/pages/placeholders.tsx` remains present but appears unused by `frontend/src/App.tsx`; verify before ignoring or deleting.
- No backend, database, API, worker, training, or Docker source changes are required by Phase 31 docs.

## Unknowns And Assumptions

- Unknown: exact user-supplied risk level. Assumption: `MEDIUM`.
- Unknown: whether manual browser smoke must use live backend data or test/mocked state for all routes. Assumption: use available local frontend test harness first, then browser smoke with current frontend when a backend is available or mocked routes are practical.
- Unknown: whether `CV subsystem`, `Precision`, `Recall`, `Bounding box`, and `Track ID` are acceptable technical labels. Assumption: audit them against `docs/FRONTEND_UX.md`; keep only labels that are documented technical terms or necessary field names.
- Unknown: exact visual deltas between production frontend and prototype until browser screenshots are reviewed side by side.
- Assumption: prototype visual language is the design source for production frontend styling, but prototype mock-only behavior, data, actions, and CDN/runtime approach are not implementation contracts.
- Assumption: no new routes, API calls, database fields, or product flows should be added in Phase 31.

## Files Likely Relevant For Implementation

- `frontend/src/App.tsx`
- `frontend/src/index.css`
- `frontend/tailwind.config.ts`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/components/Logo.tsx`
- `frontend/src/components/Alert.tsx`
- `frontend/src/components/SkeletonPage.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/input.tsx`
- `frontend/src/pages/AuthLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/UploadPage.tsx`
- `frontend/src/pages/upload/UploadPageParts.tsx`
- `frontend/src/pages/upload/uploadUtils.ts`
- `frontend/src/pages/JobsPage.tsx`
- `frontend/src/pages/JobDetailsPage.tsx`
- `frontend/src/pages/jobs/JobPageParts.tsx`
- `frontend/src/pages/jobs/jobFormatters.ts`
- `frontend/src/pages/ModelsPage.tsx`
- `frontend/src/pages/models/ModelPageParts.tsx`
- `frontend/src/pages/models/modelPageUtils.ts`
- `frontend/src/pages/ExperimentsPage.tsx`
- `frontend/src/pages/experiments/ExperimentPageParts.tsx`
- `frontend/src/pages/experiments/experimentPageUtils.ts`
- `frontend/src/pages/AdminPage.tsx`
- `frontend/src/pages/admin/AdminPageParts.tsx`
- `frontend/src/pages/ForbiddenPage.tsx`
- `frontend/src/pages/NotFoundPage.tsx`
- `frontend/src/test/auth-routes.test.tsx`
- `frontend/src/test/dashboard.test.tsx`
- `frontend/src/test/upload-page.test.tsx`
- `frontend/src/test/jobs-page.test.tsx`
- `frontend/src/test/job-details-page.test.tsx`
- `frontend/src/test/models-page.test.tsx`
- `frontend/src/test/experiments-page.test.tsx`
- `frontend/src/test/admin-page.test.tsx`
- `prototype/AeroVision.html`
- `prototype/styles.css`
- `prototype/ui.jsx`
- `prototype/sidebar.jsx`
- `prototype/auth.jsx`
- `prototype/dashboard.jsx`
- `prototype/upload.jsx`
- `prototype/jobs.jsx`
- `prototype/job-detail.jsx`
- `prototype/models.jsx`
- `prototype/experiments.jsx`
- `prototype/admin.jsx`
