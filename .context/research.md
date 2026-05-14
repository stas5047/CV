# Research - Phase 30 Frontend admin page

## Current phase

- Confirmed current phase from `docs/phase.md`: Phase 30 - Frontend admin page.
- Direction: Frontend / Admin.
- Goal: implement admin-only UI for global stats, global jobs, users, shortcuts, and cleanup.
- User-supplied phase/risk placeholders were not filled in prompt.
- Assumption: risk is MEDIUM because phase exposes admin-only UI and cleanup trigger, but backend authorization remains source of truth.

## Docs consulted

Initial required docs:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Phase-relevant docs from `docs/phase.md`:

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

Design reference requested by user:

- `prototype/admin.jsx`
- `prototype/styles.css`

## Confirmed repository facts

- Git checkout exists.
- `git status --short` shows existing modified files before this planning pass:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- User explicitly requested writing only `.context/research.md`, `.context/design.md`, `.context/plan.md`.
- Frontend stack in `frontend/package.json`: React 19, Vite 6, TypeScript, Tailwind CSS 3.4, React Router 7, TanStack Query 5, Recharts, shadcn-style local components, `@radix-ui/react-icons`.
- Frontend scripts in `frontend/package.json`:
  - `npm run lint`
  - `npm run build` (`tsc -b && vite build`)
  - `npm run test`
- `@phosphor-icons/react` and Framer Motion are not installed.
- Per `design-taste-frontend`, use installed `@radix-ui/react-icons` if icons needed; do not assume missing dependencies.
- `prototype/` contains static UI reference. `prototype/admin.jsx` has admin stats cards, global jobs table, system shortcuts, cleanup confirmation, and users table matching Phase 30 scope.
- `frontend/src/index.css` already mirrors prototype visual direction: dark dashboard, Space Grotesk/DM Sans/JetBrains Mono, green accent, compact cards/tables, skeleton styles.

## Existing implementation state

- `frontend/src/App.tsx` already registers `/admin` route inside protected shell and wraps it in `AdminRoute`.
- `/admin` currently imports `AdminPage` from `frontend/src/pages/placeholders.tsx`.
- `frontend/src/pages/placeholders.tsx` currently defines `AdminPage` as a placeholder only.
- `frontend/src/auth/AdminRoute.tsx` rejects non-admin users with `ForbiddenPage`.
- `frontend/src/layout/AppShell.tsx` hides admin nav from regular users and shows it only for `user.role === "admin"`.
- `frontend/src/api/types.ts` already defines `AdminStatsResponse`.
- `frontend/src/api/dashboard.ts` already calls:
  - `GET /admin/stats`
  - `GET /admin/jobs?limit=5`
- Backend admin API already exists in `backend/app/api/admin.py`:
  - `GET /api/admin/stats`
  - `GET /api/admin/jobs`
  - `GET /api/admin/users`
  - `POST /api/admin/storage/cleanup`
- Backend schemas in `backend/app/schemas/admin.py` define admin stats, admin users/jobs list responses, cleanup request/response.
- Backend cleanup service only deletes unreferenced `temp` files; other unprotected files are reported, not deleted.
- Existing frontend tests cover auth route guard and admin dashboard data, but not a real `/admin` page.

## Unknowns and assumptions

- Unknown: exact final visual copy from prototype is mojibake in terminal output. Assumption: implementation should preserve existing frontend encoding/style and use Ukrainian visible text consistent with current frontend files.
- Resolved for implementation contract: cleanup UI must use a two-step flow. First request sends `{ dry_run: true }` for preview. Confirmed cleanup sends `{ dry_run: false }`. UI must render backend counts only and not display storage paths.
- Unknown: whether global jobs table needs pagination/filtering in Phase 30. Docs require recent jobs from all users, not full global job management. Assumption: show recent limited list only.
- Unknown: whether admin users table needs status controls. Docs explicitly forbid complex user management unless approved. Assumption: read-only basic users table only.
- Unknown: whether admin page should link to model import forms or only shortcut navigation. Docs require model management shortcuts. Assumption: use links/buttons to existing `/models` and `/experiments`.

## Files likely relevant for implementation

- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/pages/AdminPage.tsx` if new page file follows existing page pattern
- `frontend/src/api/types.ts`
- `frontend/src/api/admin.ts` if new API wrapper follows existing API-module pattern
- `frontend/src/pages/jobs/jobFormatters.ts`
- `frontend/src/pages/jobs/JobPageParts.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/input.tsx`
- `frontend/src/lib/utils.ts`
- `frontend/src/test/admin-page.test.tsx` if new focused test follows existing test pattern
- `frontend/src/test/auth-routes.test.tsx`
- `frontend/src/index.css`
- `prototype/admin.jsx`
- `prototype/styles.css`
