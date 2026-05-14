# Plan

1. `@role/developer-frontend` Add experiment TypeScript contracts.
   - Update `frontend/src/api/types.ts` with `ExperimentType`, `ExperimentMetric`, `ExperimentRun`, and `ExperimentListResponse`.
   - Verifiable: types match current backend schema and do not invent fields.

2. `@role/developer-frontend` Add experiment API client.
   - Create `frontend/src/api/experiments.ts` with list helper for `GET /experiments?limit=100`.
   - Verifiable: helper uses existing `apiRequest` and auth token flow.

3. `@role/developer-frontend` Add experiment data utilities.
   - Create helpers for safe text, percent/number/FPS/latency formatting, metric alias lookup, experiment grouping, and section-empty detection.
   - Verifiable: helpers return Ukrainian placeholder/empty state for `null`, missing, or unknown values.

4. `@role/developer-frontend` Build page parts from prototype visual structure.
   - Create reusable components for header, tabs, skeleton, error state, empty section, model comparison, threshold analysis, FPS/latency chart, tracker behavior comparison, false-positive summary, metric cards, and optional confusion matrix area.
   - Render confusion matrix image only from a documented safe API-served URL or safe metadata field; otherwise show exact experiment empty state.
   - Verifiable: visible text is Ukrainian except accepted technical labels; layout uses Tailwind/shadcn-style classes and Radix icons already installed.

5. `@role/developer-frontend` Implement `ExperimentsPage`.
   - Fetch experiments with TanStack Query.
   - Render loading, error, empty, and data states.
   - Render Recharts charts only when data exists.
   - Keep section empty states instead of blank charts, including FPS/latency and confusion matrix sections.
   - Verifiable: `/experiments` no longer renders placeholder.

6. `@role/developer-frontend` Wire route import.
   - Update `frontend/src/App.tsx` to import real `ExperimentsPage`.
   - Remove only the experiments placeholder usage; do not implement admin page.
   - Verifiable: `/experiments` route still stays inside `ProtectedRoute` and `AppShell`.

7. `@role/developer-frontend` Preserve documented tracker boundary.
   - Use behavior indicators from imported data such as FPS, unique track IDs, frames with detections, average confidence, fragmentation proxy, visual stability, and ID-switch examples when available.
   - Do not render MOTA, IDF1, HOTA, tracking accuracy, targeting, navigation, interception wording, or Ukrainian equivalents for targeting/navigation/interception if new copy is introduced.
   - Verifiable: tests and text search confirm forbidden terms are absent.

8. `@role/tester` Add focused frontend tests.
   - Create `frontend/src/test/experiments-page.test.tsx`.
   - Cover guest redirect, loading, API error, empty data, null metrics, all section rendering, FPS/latency chart rendering, confusion matrix empty state when no safe URL exists, role-safe data assumptions, no raw unsafe values, and exact required empty text from `docs/FRONTEND_UX.md`.
   - Assert no raw `artifacts_path`, storage-relative path, `/app/storage`, or `C:\` appears or is used as an image `src`.
   - Verifiable: Vitest assertions pass.

9. `@role/tester` Run relevant gates.
   - Run from `frontend/`:
     - `npm run lint`
     - `npm test`
     - `npm run build`
   - Verifiable: commands PASS or exact blocker captured.

10. `@role/code-reviewer` Review Phase 29 scope.
    - Check docs alignment, prototype conflict resolution, Ukrainian UI, Recharts use, FPS/latency chart presence, safe confusion matrix handling, no raw null/path display, no frontend auth overreach, no training launch, no forbidden tracker/targeting wording.
    - Run a focused visual comparison against `prototype/experiments.jsx` after build for tabs, comparison split, threshold chart/table, tracker table, false-positive section, and empty state; do not treat prototype mock metrics as contract.
    - Verifiable: review finds no blocking Phase 29 mismatch.
