# Phase 32 Design

## Phase goal

Finalize local/demo Docker runtime and first-launch documentation for Phase 32 only.

Confirmed goal from `docs/phase.md`:

- Complete app launches from clean local setup.
- Compose includes `postgres`, `backend`, `cv-worker`, and `frontend`.
- CPU mode works by default.
- Optional GPU mode affects only `cv-worker`.
- README explains setup, env, model artifacts, startup, seeded admin policy, CPU/GPU notes, troubleshooting, and large-file policy.

Risk level:

- Assumption: HIGH because this phase joins all services and docs. No user risk value was provided.

## Intended behavior from docs

Confirmed:

- Runtime services remain `postgres`, `backend`, `cv-worker`, and `frontend`.
- Backend and CV worker must mount same shared storage at `/app/storage`.
- PostgreSQL stores structured data only; storage keeps uploads, results, reports, models, temp files, and datasets.
- Backend startup may run Alembic migrations and idempotent seed/setup in local/demo mode.
- Seeded admin comes from `ADMIN_EMAIL` and `ADMIN_PASSWORD`; password is hashed by setup.
- Secrets, admin password, JWT secret, DB password, tokens, and sensitive env values must not be logged or committed.
- Frontend calls backend REST API only.
- CV worker waits/retries for PostgreSQL and logs selected device at startup.
- GPU support is optional and isolated to `cv-worker`.
- Base app must run without GPU.
- Docs must not promise fixed FPS.
- Model weights and training artifacts are placed under storage by humans; app registers/imports artifacts, not training jobs.
- Generated datasets, weights, uploads, results, reports, and temp files stay out of Git.

## Architecture decisions

Confirmed decisions:

- Keep existing service names: `postgres`, `backend`, `cv-worker`, `frontend`.
- Keep backend and worker storage mount identical: host `./storage`, container `/app/storage`.
- Keep backend startup flow in `backend/startup.sh`: optional migrations, optional setup, then Uvicorn.
- Keep PostgreSQL healthcheck as service readiness source.
- Keep worker DB retry behavior in worker startup; do not add backend-worker HTTP coupling.
- Keep GPU override in `docker-compose.gpu.yml`; only `cv-worker` may request GPU devices or force `CV_DEVICE=cuda`.
- Do not add Celery, Redis, Flask, Streamlit, RTSP/live camera, training launch, or extra runtime services.

Design choices for implementation:

- Replace placeholder `frontend/Dockerfile` with container runtime for existing Vite app.
- Publish frontend service through `${FRONTEND_PORT:-5173}:5173`.
- Use Vite build-time API-base injection for Docker runtime: pass `VITE_API_BASE_URL=http://localhost:${BACKEND_PORT:-8000}/api` as a frontend build argument/environment value during image build, because browser bundles cannot read Compose runtime environment after static build without a separate runtime-config mechanism.
- Add service healthchecks where practical: keep PostgreSQL; add backend `/api/health`; add frontend reachability after frontend runtime exists. Worker does not need public HTTP health endpoint.
- Expand Makefile with shortcuts for storage setup, Compose config, CPU launch, GPU launch, logs, migrations, seed, and relevant tests.
- Update implementation docs to match actual Phase 32 runtime state and remove stale "frontend not available" and stale CV-worker unavailable claims.

## Backend impact

Touched only through runtime wiring unless implementation discovers a missing healthcheck dependency.

- No new API routes.
- No schema changes.
- No auth behavior changes.
- Backend health endpoint already exists and can support Compose healthcheck.
- Startup migrations and setup already exist; Phase 32 should verify and document them.

## Frontend impact

Touched through container/runtime wiring.

- Existing Vite React app should be served by the `frontend` service.
- Existing `VITE_API_BASE_URL` contract should be used.
- No route/page/product UI changes planned.
- No new user-facing text planned except documentation if needed.

## DB impact

No schema/model changes planned.

- PostgreSQL service config remains.
- Existing volume `postgres_data` remains.
- Migrations run through backend startup or Makefile/manual commands.

## API impact

No endpoint contract changes planned.

- `/api/health` used for runtime healthcheck.
- `/api/health/db` must be included in Phase 32 startup smoke validation to prove database connectivity after launch.

## Security/privacy impact

Touched surfaces:

- `.env.example`
- Compose env wiring
- README/admin credential policy
- logs/troubleshooting docs

Security decisions:

- `.env.example` keeps placeholders only.
- README must instruct replacing placeholder secrets before real use.
- README must avoid placing JWT tokens in command history; training docs already prefer env var for admin JWT.
- Compose/Makefile commands must not print real secrets beyond normal Docker env interpolation.
- Docs must not include real credentials, tokens, database passwords, or model artifacts.
- GPU override must not grant GPU access to backend/frontend/postgres.

## Test strategy

Relevant checks for Phase 32:

- `docker compose --env-file .env.example config`
- `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1`
- `npm run build` from `frontend/` after frontend Docker/runtime changes.
- `docker compose --env-file .env.example build frontend`
- Bounded CPU startup smoke with detached Compose: `docker compose --env-file .env.example up --build -d`, followed by health/log checks and `docker compose --env-file .env.example down`.
- Backend health smoke: request `http://localhost:8000/api/health`.
- Backend database health smoke: request `http://localhost:8000/api/health/db`.
- Seeded admin smoke: verify the configured admin exists without printing secrets, preferably through seeded-admin login or a safe backend container/database command.
- Frontend reachability smoke: request `http://localhost:5173`.
- Worker log smoke: confirm `device_selected` appears and selected device is CPU in base launch.
- GPU config audit: rendered GPU Compose config shows GPU request only under `cv-worker`.

Checks intentionally not generic:

- No backend unit test suite required unless backend code changes.
- No CV processing tests required unless worker processing code changes.
- No frontend route/component tests required unless frontend source behavior changes.
- No migration-generation command; no schema change.

## Ambiguities or conflicts

WARNING: CONFLICT

- `README.md` still reports frontend UI/tests/build as unavailable.
- `frontend/index.md` reports implemented Phase 31 frontend with commands.
- `docs/index.md` current implementation state appears older than `frontend/index.md`.
- Resolve by updating implementation docs during Phase 32; do not change product contracts.

Ambiguities:

- User did not provide risk level; HIGH assumed.
- `all implementation docs` is broad. Assumption: update README and any index docs that become inaccurate due runtime command/status changes.
- Frontend serving method is not fixed by docs. Existing service should serve the Vite app without adding another service.
- GPU runtime cannot be fully proven without NVIDIA host setup; config audit is required, real GPU launch is optional.
