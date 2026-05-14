## Phase 24 - Frontend scaffold, API client, auth, and protected routing

**Direction:** Frontend
**Goal:** Create the React frontend foundation after backend contracts are stable.

### Scope

- Scaffold `frontend/` with Vite, React, TypeScript.
- Add Tailwind CSS and shadcn/ui baseline.
- Add React Router, TanStack Query, React Hook Form/Zod if used for forms, Recharts, and supporting UI libraries.
- Add frontend folder structure for app shell, routes, features, shared components, API client, and utilities.
- Add typed API client for `/api` endpoints.
- Add auth token storage strategy and logout behavior.
- Implement current-user query and auth state.
- Implement protected route wrapper.
- Implement admin route guard.
- Implement `/login` and `/register` pages.
- Map backend errors to Ukrainian UI messages.
- Ensure public registration disabled state redirects or shows Ukrainian notice.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Frontend install succeeds.
- Frontend lint/typecheck/build pass.
- Login page renders in Ukrainian.
- Registration page renders in Ukrainian and handles disabled-registration behavior.
- Protected routes redirect guests to login.
- Non-admin users cannot access `/admin` route.
- Auth smoke flow works against backend.

### Commit

`feat(frontend): scaffold React app auth and protected routing`
