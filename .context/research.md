# Phase 28 Research - Frontend Model Registry Page

## Current phase

- Phase: `Phase 28 - Frontend model registry page`
- Direction: Frontend
- Goal: Implement model list and admin model-management actions.
- Risk level: MEDIUM assumption. User prompt left risk placeholder unresolved; phase touches authenticated admin mutation UI and must preserve backend authority.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- Phase `Relevant docs:` only:
  - `docs/FRONTEND_UX.md`
  - `docs/API.md`
  - `docs/TRAINING_EXPERIMENTS.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/TESTING_QA.md`

## Repository files inspected

- `frontend/index.md`
- `prototype/index.md`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/api/types.ts`
- `frontend/src/api/upload.ts`
- `frontend/src/api/client.ts`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/index.css`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/test/jobs-page.test.tsx`
- `prototype/models.jsx`
- `backend/app/api/models.py`
- `backend/app/schemas/models.py`

## Confirmed repository facts

- Git worktree has existing modified files before this contract work:
  - `.context/design.md`
  - `.context/plan.md`
  - `.context/research.md`
  - `.context/review-code-openai.md`
  - `.context/review-code-resolution.md`
  - `.context/review-plan-claude.md`
  - `.context/review-plan-resolution.md`
  - `.context/status.md`
  - `docs/phase.md`
- Current `docs/phase.md` content exactly describes Phase 28.
- `frontend/package.json` confirms React, TypeScript, Vite, Tailwind CSS v3, shadcn-style components, React Router, TanStack Query, Recharts, and `@radix-ui/react-icons`.
- `frontend/package.json` does not include Framer Motion or Phosphor icons. Current icon dependency is `@radix-ui/react-icons`; use it for this phase.
- `frontend/src/App.tsx` routes `/models` to `ModelsPage` imported from `frontend/src/pages/placeholders.tsx`.
- `frontend/src/pages/placeholders.tsx` currently has a placeholder `ModelsPage`.
- `frontend/src/api/types.ts` already defines `ModelVersion` and `ModelListResponse`.
- `frontend/src/api/upload.ts` already calls `GET /models?limit=100` through `listModelsForUpload`.
- `frontend/src/api/dashboard.ts` already calls `GET /models?is_active=true&limit=1`.
- `backend/app/api/models.py` exposes:
  - `GET /api/models`
  - `GET /api/models/{model_id}`
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
- `backend/app/schemas/models.py` confirms model create fields:
  - `name`
  - `model_family`
  - `variant`
  - `weights_path`
  - `dataset_name`
  - `dataset_split_description`
  - `metrics_json`
  - `is_active`
- `prototype/models.jsx` contains the intended visual shape for the models page: page header, admin-only register action, admin registration form, active model indicator, model rows/cards, metrics bars, empty state, and activation button.
- `prototype/index.md` says prototype is UI reference only. Prototype mock data/actions are not product contracts.

## Existing implementation state

- Backend model registry API exists and already enforces authenticated view access plus admin-only register/activate behavior.
- Frontend already has authenticated shell, protected routing, admin guard, dashboard, upload, jobs history, and job details.
- `/models` exists as a protected route but still renders a placeholder.
- Existing frontend pages use TanStack Query, `apiRequest`, Tailwind utility classes, `av-card`, `av-input`, `av-label`, `av-skeleton`, shadcn button/input primitives, and Radix icons.
- Existing frontend tests mock `fetch`, set `tokenStorage`, render `<App initialEntries=[...]>`, and assert Ukrainian text plus absence of `null`, `undefined`, `frame_stride`, and unsafe storage paths.
- Current UI theme is dark dashboard style with compact cards, mono numeric/model text, emerald accent, and prototype-like sidebar layout.

## Unknowns and assumptions

- Assumption: Risk is MEDIUM because user left risk placeholder unresolved.
- Assumption: Phase 28 should add frontend API helpers for model registry rather than reuse upload-specific helper names.
- Assumption: Admin registration form should register existing relative model weights paths only; no `.pt` upload UI because API docs say large `.pt` upload through UI is optional and not required.
- Assumption: `metrics_json` values may use varied keys from training artifacts. UI should read documented/common keys without requiring new backend fields.
- Assumption: `model_size` may appear in `metrics_json` under keys such as `model_size_mb` or `size_mb`; no schema field exists for size.
- Assumption: Missing metrics render Ukrainian placeholders or empty states, not raw `null`.
- Assumption: Prototype visual layout should guide composition, spacing, active markers, metrics bars, and admin form. Prototype mock dataset names and fake values must not override docs.

## WARNING: CONFLICT

- `docs/index.md` current implementation state says the frontend contains the Phase 24 scaffold, while `frontend/index.md`, `docs/phase.md`, and actual `frontend/src/pages` files show implementation through Phase 27 with Phase 28 next.
- This is documentation-state drift, not a product behavior conflict. Use `docs/phase.md` as current phase source and actual files for implementation state.

## Files likely relevant for implementation

- `frontend/src/App.tsx`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/pages/ModelsPage.tsx`
- `frontend/src/pages/models/ModelPageParts.tsx`
- `frontend/src/api/models.ts`
- `frontend/src/api/types.ts`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/input.tsx`
- `frontend/src/index.css`
- `frontend/src/test/models-page.test.tsx`
- `frontend/src/test/auth-routes.test.tsx`
- `prototype/models.jsx`
- `prototype/styles.css`
- `backend/app/api/models.py`
- `backend/app/schemas/models.py`
