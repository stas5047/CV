# Plan - Phase 30 Frontend admin page

1. `@role/developer-frontend` Add typed admin API helpers for existing endpoints.
   - Scope: frontend API layer only.
   - Use `apiRequest`.
   - Cover stats, admin jobs, users, and storage cleanup.
   - Verify by tests/mocks expecting exact `/api/admin/*` calls.

2. `@role/developer-frontend` Add missing frontend admin response types if needed.
   - Scope: `AdminUserListResponse`, `AdminJobListResponse`, `StorageCleanupRequest`, `StorageCleanupResponse`.
   - Keep shapes aligned with backend schemas already present.
   - Do not add fields absent from backend schema.

3. `@role/developer-frontend` Replace placeholder `/admin` page with real admin page.
   - Render global stats from `GET /admin/stats`.
   - Render recent global jobs from `GET /admin/jobs`.
   - Render basic users table from `GET /admin/users`.
   - Render model/experiment shortcut buttons linking to existing `/models` and `/experiments`.
   - Keep all visible text Ukrainian.
   - Do not add user-management mutation controls.

4. `@role/developer-frontend` Implement admin page states.
   - Loading: skeletons sized like stats/cards/tables.
   - Error: safe Ukrainian error message plus retry.
   - Empty: Ukrainian empty states for no jobs and no users.
   - Success: cleanup result summary after cleanup request.
   - Verify no raw `null` or `undefined` renders.

5. `@role/developer-frontend` Implement conservative cleanup UI.
   - Use required two-step flow: preview first, then confirmed cleanup.
   - Preview button sends `POST /api/admin/storage/cleanup` with `{ dry_run: true }`.
   - Confirmed cleanup is enabled only after preview and explicit confirmation, then sends `{ dry_run: false }`.
   - Show backend response counts only.
   - Do not display storage paths.
   - Do not claim active models/results are deleted.

6. `@role/developer-frontend` Match prototype-driven layout and existing design system.
   - Use dark dashboard card/table style from `prototype/admin.jsx` and current `index.css`.
   - Use installed Radix icons only.
   - Use Tailwind CSS v3-compatible classes.
   - Keep responsive grid collapse for laptop/narrow screens.

7. `@role/developer-frontend` Wire route import.
   - Point `frontend/src/App.tsx` at real admin page.
   - Remove only obsolete placeholder export if no longer used.
   - Preserve `AdminRoute` and `AppShell` behavior.

8. `@role/tester` Add focused frontend tests for Phase 30.
   - Admin sees page data from admin APIs.
   - Regular user is forbidden and admin nav stays hidden.
   - Empty jobs/users render empty states.
   - API failure shows safe Ukrainian error, not raw backend detail.
   - Cleanup preview posts `{ dry_run: true }` and shows response summary.
   - Confirmed cleanup posts `{ dry_run: false }` only after explicit confirmation and shows response summary.
   - Cleanup API failure shows safe Ukrainian error.
   - Container does not contain `null`, `undefined`, `C:\`, `/app/`, `/storage/`, or raw token-like values from mocks.

9. `@role/tester` Run relevant quality gates.
   - `npm run test -- admin-page` or equivalent targeted Vitest command: expected PASS.
   - `npm run lint`: expected PASS.
   - `npm run build`: expected PASS.
   - Manual browser smoke for `/admin` when app/browser tooling is available: expected PASS.
   - If a command/tool is unavailable, report `not available yet` with reason.
   - Backend tests: not run / not required unless frontend implementation reveals API mismatch.

10. `@role/code-reviewer` Review changed frontend files against docs.
   - Check admin-only visibility, Ukrainian text, empty/loading/error states, no absolute paths, no raw nulls, no scope creep, no invented backend behavior, no out-of-scope CV wording.
   - Verify design follows prototype and existing dashboard system.
   - Compare `/admin` layout structure against `prototype/admin.jsx` and current `index.css` visual system without adding new dependencies.

11. `@role/docs-maintainer` Skip product doc updates.
   - No commands, env vars, routes, product docs, or source-of-truth docs should change in this phase.
   - If implementation creates `frontend/src/pages/AdminPage.tsx`, `frontend/src/api/admin.ts`, or otherwise changes frontend folder contents tracked by `frontend/index.md`, update `frontend/index.md`; otherwise record index update skipped.
