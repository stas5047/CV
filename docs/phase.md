## Phase 1 - Repository scaffold, environment, and Docker baseline

**Direction:** DevOps / Repository setup  
**Goal:** Create the project skeleton and a minimal Compose runtime without product business logic.

### Scope

- Create or normalize root structure: `backend/`, `frontend/`, `cv/`, `training/`, `scripts/`, `storage/`, `docs/` if not already present.
  - Add `.gitignore` rules for `.env`, uploads, results, datasets, model weights, generated reports, temp files, Python caches, Node artifacts, and build outputs.
  - Add `.env.example` with safe placeholders for database, auth, storage, backend, worker, and CV variables.
  - Add initial `docker-compose.yml` with `postgres`, `backend`, `cv-worker`, and `frontend` services as buildable placeholders.
  - Add optional `docker-compose.gpu.yml` or GPU profile placeholder for `cv-worker` only.
  - Ensure backend and worker both mount shared storage at `/app/storage`.
  - Add storage-directory bootstrap script or Makefile target.
  - Add README section for initial setup and expected one-command local/demo launch.
  - Avoid implementing frontend UI or backend product routes beyond placeholders.

### Relevant docs

- `docs/PROJECT_CONTEXT.md`
  - `docs/ARCHITECTURE.md`
  - `docs/AUTH_SECURITY.md`
  - `docs/TESTING_QA.md`

### Validation

- `docker compose config` succeeds.
  - `.env.example` contains no real secrets.
  - Storage directories can be created locally.
  - Git status does not include generated storage contents.
  - README documents the current state honestly.

### Commit

`chore(scaffold): add repository layout environment and compose baseline`