# Phase 25 Status

## Implementation

- Implemented `/dashboard` as protected frontend page using existing backend REST routes only.
- Added dashboard API helpers for:
  - `GET /api/jobs?limit=100`
  - `GET /api/admin/stats`
  - `GET /api/admin/jobs?limit=5`
  - `GET /api/models?is_active=true&limit=1`
- Added typed frontend models for jobs, active model data, and admin stats.
- Polished authenticated shell active states and kept admin navigation role-gated.
- Added Ukrainian dashboard loading, error, empty, metric, active-model, activity, and recent-jobs states.
- Updated frontend tests for dashboard data, empty/error states, admin visibility, no raw `null`, no `weights_path` display, and regular-user no-admin-fetch behavior.
- Updated `frontend/index.md` for current Phase 25 frontend state.
- `frontend/src/pages/DashboardPage.tsx` is 490 LOC. Kept as one cohesive page module for Phase 25 because helper/view-model logic, dashboard-only primitives, and page composition are tightly coupled; split can happen when later dashboard widgets become shared.
- Final fix changed admin average confidence/FPS to unavailable placeholders because current backend admin stats do not provide global aggregate values.

## Quality Gates

- `cd frontend; npm test`: PASS.
- `cd frontend; npm run lint`: PASS.
- `cd frontend; npm run build`: PASS.
- `git diff --check`: PASS, line-ending warnings only.
- Browser plugin path: BLOCKED because the Node REPL JavaScript tool required by the Browser plugin is not exposed in this session.
- `cd frontend; npx playwright --version`: PASS, version 1.60.0.
- `cd frontend; npx playwright screenshot` with mock API, token storage state, `1440x900` dashboard: PASS, screenshot written to temp.
- `cd frontend; npx playwright screenshot` with mock API, token storage state, `390x844` dashboard: PASS, screenshot written to temp.

## Security / Privacy

- Regular dashboard uses only user-visible `/api/jobs`; it does not call `/api/admin/*`.
- Admin dashboard uses admin endpoints only after authenticated role is `admin`.
- Dashboard does not display `weights_path`, raw storage paths, tokens, secrets, `null`, or `undefined`.
- Admin dashboard no longer presents recent-job confidence/FPS as global average metrics.
- Frontend remains display-only for Phase 25; no backend authorization assumptions were changed.

## Deviations

- No backend aggregate endpoint was added; metric derivation follows approved plan and renders Ukrainian placeholders when values are not available.
- Browser plugin could not be used because its required Node REPL JavaScript tool is unavailable; Playwright CLI fallback verified rendered dashboard desktop and mobile states with mocked API.

## Remaining Risks

- Regular-user dashboard aggregates are based on visible job-list data because no user dashboard stats endpoint exists.
- Admin average confidence/FPS remain unavailable until a backend global aggregate source exists.
