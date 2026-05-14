# Design - Phase 30 Frontend admin page

## Phase goal

Implement the `/admin` frontend page only. Page must be admin-only, use existing backend REST admin endpoints, follow `@prototype` admin layout/style, show global stats, recent global jobs, model/experiment shortcuts, conservative storage cleanup UI, and basic users table.

## Intended behavior from docs

Confirmed:

- `/admin` is required route and admin-only page.
- Guests must be redirected by protected routing.
- Regular users must not see admin navigation and must not access `/admin`.
- Admin page content:
  - global processing statistics;
  - recent jobs from all users;
  - model management shortcuts;
  - storage cleanup action;
  - basic users table.
- Complex user management is out of scope.
- Backend remains authorization source of truth.
- Visible UI text must be Ukrainian.
- Empty, loading, error, forbidden, and success states must be clear.
- No raw `null`, `undefined`, unsafe absolute filesystem paths, secrets, or tokens should be shown.
- UI must stay inside CV-only boundary and must not imply targeting, navigation, interception, or hardware control.

Assumptions:

- Recent global jobs can use `GET /api/admin/jobs?limit=6` or similar small limit.
- Basic users table can use `GET /api/admin/users?limit=50`.
- Cleanup action uses existing `POST /api/admin/storage/cleanup` in an explicit two-step flow: preview sends `{ dry_run: true }`; confirmed cleanup sends `{ dry_run: false }`.
- Cleanup UI should present counts from backend response, not invent file lists.

## Architecture decisions

- Keep implementation in frontend only.
- Use TanStack Query for admin stats, jobs, and users, matching existing dashboard/jobs pages.
- Use existing `apiRequest` so JWT header and API base URL handling stay centralized.
- Add typed API wrappers for admin endpoints if needed, matching existing `frontend/src/api/*` pattern.
- Reuse existing UI patterns:
  - `av-card`, `av-label`, `av-skeleton`;
  - shadcn-style `Button`;
  - Radix icons from installed `@radix-ui/react-icons`;
  - job `StatusBadge`, `MediaIcon`, and formatters where practical.
- Base visual layout on `prototype/admin.jsx`:
  - compact metric row;
  - main grid with recent jobs and admin action rail;
  - cleanup confirmation block;
  - users table.
- Respect design skill constraints:
  - Tailwind v3 syntax only;
  - no new dependency imports unless already installed;
  - no emoji;
  - no Framer Motion unless installed and needed, which it is not;
  - avoid `h-screen`; existing shell uses `min-h-[100dvh]`;
  - no purple/blue glow aesthetic; keep existing dark neutral + green accent.

## Backend impact

- No backend source changes planned.
- Frontend consumes already implemented admin API routes only.

## Frontend impact

- Replace `/admin` placeholder with real admin page.
- Add admin API client functions and missing frontend response types if needed.
- Add admin page tests for data, empty/loading/error, cleanup interaction, and route visibility.
- Keep admin navigation/guard behavior already implemented.

## DB impact

- No DB changes.
- Cleanup semantics remain backend-owned.

## API impact

- No API contract changes.
- Consumed endpoints:
  - `GET /api/admin/stats`
  - `GET /api/admin/jobs`
  - `GET /api/admin/users`
  - `POST /api/admin/storage/cleanup`

## Security/privacy impact

- Admin page must rely on backend authorization and not treat hidden UI as security.
- Regular users must still be blocked by `AdminRoute`; backend still rejects direct API calls.
- Cleanup action wording must be conservative and not claim deletion beyond backend response.
- Cleanup UI must require preview before confirmed cleanup and must show only response counts/categories, not file names or storage paths.
- Do not display internal storage paths, passwords, tokens, password hashes, DB passwords, JWT secrets, or raw backend error details.
- Do not add user management controls.

## Test strategy

Frontend checks relevant to touched surface:

- Add focused admin page test(s):
  - admin route renders global stats/jobs/users from `/api/admin/*`;
  - regular user cannot access `/admin`;
  - empty admin jobs/users render Ukrainian empty states;
  - failed admin request shows safe Ukrainian error and retry;
  - cleanup preview posts `{ dry_run: true }`;
  - confirmed cleanup posts `{ dry_run: false }` only after explicit confirmation;
  - cleanup response counts and success/error states render without storage paths;
  - page does not render `null`, `undefined`, or absolute paths from mocked data.
- Run:
  - `npm run test -- admin-page`
  - `npm run lint`
  - `npm run build`
- Manual browser smoke when app/browser tooling is available:
  - admin can view `/admin`;
  - regular user is blocked;
  - responsive stats/table/action layout matches prototype structure;
  - loading, error, empty, cleanup preview, and cleanup success states remain Ukrainian and do not show raw `null` or absolute paths.
- If test name filtering is not supported by npm script, run targeted Vitest file directly or `npm run test`.
- Backend tests not required because backend is not modified.

## Ambiguities or conflicts

- No doc conflict found between `docs/phase.md`, `docs/ROADMAP.md`, `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/AUTH_SECURITY.md`, and `docs/TESTING_QA.md` for Phase 30.
- User prompt placeholders for phase title and risk are unresolved. Current phase is taken from `docs/phase.md`; risk treated as assumption.
- Prototype text appears mojibake through terminal, but production frontend files already use same encoded Ukrainian convention. Implementation should preserve app-visible Ukrainian behavior and avoid changing encoding policy during this phase.
