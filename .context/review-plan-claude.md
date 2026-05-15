# Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 32 scope at high level: Docker runtime, frontend container, Compose CPU/GPU wiring, Makefile shortcuts, README/implementation docs, and targeted runtime validation. No source-code implementation outside DevOps/docs is proposed.

Approval needs changes because plan misses some Phase 32 validation evidence and under-scopes existing implementation-doc conflicts that affect first-launch accuracy.

## Blocking issues

None.

## Important issues

1. Missing database health endpoint validation.
   - Evidence: `docs/phase.md` Phase 32 validation says "Backend health endpoints work." `docs/TESTING_QA.md` Docker and launch tests require backend health endpoint and backend database health endpoint. `.context/plan.md` step 11 verifies only `http://localhost:8000/api/health`.
   - Risk: Compose may launch with API process healthy while DB connectivity is broken after migration/seed startup. Phase 32 can be marked complete without proving `/api/health/db`.
   - Required change: Add `/api/health/db` smoke after startup.

2. Missing seeded-admin existence check.
   - Evidence: `docs/phase.md` Phase 32 validation says "Seeded admin exists." `docs/AUTH_SECURITY.md` requires seeded admin from `ADMIN_EMAIL` and `ADMIN_PASSWORD`, hashed before storage. `.context/plan.md` step 11 verifies migrations/setup run, but does not verify admin row/login/existence.
   - Risk: Startup may run setup but fail to create expected admin, leaving first-launch flow broken.
   - Required change: Add targeted verification that seeded admin exists after startup, preferably through existing backend/auth behavior or a safe backend container command that does not print secrets.

3. Implementation-doc conflict cleanup is too narrow.
   - Evidence: `.context/research.md` reports `README.md` says CV model loading, queue polling/claiming, inference, tracking, exports, and React/Vite frontend UI are unavailable, while `cv/index.md` says worker queue/inference/tracking/exports exist and `frontend/index.md` says Phase 31 frontend exists. `docs/index.md` current state is also older than `frontend/index.md`. `.context/plan.md` step 7 focuses mainly on docs made stale by Phase 32 and says only to verify no doc still says frontend Dockerfile is placeholder.
   - Risk: Phase 32 README/first-launch docs can remain internally contradictory, violating `docs/phase.md` requirement for accurate README startup instructions and `docs/index.md` update rule for current implementation state.
   - Required change: Include cleanup of all current implementation-state conflicts found in README/component indexes/docs index, not only frontend Docker runtime claims.

4. Startup smoke command lacks execution shape for reliable evidence.
   - Evidence: `.context/plan.md` step 11 uses `docker compose --env-file .env.example up --build` as a long-running foreground command. `docs/phase.md` requires confirming services start, frontend reachable, backend health works, worker logs selected device, and README accuracy.
   - Risk: Foreground `up` can block the implementation session and make health/log checks and teardown inconsistent.
   - Required change: Specify detached startup, health/log checks, and cleanup, or another bounded smoke method that records evidence without leaving services running.

## Optional improvements

1. Clarify frontend API-base injection for the container.
   - Evidence: `.context/design.md` says frontend Docker runtime should use existing Vite app and `VITE_API_BASE_URL`; `.context/plan.md` says "build/runtime API base" but not exactly how the browser bundle receives it.
   - Risk: Vite env handling is easy to miswire during Docker build/serve changes.
   - Suggested change: State whether `VITE_API_BASE_URL` is passed at image build time, served through runtime config, or intentionally handled by Vite dev/preview runtime.

## Questions for resolution

None.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`
- `README.md`
- `backend/index.md`
- `frontend/index.md`
- `cv/index.md`
- `training/index.md`
- `training/README.md`
- `prototype/index.md`
