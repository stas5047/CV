# Phase 31 Design

## Phase Goal

Make the production frontend coherent, Ukrainian, polished, responsive, based on the `prototype/` visual reference, and within the documented CV-only scope.

## Intended Behavior From Docs

Confirmed:

- All visible frontend UI text must be Ukrainian.
- Accepted technical labels such as `FPS`, `mAP`, `YOLO`, `CSV`, and `JSON` remain readable.
- Required frontend routes remain `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`.
- Protected routes redirect guests to login.
- Admin route and admin navigation/actions are visible only to admins.
- UI must use polished dashboard components, not raw debug panels.
- UI must use Tailwind CSS and shadcn/ui components.
- UI must use Recharts for frontend charts.
- UI must include loading, error, empty, forbidden, and no-detection states.
- UI must not display raw `null` values.
- UI must not display unsafe absolute filesystem paths.
- UI must not expose `frame_stride` in the standard UI.
- UI must not present CV outputs as targeting, navigation, interception, hardware-control, or engagement instructions.
- Completed no-detection jobs are successful results, with Ukrainian empty state.
- Experiment sections without data must show the exact documented Ukrainian empty-state text from `docs/FRONTEND_UX.md`.

Assumptions:

- Prototype visual styling is authoritative for look and feel only: dark compact dashboard shell, narrow sidebar, dense data tables, restrained green accent, compact cards, clear skeletons, badges, toasts, forms, progress bars, and responsive mobile drawer.
- Existing production API client calls and route flows remain unchanged.
- Phase 31 should prefer consolidating existing presentation/formatting patterns over adding new product features.

## Architecture Decisions

- Keep production stack as React + TypeScript + Vite + Tailwind CSS v3 + shadcn/ui + React Router + TanStack Query + Recharts.
- Use `@radix-ui/react-icons`, because it is already installed. Do not add `@phosphor-icons/react`.
- Do not add Framer Motion, GSAP, Three.js, or other motion libraries in this phase. Existing CSS transitions, `animate-pulse`, and skeleton shimmer are sufficient and align with current dependency set.
- Use prototype tokens as the visual baseline, but implement them through `frontend/src/index.css`, Tailwind utilities, and existing shadcn-style primitives.
- Keep browser-visible product behavior driven by docs and backend API contracts, not prototype mock data.
- Keep `frontend/src/App.tsx` route structure unchanged unless review finds an existing route guard bug.
- Prefer existing files and existing test files. Do not create new routes or product surfaces.
- Deduplicate shared UX primitives only when it reduces inconsistent badges, cards, skeletons, or empty states without changing API behavior.
- Keep high-density dashboard design compact and scan-friendly. Avoid marketing hero layouts.
- Keep mobile layouts single-column or horizontally scrollable for data tables; avoid layout shifts and viewport `h-screen`.

## Backend Impact

- None planned.
- Backend remains authorization authority.
- No backend routes, response schemas, auth behavior, upload rules, or download behavior should change in this phase.

## Frontend Impact

- Touched surface is frontend route/page/control polish, tests, and possibly shared styling.
- Audit all pages for Ukrainian text, safe placeholders, hidden admin controls, safe errors, no raw paths, no `frame_stride`, and no out-of-scope CV wording.
- Standardize page-level components:
  - status badges;
  - buttons;
  - forms;
  - tables;
  - cards;
  - charts;
  - skeletons;
  - toast notifications or equivalent documented success/error feedback for implemented user actions;
  - empty/error states.
- Standardize data formatting:
  - date;
  - duration;
  - confidence;
  - percentage;
  - bounding box;
  - missing data placeholder.
- Align production styles with prototype:
  - dark off-black background;
  - compact sidebar;
  - green accent;
  - restrained borders;
  - small-radius cards;
  - mono numeric data;
  - compact table rows;
  - clear mobile drawer and table scrolling.

## Database Impact

- None planned.
- No schema, migration, seed, or database helper changes.

## API Impact

- None planned.
- No endpoint additions or payload changes.
- Existing frontend API calls may be reused only as already implemented.

## Security And Privacy Impact

- Touched through frontend display and visibility only.
- Frontend must not reveal unsafe absolute paths, raw stack traces, tokens, secrets, database passwords, or backend storage internals.
- Frontend must hide admin navigation and admin mutation actions from regular users.
- Frontend route guard must still reject non-admin users from `/admin`, while backend remains source of truth.
- Error messages shown to users must be safe Ukrainian summaries.
- UI must not show text that implies targeting, navigation, interception, payload, geolocation, or hardware-control behavior.

## Test Strategy

Relevant automated checks:

- `cd frontend; npm run lint`
- `cd frontend; npm test`
- `cd frontend; npm run build`

Relevant focused test additions or updates:

- Ukrainian visible text audit assertions for pages where English labels are not documented technical terms.
- Raw `null`, `undefined`, `frame_stride`, `C:\`, `/app/storage`, and `/storage/` non-display assertions for pages touched by polish.
- Admin visibility assertions for shell navigation and admin actions.
- Empty/loading/error/no-detection state assertions where components change.
- Responsive behavior is primarily manual/browser verification unless an existing test can assert structure without brittle layout checks.

Manual/browser checks:

- Login route.
- Registration route, including disabled-registration state where practical.
- Dashboard route for user and admin data shapes.
- Upload route, including invalid file and processing status states.
- Jobs route with empty and filtered states.
- Job details route with completed, processing, failed, video-preview-unavailable, and no-detection states.
- Models route for regular user and admin.
- Experiments route with missing metrics and charts.
- Admin route for admin only.
- Narrow viewport smoke for shell, tables, forms, and cards.
- Manual smoke notes must record data source: live backend data, seeded/mock test data, or route-level test harness data.

Baseline results from research:

- `npm run lint` PASS.
- `npm test` PASS, 8 files and 50 tests.
- `npm run build` PASS, with Vite chunk-size warning.

## Ambiguities Or Conflicts

- No docs conflict found between `docs/phase.md` and `docs/ROADMAP.md` for Phase 31.
- Ambiguity: user risk level was placeholder only. Assumed `MEDIUM`.
- Ambiguity: whether `CV subsystem`, `Precision`, `Recall`, `Bounding box`, and `Track ID` count as accepted technical labels. Resolve during Phase 31 audit by preferring Ukrainian labels unless docs require exact English wording.
- Ambiguity: exact prototype fidelity target. Use prototype for layout, density, color, and component behavior, but do not copy mock-only behavior or treat prototype data/actions as product contract.
