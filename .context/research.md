# Research

## Current Phase

- Phase 29 - Frontend experiments and metrics page.
- Direction: Frontend.
- Risk level assumption: MEDIUM, because phase renders role-filtered experiment data from protected API and must avoid forbidden tracking/targeting wording.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`

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
- `docs/phase.md` names Phase 29 and lists relevant docs matching `docs/ROADMAP.md`.
- `frontend/package.json` has required Phase 29 dependencies:
  - React 19
  - React Router 7
  - TanStack Query 5
  - Recharts 2
  - Tailwind CSS 3
  - `@radix-ui/react-icons`
- `@phosphor-icons/react` is not installed. Use existing `@radix-ui/react-icons`.
- `framer-motion` is not installed. No new motion dependency is needed for this phase.
- `frontend/tailwind.config.ts` uses Tailwind v3 and existing dashboard palette/fonts.
- `prototype/index.md` says prototype is UI reference only, with docs remaining authoritative.
- `prototype/experiments.jsx` provides visual reference for tabs, model comparison, threshold chart, tracker behavior table, false-positive section, and required empty state.

## Existing Implementation State

- `/experiments` route exists in `frontend/src/App.tsx`, protected by `ProtectedRoute` and rendered inside `AppShell`.
- Current `ExperimentsPage` is a placeholder from `frontend/src/pages/placeholders.tsx`.
- No frontend experiments API helper exists yet.
- `frontend/src/api/types.ts` has no experiment response types yet.
- Backend already exposes:
  - `GET /api/experiments`
  - `GET /api/experiments/{experiment_id}`
  - `POST /api/experiments/import`
- Backend schemas expose experiment runs with:
  - `id`
  - `name`
  - `experiment_type`
  - `description`
  - `model_version_id`
  - `dataset_name`
  - `config_json`
  - `artifacts_path`
  - `is_published`
  - `created_by_user_id`
  - `created_at`
  - `metrics`
- Regular users see published experiments only through backend service behavior; admins may see all.
- Backend rejects forbidden tracker metric terms: `tracking_accuracy`, `mota`, `idf1`, `hota`.
- Existing frontend pages use:
  - `useQuery` from TanStack Query
  - `apiRequest`
  - Radix icons
  - `av-card`, `av-label`, `av-skeleton`, Tailwind utilities
  - Ukrainian visible UI text
  - tests under `frontend/src/test`

## Unknowns And Assumptions

- Risk level placeholder was not filled by user. Assumption: MEDIUM.
- Exact imported metric names are not fully fixed by docs or API. Implementation should map known aliases defensively and render empty states for missing/null values.
- API has list endpoint only for experiment runs; frontend should derive all Phase 29 sections from `GET /api/experiments?limit=100` without inventing new endpoints.
- Confusion matrix image display is optional when available. API exposes `artifacts_path`, but frontend must not expose raw paths and has no documented file download endpoint for experiment artifacts. Assumption: show artifact availability/empty state only unless existing API already supplies safe image URL in metadata.
- Prototype data is mock data, not contract. Use prototype visual structure, spacing, and page composition, but docs/API decide behavior and field mapping.

## WARNING: CONFLICT

- `prototype/experiments.jsx` includes mock tracker metrics such as `MOTA`, `ID Switches`, and `Track Recall`, while `docs/TRAINING_EXPERIMENTS.md` says tracker comparison is not absolute tracking accuracy and must not require MOTA/IDF1/HOTA. `backend/app/services/experiments.py` also rejects `mota`, `idf1`, and `hota`.
- `prototype/experiments.jsx` includes custom SVG chart helpers despite the phase docs requiring Recharts for frontend charts.
- Resolution for implementation: use prototype layout and visual rhythm only; use Recharts and documented behavior metrics.

## Files Likely Relevant For Implementation

- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/pages/ModelsPage.tsx`
- `frontend/src/pages/models/ModelPageParts.tsx`
- `frontend/src/pages/models/modelPageUtils.ts`
- `frontend/src/index.css`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/test/models-page.test.tsx`
- `prototype/experiments.jsx`
- `prototype/styles.css`
- `backend/app/api/experiments.py`
- `backend/app/schemas/experiments.py`
- `backend/app/services/experiments.py`
