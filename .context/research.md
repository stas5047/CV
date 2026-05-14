# Research - Phase 24 Frontend scaffold, API client, auth, and protected routing

## Current phase

- Confirmed current phase: `Phase 24 - Frontend scaffold, API client, auth, and protected routing`.
- Source: `docs/phase.md`.
- Direction: Frontend.
- Goal from phase doc: create the React frontend foundation after backend contracts are stable.
- Risk level: not provided in user prompt. Assumption for this contract: `MEDIUM`, because this phase introduces frontend auth state, token handling, protected routing, and admin route guarding, but does not change backend authorization.

## Docs consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

## Confirmed repository facts

- Git checkout is dirty before this planning work.
- Existing modified/tracked state includes `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/*review*`, `.context/status.md`, `docs/index.md`, `docs/phase.md`, and added `prototype/*` files.
- `.context/` files currently exist and are empty in the working tree.
- `frontend/` currently contains only:
  - `frontend/Dockerfile`
  - `frontend/index.md`
- No `package.json`, lockfile, `components.json`, Tailwind config, Vite config, or TypeScript config exists yet.
- `frontend/index.md` says frontend dependency install, dev server, lint/typecheck, tests, and build are not available yet.
- `frontend/Dockerfile` is still a placeholder that prints that the React app is not implemented.
- `docker-compose.yml` defines `frontend` with build context `./frontend` and `VITE_API_BASE_URL=http://localhost:${BACKEND_PORT:-8000}/api`.
- Planning review resolution explicitly defers replacing `frontend/Dockerfile` to Phase 32 runtime finalization. Phase 24 may leave it as a placeholder because current phase validation does not require Compose/frontend-container launch.
- Backend API routes are already mounted under `/api`.
- Implemented auth endpoints:
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- Current backend auth response/request schemas:
  - `RegisterRequest`: `email`, `password`
  - `LoginRequest`: `email`, `password`
  - `TokenResponse`: `access_token`, `token_type`
  - `UserResponse`: `id`, `email`, `role`, `is_active`, `created_at`, `updated_at`
- No backend `POST /api/auth/logout` route exists in current code. Docs allow frontend logout by deleting local token.
- Admin-only backend endpoints exist for stats, jobs, users, and storage cleanup.
- Prototype exists under `prototype/` and is explicitly documented as a static UI reference, not production app code or API contract.
- Prototype has React UMD/Babel, CSS variables, compact dark dashboard styling, icon-only desktop sidebar, mobile drawer, auth pages, page modules, status badges, metric cards, skeletons, empty states, progress bars, tabs, toasts, upload controls, jobs, job detail, models, experiments, and admin mock screens.

## Existing implementation state

- Backend is implemented beyond auth: media, jobs/results/downloads, models, experiments, admin APIs, OpenAPI contract tests, and backend tests exist.
- CV worker and training folders exist, but Phase 24 should not modify worker or training code.
- Frontend production app is not scaffolded.
- Frontend Phase 24 must create Vite/React/TypeScript foundation and auth routing only.
- Frontend Phase 24 must not implement later pages beyond route shells/placeholders needed for protected/admin routing.
- Prototype UI may guide frontend layout and visual system, but mock data/actions in prototype must not become product contracts.

## Unknowns and assumptions

- Risk level was not filled in by user. Assumption: `MEDIUM`.
- Package manager is not established by repo files. Assumption: implementation may choose a standard Vite-compatible npm setup unless user or repo later provides another package manager.
- shadcn/ui setup details are absent because `components.json` does not exist yet. Assumption: Phase 24 must initialize baseline shadcn/ui config in `frontend/`.
- Icon package is not established because no `package.json` exists. Assumption from `$design-taste-frontend`: after package creation, use one approved icon import family such as `@radix-ui/react-icons` or `@phosphor-icons/react`, not emoji or ad hoc text symbols.
- Backend does not expose a public registration-settings endpoint in the docs or code. Assumption: disabled registration handling can be based on `POST /api/auth/register` returning `403`, and the register page can show a Ukrainian notice/error after that response.
- The prototype contains demo credential hints and mock route behavior. Assumption: production UI must not hard-code prototype credentials or mock login shortcuts.
- The prototype text appears mojibake in terminal output due encoding display, but docs require Ukrainian visible UI text.
- Planning review resolution keeps the risk assumption as `MEDIUM`; no user instruction or product doc requires treating this phase as `HIGH`.

## Files likely relevant for implementation

- `frontend/package.json`
- `frontend/package-lock.json` or chosen lockfile
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/index.css`
- `frontend/src/router/*`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/auth/AuthProvider.tsx`
- `frontend/src/auth/ProtectedRoute.tsx`
- `frontend/src/auth/AdminRoute.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/RegisterPage.tsx`
- `frontend/src/pages/*Placeholder*.tsx`
- `frontend/src/components/*`
- `frontend/src/lib/utils.ts`
- `frontend/components.json`
- `frontend/Dockerfile`
- `frontend/index.md`
- `docker-compose.yml`
- Prototype references:
  - `prototype/index.md`
  - `prototype/styles.css`
  - `prototype/ui.jsx`
  - `prototype/auth.jsx`
  - `prototype/sidebar.jsx`
