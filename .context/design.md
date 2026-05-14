# Design

## Phase Goal

Implement Phase 29 frontend contract for `/experiments`: protected Ukrainian experiments and metrics page that displays imported experiment results, uses Recharts, handles missing/null data with required empty states, and follows prototype visual direction without treating prototype mock data as API contract.

## Intended Behavior From Docs

- `/experiments` remains protected for authenticated users.
- Page displays:
  - model comparison table
  - confidence threshold analysis chart
  - tracker behavior comparison table
  - false-positive analysis summary
  - precision/recall/mAP cards
  - FPS/latency chart
  - confusion matrix image if available
- Charts use Recharts only.
- Matplotlib is not used in frontend UI.
- Missing section data shows exact text:

```text
Дані експерименту ще не завантажено
```

- Blank charts are not rendered.
- Raw `null`/`undefined` are not displayed.
- Regular users see published experiments only through backend API.
- Admins see all experiments where backend allows it.
- Tracker copy uses `tracker behavior comparison`, not absolute tracking accuracy.
- UI must not expose absolute filesystem paths or imply targeting/navigation/interception.

## Architecture Decisions

- Add frontend-only API helper for experiments using existing `apiRequest`.
- Add experiment response types to `frontend/src/api/types.ts` matching current backend schema.
- Replace placeholder `ExperimentsPage` with real page module and import it from `App.tsx`.
- Keep data fetching client-side with TanStack Query, consistent with existing frontend pages.
- Request `GET /api/experiments?limit=100`; do not create new endpoints.
- Group runs by documented `experiment_type`:
  - `model_comparison`
  - `threshold_analysis`
  - `tracker_comparison`
  - `false_positive_analysis`
- Build small local mapping helpers for metric aliases and safe display formatting.
- Use prototype as visual reference:
  - tabbed sections
  - dark dashboard cards
  - compact metric strips
  - model comparison chart/table split
  - threshold chart with adjacent values
  - FPS/latency chart with adjacent performance values
  - tracker behavior notice
  - false-positive summary blocks
- Override prototype conflicts:
  - use Recharts, not prototype SVG chart helpers
  - avoid MOTA/IDF1/HOTA/absolute tracking accuracy labels
  - avoid mock-only fake data unless tests inject it
- Use Radix icons already installed; do not add new icon package.
- Use Tailwind v3 syntax and existing `av-*` component classes.
- Keep motion minimal and CSS-only because no motion dependency is installed.

## Backend Impact

- No backend source change planned.
- Frontend consumes existing experiment list endpoint and current schema.

## Frontend Impact

- Add `frontend/src/api/experiments.ts`.
- Extend `frontend/src/api/types.ts`.
- Add `frontend/src/pages/ExperimentsPage.tsx`.
- Likely add `frontend/src/pages/experiments/experimentPageUtils.ts`.
- Likely add `frontend/src/pages/experiments/ExperimentPageParts.tsx`.
- Update `frontend/src/App.tsx` import to use real page instead of placeholder.
- Add `frontend/src/test/experiments-page.test.tsx`.

## DB Impact

- None.

## API Impact

- None. Use existing `/api/experiments`.

## Security/Privacy Impact

- Protected route remains behind `ProtectedRoute`.
- Frontend does not enforce experiment visibility beyond display; backend remains authority.
- Do not display `artifacts_path` raw.
- Do not display absolute host/container paths.
- Do not use `artifacts_path` or storage-relative paths as image `src`.
- Render confusion matrix image only from a documented safe API-served URL or safe metadata field. Until that exists, render the required empty state for the confusion matrix section.
- Do not surface raw backend errors directly; map to Ukrainian error message.
- Do not expose admin-only import UI in this phase.
- Do not add training launch controls.
- Do not display forbidden output fields or CV claims beyond documented metrics.

## Test Strategy

- Add frontend route/component tests for `/experiments`.
- Mock `GET /api/experiments` responses for:
  - loading skeleton
  - API error
  - empty list
  - published/user-visible data
  - null metric values
  - all four experiment types
  - FPS/latency chart renders when data exists
  - confusion matrix section uses empty state when no safe URL exists
  - tracker comparison without forbidden metric wording
- Assert:
  - route redirects guests through existing auth behavior
  - required empty-state text appears for missing sections
  - no raw `null`, `undefined`, `frame_stride`, `artifacts_path`, `/app/storage`, `storage/`, or `C:\` appears or is used as an image `src`
  - Recharts-backed chart content renders when data exists
  - regular UI text is Ukrainian except accepted technical labels
- Relevant quality gates:
  - `npm run lint`
  - `npm test -- experiments-page.test.tsx` if Vitest target filtering works; otherwise `npm test`
  - `npm run build`

## Ambiguities Or Conflicts

- WARNING: CONFLICT: prototype `prototype/experiments.jsx` shows MOTA/custom SVG chart patterns that conflict with `docs/TRAINING_EXPERIMENTS.md`, `docs/FRONTEND_UX.md`, and backend metric safety. Implementation must follow docs and use prototype only for visual composition.
- Confusion matrix display lacks documented safe frontend URL contract. Show it only from a documented safe API-served URL or safe metadata field; otherwise render required empty state.
- Exact experiment metric names are flexible/import-dependent. Use alias mapping and empty states instead of hard failures.
