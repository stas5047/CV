# Phase 32 Plan

Scope: `Phase 32 - Final Docker runtime, GPU override, README, and first-launch flow`.

Risk: HIGH assumed because user risk placeholder was not filled.

Rules:

- No product behavior changes.
- No new API routes.
- No DB schema changes.
- No CV inference/training changes.
- No extra runtime services.
- CPU launch required; GPU optional and isolated to `cv-worker`.

## Ordered implementation plan

1. [ ] `@role/developer-devops` Confirm dirty worktree before edits.
   - Run: `git status --short`
   - Verify: note pre-existing modified files; do not revert unrelated changes.

2. [ ] `@role/developer-devops` Finalize frontend container runtime.
   - Modify likely files: `frontend/Dockerfile`, `frontend/package.json`, `frontend/package-lock.json` if package scripts change.
   - Replace placeholder container behavior with existing Vite app build/serve flow.
   - Preserve `VITE_API_BASE_URL` use.
   - Use Vite build-time API-base injection for Docker runtime: pass `VITE_API_BASE_URL=http://localhost:${BACKEND_PORT:-8000}/api` during frontend image build unless a repo-native runtime-config mechanism already exists.
   - Verify: frontend image can build and serve app on port `5173`.

3. [ ] `@role/developer-devops` Finalize base Compose runtime.
   - Modify likely file: `docker-compose.yml`.
   - Keep services: `postgres`, `backend`, `cv-worker`, `frontend`.
   - Keep backend and worker storage mount at `/app/storage`.
   - Publish backend via `${BACKEND_PORT:-8000}:8000`.
   - Publish frontend via `${FRONTEND_PORT:-5173}:5173`.
   - Wire frontend build/runtime API base to `http://localhost:${BACKEND_PORT:-8000}/api`.
   - Add backend healthcheck against `/api/health`.
   - Add frontend reachability healthcheck after frontend runtime exists.
   - Keep PostgreSQL healthcheck.
   - Do not add backend-worker HTTP calls.
   - Verify: `docker compose --env-file .env.example config` succeeds.

4. [ ] `@role/developer-devops` Audit GPU override.
   - Modify likely file only if needed: `docker-compose.gpu.yml`.
   - Keep GPU device request and `CV_DEVICE=cuda` only under `cv-worker`.
   - Do not add GPU settings to backend, frontend, or postgres.
   - Verify: rendered GPU config shows GPU reservation only for `cv-worker`.

5. [ ] `@role/developer-devops` Expand Makefile shortcuts.
   - Modify likely file: `Makefile`.
   - Keep existing storage/config targets.
   - Add or normalize targets for local setup, migration, seed, logs, tests, CPU launch, optional GPU launch.
   - Use `docker compose`, not legacy `docker-compose`.
   - Verify: listed targets invoke documented commands and do not require real secrets.

6. [ ] `@role/docs-maintainer` Update first-launch docs.
   - Modify likely file: `README.md`.
   - Document prerequisites, `.env` setup, placeholder secret replacement, storage bootstrap, model artifact placement/registration, one-command CPU startup, seeded admin policy, CPU/GPU notes, troubleshooting, and large-file/Git policy.
   - Remove stale "frontend not available" claims if frontend Docker runtime is finalized.
   - Remove stale CV-worker unavailable claims if current worker index/code state shows queue/inference/tracking/export support is implemented.
   - Do not duplicate full product specs from canonical docs.
   - Verify: README commands match actual files and Makefile/Compose targets.

7. [ ] `@role/docs-maintainer` Update implementation indexes only where made stale by Phase 32 changes.
   - Likely files: `frontend/index.md`, `docs/index.md`.
   - Possible files: `backend/index.md`, `cv/index.md`, `training/index.md`.
   - Clean up all current implementation-state conflicts found in README/component indexes/docs index, including stale frontend and CV-worker availability/status claims.
   - Update only current-state and command/status entries changed by runtime/doc work or already-conflicting implementation-state summaries.
   - Do not change canonical product contracts.
   - Verify: no implementation doc still says frontend Dockerfile is placeholder after it is finalized.
   - Verify: implementation docs do not contradict each other on current frontend or CV-worker availability.

8. [ ] `@role/tester` Validate Compose configuration.
   - Run: `docker compose --env-file .env.example config`
   - Expected: PASS.
   - Run: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config`
   - Expected: PASS; only `cv-worker` has GPU request.

9. [ ] `@role/tester` Validate storage bootstrap.
   - Run: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1`
   - Expected: PASS; `storage/uploads`, `storage/results`, `storage/reports`, `storage/models`, `storage/temp`, and `storage/datasets` exist.

10. [ ] `@role/tester` Validate frontend build/runtime surface if frontend Docker/package changed.
    - Run from `frontend/`: `npm run build`
    - Expected: PASS.
    - Run from repo root: `docker compose --env-file .env.example build frontend`
    - Expected: PASS.

11. [ ] `@role/tester` Run Phase 32 CPU startup smoke.
    - Run: `docker compose --env-file .env.example up --build -d`
    - Expected: `postgres`, `backend`, `cv-worker`, and `frontend` start.
    - Verify: backend startup runs migrations/setup when `RUN_MIGRATIONS_ON_START=true` and `RUN_SEED_ON_START=true`.
    - Verify: seeded admin exists, preferably by authenticating with configured `.env` credentials through `POST /api/auth/login` or by a safe backend container/database command that does not print secrets.
    - Verify: worker logs `device_selected` with CPU in base config.
    - Verify: frontend reachable at `http://localhost:5173`.
    - Verify: backend health reachable at `http://localhost:8000/api/health`.
    - Verify: backend database health reachable at `http://localhost:8000/api/health/db`.
    - Cleanup: run `docker compose --env-file .env.example down` after evidence is captured.

12. [ ] `@role/developer-auth-security` Audit security/privacy after runtime/doc changes.
    - Verify `.env.example` contains placeholders only.
    - Verify README does not include real secrets, tokens, database passwords, admin passwords beyond placeholders, or fixed FPS promises.
    - Verify Compose/Makefile do not route secrets into logs beyond normal env usage.
    - Verify GPU override affects only `cv-worker`.

13. [ ] `@role/code-reviewer` Review Phase 32 diff against docs.
    - Check against `docs/ARCHITECTURE.md`, `docs/AUTH_SECURITY.md`, `docs/TRAINING_EXPERIMENTS.md`, `docs/TESTING_QA.md`, and implementation docs.
    - Flag scope creep, new services, unsafe secret docs, mismatched storage mounts, missing frontend port/runtime, stale README/index claims, and GPU leakage outside worker.

14. [ ] `@role/tester` Record final quality gates.
    - Report each command as `PASS`, `FAIL`, or `not available`.
    - If `docker compose up --build` fails because model artifacts or host dependencies are absent, record exact blocker and do not mark complete.

## Out of scope for this phase

- Backend API route changes.
- DB schema or Alembic migration changes.
- CV queue/inference/tracking/export logic changes.
- Frontend page/UX feature changes.
- Training execution.
- New runtime services.
- Production deployment hardening beyond local/demo Compose.
