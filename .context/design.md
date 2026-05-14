# Design - Phase 24 Frontend scaffold, API client, auth, and protected routing

## Phase goal

Create the production frontend foundation under `frontend/` using React, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, and the backend `/api` contract. Implement only auth pages, auth state, API client base, protected route wrapper, admin route guard, and route placeholders needed to prove routing.

## Intended behavior from docs

Confirmed:

- Visible frontend UI text must be Ukrainian.
- Code identifiers, route names, API fields, database fields, logs, and developer comments stay English.
- Required frontend routes include `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`.
- Protected routes redirect unauthenticated users to `/login`.
- Admin routes reject or redirect non-admin users.
- Guests must not see authenticated dashboard navigation.
- Admin navigation appears only for admin users.
- Login page needs email input, password input, login button, registration link when public registration is enabled or appropriate registration UX, error display, and loading state.
- Registration page needs email, password, confirm password, registration button, login link, validation messages, and visible minimum password length rule.
- Public registration disabled state should redirect to login or show a Ukrainian notice.
- Frontend logout may delete local JWT because backend logout endpoint is optional and currently absent.
- Backend remains authorization source of truth. Frontend hiding controls is not security enforcement.
- API responses, UI text, and exports must stay inside CV-only boundary and must not imply targeting, navigation, interception, or hardware control.

Assumptions:

- Because no registration-settings endpoint exists, the register page cannot know disabled-registration state before submit unless implementation later adds a documented backend capability. For Phase 24, map `403` from `POST /api/auth/register` to a Ukrainian disabled-registration notice.
- Use `localStorage` or equivalent browser storage for the JWT in this phase unless implementation review chooses a safer documented pattern. Do not store passwords or user secrets beyond the access token.
- Route placeholders for later pages should be minimal Ukrainian protected/admin shells, not full Phase 25-31 feature pages.

## Architecture decisions

- Production frontend must live under `frontend/`; do not convert `prototype/` into production code.
- Use prototype as visual reference:
  - dark dashboard surface;
  - compact left icon sidebar for authenticated layout;
  - mobile top bar/drawer;
  - `AeroVision` brand mark;
  - muted slate/charcoal palette with green accent around `#3d8b6a`;
  - compact metric/card/table visual grammar;
  - skeletons, badges, empty/error blocks, progress primitives where needed.
- Do not copy prototype mock state, mock data, demo credentials, edit/tweaks panel, UMD/Babel loading pattern, or inline global `window.*` module style.
- Use React Router for route definitions and redirects.
- Use TanStack Query for `/api/auth/me` current-user query and future API calls.
- Build a small API client around `VITE_API_BASE_URL`, JSON requests, `Authorization: Bearer <token>`, typed error normalization, and file-download compatibility for later phases.
- Build auth provider/state around token persistence, login mutation, register mutation, current-user query, and logout token deletion.
- Keep route guards thin:
  - `ProtectedRoute` waits for current-user query when token exists;
  - redirects guests to `/login`;
  - rejects inactive/missing users by clearing token and redirecting;
  - `AdminRoute` checks `user.role === "admin"` and shows/redirects with Ukrainian forbidden handling.
- shadcn/ui components should be customized to match the prototype, not left as generic defaults.
- No emoji in markup, text, alt text, or code-generated UI symbols.
- Keep frontend away from PostgreSQL, shared storage internals, direct CV inference, and absolute filesystem paths.

## Backend impact

- No backend source changes in this phase.
- Frontend consumes existing backend auth endpoints:
  - `POST /api/auth/login`
  - `POST /api/auth/register`
  - `GET /api/auth/me`
- Frontend may define typed client wrappers for other existing endpoints, but must not create calls to undocumented or unimplemented routes.
- Backend `POST /api/auth/logout` is not currently implemented; frontend logout must use client token deletion.

## Frontend impact

