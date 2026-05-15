## Phase 32 - Final Docker runtime, GPU override, README, and first-launch flow

**Direction:** DevOps / Documentation
**Goal:** Make the complete application launchable and understandable from a clean local setup.

### Scope

- Finalize `docker-compose.yml` for:
  - `postgres`;
  - `backend`;
  - `cv-worker`;
  - `frontend`.
- Finalize optional GPU override/profile for `cv-worker` only.
- Ensure backend startup can run migrations and seed/setup in local/demo mode.
- Ensure storage directories are created or verified.
- Ensure frontend connects to backend through Docker/local configuration.
- Ensure backend and worker share the same storage mount path.
- Ensure worker waits for or retries database availability.
- Add service health checks where practical.
- Add Makefile or script shortcuts for:
  - local setup;
  - migration;
  - seed;
  - logs;
  - tests;
  - CPU launch;
  - optional GPU launch.
- Update README with:
  - prerequisites;
  - `.env` setup;
  - model artifact placement/registration;
  - one-command startup;
  - seeded admin credentials policy;
  - CPU/GPU notes;
  - troubleshooting;
  - large-file/Git policy.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/TESTING_QA.md`
- all implementation docs

### Validation

- `docker compose config` succeeds.
- `docker compose up --build` starts all base services in CPU mode after documented setup.
- Backend migrations apply automatically in local/demo mode.
- Idempotent seed/setup runs automatically in local/demo mode.
- Seeded admin exists.
- Frontend is reachable in the browser.
- Backend health endpoints work.
- Worker logs selected device.
- Only `cv-worker` requests GPU in GPU configuration.
- README startup instructions are accurate.

### Commit

`chore(runtime): finalize Docker Compose startup and first-launch docs`
