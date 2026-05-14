# Phase 25 Plan

## Scope

Phase 25 only: frontend dashboard and authenticated shell. No backend, database, CV worker, training, product-doc, Docker, or route-contract changes.

## Ordered Atomic Steps

1. `@role/developer-frontend` Re-read `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/AUTH_SECURITY.md`, `docs/TESTING_QA.md`, and prototype dashboard/shell files before source edits.
   - Verify: notes in implementation status reference only Phase 25 docs and prototype files.

2. `@role/developer-frontend` Inspect current frontend route/auth structure.
   - Files: `frontend/src/App.tsx`, `frontend/src/layout/AppShell.tsx`, `frontend/src/pages/placeholders.tsx`, `frontend/src/auth/*`.
   - Verify: `/dashboard` remains protected and admin guard remains only on `/admin`.

3. `@role/developer-frontend` Add frontend API types for dashboard-consumed existing backend responses.
   - Surface: `frontend/src/api/types.ts` or adjacent frontend API module.
   - Include only fields returned by existing schemas and needed by dashboard.
   - Verify: types match backend schemas for jobs, models, and admin stats; no new endpoint or field names.

4. `@role/developer-frontend` Add dashboard API/query helpers using existing routes only.
   - Regular user calls:
     - `GET /api/jobs?limit=100`
     - `GET /api/models?is_active=true&limit=1`
   - Admin calls:
     - `GET /api/admin/stats`
     - `GET /api/admin/jobs?limit=5`
     - `GET /api/models?is_active=true&limit=1`
   - Verify: helpers use `apiRequest`, send JWT through existing client behavior, do not call nonexistent routes, and regular-user fetch logic never calls `/api/admin/*`.

5. `@role/developer-frontend` Add dashboard formatting helpers.
   - Format dates with `uk-UA`.
   - Format duration, confidence percent, FPS, counts, media type, and status text.
   - Map missing values to Ukrainian placeholders.
   - Derive `total processed files` from completed jobs only; do not substitute total media or total jobs.
   - Derive total detections from admin stats for admins or completed-job summaries for regular users when numeric data exists.
   - Derive average confidence and average FPS only from available completed-job `summary_json` numeric values.
   - Show Ukrainian unavailable placeholders when a metric cannot be derived; do not calculate global averages from only `GET /api/admin/jobs?limit=5`.
   - Verify: helper tests or component tests prove raw `null` is not rendered.

6. `@role/developer-frontend` Add reusable UI primitives needed by dashboard.
   - Needed primitives: status badge, metric card, empty state, dashboard skeleton, section header, mini progress/metric bar.
   - Match prototype visual language with Tailwind v3 and existing CSS tokens.
   - Use `@radix-ui/react-icons` only.
   - Verify: no new third-party dependency, no emoji, no pure black, no purple/blue glow, no `h-screen`.

7. `@role/developer-frontend` Polish authenticated shell to match prototype within existing behavior.
   - Keep compact desktop sidebar.
   - Keep mobile top bar/drawer.
   - Add/keep active styling for `/jobs/:jobId`.
   - Keep admin item hidden unless `user.role === "admin"`.
   - Keep logout behavior.
   - Verify: route tests still prove admin nav hidden for regular users and visible for admins.

8. `@role/developer-frontend` Implement `/dashboard` page.
   - Replace only dashboard placeholder, leaving later phase routes as placeholders.
   - Add page header, quick upload action to `/upload`, four metric cards, active model panel, activity/summary panel, recent jobs table.
   - Use user-scoped data for regular users and global admin data only where existing admin endpoints support it.
   - Do not display `weights_path` or any storage-like path from model API responses.
   - Verify: dashboard renders required docs content and no later-phase upload/jobs/model mutation behavior.

9. `@role/developer-frontend` Implement dashboard loading, error, and empty states.
   - Loading: skeletons shaped like metric cards/table.
   - Error: safe Ukrainian message and retry affordance.
   - Empty: Ukrainian state for no jobs and missing active model.
   - Verify: no blank table/chart, no raw API error dump, no raw `null`.

10. `@role/developer-frontend` Add or update frontend tests for Phase 25.
    - Cover regular dashboard render with mocked jobs/model data.
    - Cover admin dashboard render with mocked admin stats/jobs/model data.
    - Cover empty dashboard state.
    - Cover failed dashboard request.
    - Cover admin nav role visibility remains correct.
    - Verify: tests assert Ukrainian visible text where practical, no raw `null`, active model UI does not show `weights_path`, and regular-user dashboard mocks fail if `/api/admin/*` is called.

11. `@role/tester` Run frontend lint.
    - Command: `cd frontend; npm run lint`
    - Expected: PASS.

12. `@role/tester` Run frontend tests.
    - Command: `cd frontend; npm test`
    - Expected: PASS.

13. `@role/tester` Run frontend production build.
    - Command: `cd frontend; npm run build`
    - Expected: PASS.

14. `@role/tester` Manual browser check, required unless dev-server or browser tooling is genuinely unavailable during implementation.
    - Command: `cd frontend; npm run dev -- --port 5173`
    - Check `/dashboard` as regular user and admin with mocked or local backend data.
    - Check desktop and narrow viewport.
    - Verify: layout resembles `prototype/AeroVision.html` dashboard/shell and no admin controls leak to regular user.
    - If skipped: record exact unavailable tool, startup failure, or environment blocker.

15. `@role/code-reviewer` Review changed frontend files against Phase 25 docs and prototype.
    - Check: Ukrainian UI, protected route, admin nav visibility, no raw `null`, no absolute paths, no nonexistent API calls, no source-scope creep into later phases.
    - Verify: findings resolved or documented before completion.

16. `@role/docs-maintainer` Decide docs/index updates.
    - Expected: no product docs update for Phase 25 unless implementation changes frontend commands or index-worthy file inventory.
    - Verify: if no command/structure changes requiring docs, report docs update skipped.

## Phase 25 Quality Gates

- `cd frontend; npm run lint`
- `cd frontend; npm test`
- `cd frontend; npm run build`
- Manual browser smoke for `/dashboard` compared against prototype, required unless exact tooling/startup blocker is recorded.

## Out Of Scope

- `/upload` implementation.
- `/jobs` implementation beyond recent-job links.
- `/jobs/:jobId` implementation.
- `/models` admin forms or activation UI.
- `/experiments` charts.
- `/admin` page implementation.
- Backend dashboard aggregate endpoint.
- Database schema changes.
- Worker changes.
- Docker runtime changes.
- Product docs changes unless command/index facts change during implementation.
