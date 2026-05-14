# Independent Planning Review - Phase 24

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 24 scope: React/Vite/TypeScript scaffold, Tailwind/shadcn baseline, API client, auth state, protected routes, admin guard, `/login`, `/register`, and minimal Ukrainian placeholders for later routes.

No product-doc mismatch, architecture mistake, backend/frontend boundary violation, CV-safety issue, or security blocker found. One important validation gap should be fixed before implementation: backend-backed auth smoke is required by phase validation but not made explicit enough in the plan.

## Blocking issues

None.

## Important issues

1. Backend-backed auth smoke is missing as a required validation step.

   Evidence:
   - `docs/phase.md:28-35` requires auth smoke flow against backend: frontend install, lint/typecheck/build, Ukrainian login/register, protected redirects, non-admin `/admin` rejection, and "Auth smoke flow works against backend."
   - `.context/plan.md:35-39` runs route/component tests "if configured" and manual browser smoke "if dev server exists", but does not require submitting login/register against the real backend or verifying `/api/auth/me` after token storage.
   - `docs/API.md:98-100` defines the auth contract this phase must consume: register conditional, login guest-only, `/api/auth/me` protected.

   Required change: make implementation validation explicitly include a backend-backed auth smoke when backend is available: login with seeded/admin or test user, token stored, `/api/auth/me` loads current user, protected route renders after auth, logout clears token, and disabled registration `403` shows Ukrainian notice. If backend is unavailable, record exact blocker rather than treating route-only tests as sufficient.

2. Manual browser smoke is too conditional for a newly scaffolded Vite app.

   Evidence:
   - Phase 24 creates the frontend scaffold and validation requires rendered pages (`docs/phase.md:6-19`, `docs/phase.md:28-35`).
   - `.context/plan.md:39` says "Run manual browser smoke if dev server exists"; after successful scaffold/install, a dev server should exist.

   Required change: make manual browser smoke mandatory after `npm run dev`/equivalent starts, covering `/login`, `/register`, guest protected redirect, user shell, admin guard, and mobile shell. If the dev server cannot start, record the failing command as a blocker.

## Optional improvements

1. Explicitly state whether `frontend/Dockerfile` remains placeholder for Phase 32 or is updated in Phase 24.

   Evidence:
   - `.context/research.md:29-33` notes `frontend/Dockerfile` is currently a placeholder.
   - Phase 24 validation does not require Compose/frontend container launch, so deferring Dockerfile work is acceptable if documented.

2. Add a quick text-search review gate for Ukrainian UI and forbidden prototype carryover.

   Evidence:
   - `docs/FRONTEND_UX.md:29-47` requires Ukrainian visible text.
   - `.context/design.md:34-41` says prototype is visual reference only and mock credentials/actions must not be copied.

## Questions for resolution

1. Risk level was provided as placeholder `<MEDIUM | HIGH>` in the prompt. `.context/research.md` assumes `MEDIUM`; confirm if this should be treated as `HIGH` before implementation.

2. Should Phase 24 update `frontend/Dockerfile`, or explicitly defer Dockerfile replacement to Phase 32 runtime finalization?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
