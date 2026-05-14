# Plan - Phase 24 Frontend scaffold, API client, auth, and protected routing

1. `@role/developer-frontend` Verify no existing frontend scaffold files beyond `frontend/Dockerfile` and `frontend/index.md`; record any new user changes before editing. Verifiable by `git status --short` and `rg --files frontend`.

2. `@role/developer-frontend` Scaffold a Vite React TypeScript app under `frontend/` with package manifest, TypeScript config, Vite config, `index.html`, and `src/` entrypoint. Verifiable by expected scaffold files existing and no source files outside `frontend/` changed except documented Docker/index updates if needed.

3. `@role/developer-frontend` Add required frontend dependencies for this phase: React, React DOM, Vite, TypeScript, Tailwind CSS, shadcn/ui baseline dependencies, React Router, TanStack Query, form validation tooling if used, and exactly one approved icon import family after dependency verification. Verifiable by `frontend/package.json`.

4. `@role/developer-frontend` Configure Tailwind and shadcn/ui baseline to match prototype visual direction: dark charcoal/slate surfaces, green accent, compact radius, dashboard typography, no emoji, responsive layout tokens. Verifiable by Tailwind/shadcn config and CSS variables/classes.

5. `@role/developer-frontend` Build shared UI primitives needed for Phase 24 only: button, input/form field, alert/error block, skeleton/loading state, app logo mark, and route placeholder shell. Verifiable by components imported by auth pages and route guards.

6. `@role/developer-frontend` Implement API base client using `VITE_API_BASE_URL`, JSON request/response handling, bearer token injection, typed normalized errors, and no logging of tokens or passwords. Verifiable by `frontend/src/api/*` and tests or typecheck.

7. `@role/developer-frontend` Add auth API wrappers matching current backend schemas only: `login(email,password)`, `register(email,password)`, `getCurrentUser()`. Do not add logout API call because current backend has no `POST /api/auth/logout`. Verifiable by route strings and request/response types.

8. `@role/developer-frontend` Implement auth token storage, logout token deletion, current-user query, invalid-token cleanup, and authenticated-user context/provider. Verifiable by auth provider tests or route smoke.

9. `@role/developer-frontend` Implement React Router route tree for `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`. Later-phase routes get minimal Ukrainian placeholders only. Verifiable by route tests/build.

10. `@role/developer-frontend` Implement `ProtectedRoute` for authenticated routes: guests redirect to `/login`; token-present state waits for `/api/auth/me`; inactive/unauthorized responses clear token and redirect. Verifiable by route tests.

11. `@role/developer-frontend` Implement `AdminRoute` and admin navigation visibility: users cannot see admin nav and cannot access `/admin`; admins can see admin nav. Verifiable by route tests.

12. `@role/developer-frontend` Implement `/login` page based on prototype visual style and docs: email, password, submit, registration link, loading, Ukrainian validation/errors, and no hard-coded demo credentials. Verifiable by component tests and manual render.

13. `@role/developer-frontend` Implement `/register` page based on prototype visual style and docs: email, password, confirm password, minimum 8-character rule, login link, Ukrainian validation/errors, role fixed by backend, and `403` disabled-registration notice. Verifiable by component tests.

14. `@role/developer-frontend` Implement authenticated shell based on prototype: compact desktop icon sidebar, mobile top bar/drawer, Ukrainian nav labels, admin item conditional on role, logout action. Verifiable by route tests and manual responsive smoke.

15. `@role/developer-auth-security` Review frontend auth/security behavior: no password/token logging, no prototype demo credentials, no frontend-only authorization claims, no absolute paths, no CV targeting/navigation/interception wording. Verifiable by code review and text search.

16. `@role/tester` Run frontend install from `frontend/`. Verifiable command: chosen install command returns `PASS`; if package manager cannot run, record exact blocker.

17. `@role/tester` Run frontend lint/typecheck/build from `frontend/`. Verifiable commands must be exact package scripts and return `PASS`.

18. `@role/tester` Run route/component tests if configured. Verifiable tests cover login, register, protected redirect, admin guard, admin nav visibility, logout token cleanup, `/api/auth/me` current-user handling through mocked client behavior, disabled-registration `403`, and Ukrainian auth error states.

19. `@role/tester` Run mandatory manual browser smoke after the Vite dev server starts: `/login`, `/register`, guest protected redirect, user shell, admin route guard, mobile width shell. If the dev server cannot start, record the exact failing command as a blocker.

20. `@role/tester` Run backend-backed auth smoke when backend is available: submit login with seeded admin or a test user, verify token storage, verify `/api/auth/me` loads current user, verify protected route renders after auth, verify logout clears token, and verify disabled registration `403` shows a Ukrainian notice. If backend is unavailable, record the exact blocker rather than treating route-only tests as sufficient.

21. `@role/tester` Run text-search review gates for Ukrainian visible UI coverage, forbidden prototype mock credentials/actions, emoji, `frame_stride`, absolute-path display, and targeting/navigation/interception wording. Verifiable by exact search commands and review notes.

22. `@role/docs-maintainer` Update only frontend-local implementation docs if commands/files changed: `frontend/index.md` and root README command status if required by repo conventions. Do not modify product docs. `frontend/Dockerfile` replacement is deferred to Phase 32 unless a direct Phase 24 scaffold need is discovered and documented. Verifiable by diff limited to implementation docs, not `docs/*.md`.

23. `@role/code-reviewer` Review implementation against this contract, `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/AUTH_SECURITY.md`, and `docs/TESTING_QA.md`. Verifiable by findings resolved before final output.