- Create Vite React TypeScript scaffold.
- Add dependency manifest and scripts for dev, build, lint/typecheck, and test if test tooling is added.
- Add Tailwind and shadcn/ui baseline.
- Add production source structure for app shell, routes, auth, API client, shared UI, and utilities.
- Leave `frontend/Dockerfile` replacement out of Phase 24 unless implementation uncovers a direct scaffold need; Docker runtime finalization belongs to Phase 32.
- Implement `/login` and `/register` fully for Phase 24.
- Implement authenticated shell/guard wiring enough to verify protected and admin routing.
- Add minimal Ukrainian placeholders for later protected pages only when needed for route tests.
- Keep later feature pages out of scope:
  - no real dashboard metrics;
  - no upload flow;
  - no jobs table/details;
  - no models management;
  - no experiments charts;
  - no admin data panels.

## DB impact

- No database schema, migration, seed, or persistence changes.

## API impact

- No API contract changes.
- Client types must mirror current backend schemas or be generated from/checked against backend OpenAPI if implementation chooses that route.
- Do not invent request fields, response fields, routes, filters, or settings endpoints.

## Security/privacy impact

- Do not log or display passwords, JWTs, token storage contents, backend stack traces, database passwords, or sensitive environment values.
- Do not hard-code demo credentials from prototype.
- Do not expose raw backend error details when they are unsafe; map known auth errors to Ukrainian UI messages.
- Enforce guest-only UX for login/register by redirecting authenticated users away from guest auth pages or preventing duplicate auth submissions.
- Enforce admin route visibility and route guard in frontend, while documenting that backend authorization remains authoritative.
- Token storage must be cleared on logout, invalid token, inactive-user response, or `/api/auth/me` unauthorized response.

## Test strategy

Relevant checks only:

- Frontend dependency install: after scaffold exists, run chosen package install command.
- Frontend lint/typecheck/build: run configured commands from `frontend/`.
- Frontend route/component tests if scaffolded:
  - `/login` renders Ukrainian login form;
  - `/register` renders Ukrainian registration form;
  - short password validation appears in Ukrainian;
  - failed login shows Ukrainian error;
  - disabled registration `403` maps to Ukrainian notice/error;
  - protected route redirects guest to `/login`;
  - admin nav hidden for `user`;
  - `/admin` rejects non-admin;
  - admin nav visible for `admin`.
- Manual browser smoke when dev server exists:
  - login page loads;
  - registration page loads;
  - protected placeholders redirect guests;
  - authenticated shell matches prototype layout at desktop and mobile widths.
- Manual browser smoke is mandatory after the Vite dev server starts. If the dev server cannot start, record the exact failing command as a blocker.
- Backend-backed auth smoke is required when the backend is available:
  - submit login with seeded admin or a test user;
  - verify token storage;
  - verify `/api/auth/me` loads the current user;
  - verify a protected route renders after auth;
  - verify logout clears the token;
  - verify disabled registration `403` maps to a Ukrainian notice.
- If the backend is unavailable, record the exact blocker instead of treating route-only tests as sufficient.
- Add a text-search review gate for Ukrainian UI coverage, raw prototype mock credentials/actions, emoji, `frame_stride`, absolute-path display, and targeting/navigation/interception wording.
- Backend tests are not required for this frontend-only phase unless frontend work reveals a backend contract mismatch.

## Ambiguities or conflicts

- No `WARNING: CONFLICT` found among consulted Phase 24 docs.
- User prompt used placeholders for phase title and risk level. Current phase was identified from `docs/phase.md`; risk level remains an assumption.
- Prototype is a UI reference only, while docs remain source of truth for product behavior. Any prototype behavior absent from docs must not be treated as required product behavior.
- Docs mention registration link when public registration is enabled, but no backend endpoint exposes that setting to frontend. Phase 24 should handle disabled registration through `403` from register attempt unless a documented settings endpoint is later added.
- Planning review resolution leaves risk level as the documented `MEDIUM` assumption because the user did not specify `HIGH`.
