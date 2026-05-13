# Phase 1 Implementation Plan

1. `@role/developer-devops` Inspect current root files and confirm missing scaffold files before edits.
   - Verify with `rg --files` and `git status --short`.

2. `@role/developer-devops` Add or update `.gitignore` for Phase 1 generated and sensitive files.
   - Include `.env`, storage generated contents, model weights, reports/results/uploads/datasets/temp files, Python caches, Node artifacts, and build outputs.
   - Verify generated storage contents stay untracked.

3. `@role/developer-devops` Add `.env.example` with safe placeholders for documented variable groups.
   - Cover database, auth, storage, backend, worker, and CV variables from `docs/ARCHITECTURE.md`.
   - Verify no real secrets or local private credentials appear.

4. `@role/developer-devops` Add minimal root Compose baseline.
   - Define `postgres`, `backend`, `cv-worker`, and `frontend`.
   - Use buildable placeholders for `backend`, `cv-worker`, and `frontend` when those services use `build:`.
   - Ensure placeholder Dockerfiles/commands can start minimal no-op containers with `docker compose up --build`.
   - Mount same shared storage host path into backend and cv-worker at `/app/storage`.
   - Keep service behavior placeholder-only where app scaffolds do not exist.
   - Avoid Celery, Redis, Flask, Streamlit, RTSP, live-camera, or extra runtime services.
   - Verify with `docker compose --env-file .env.example config`, or with a documented copied `.env` file.

5. `@role/developer-devops` Add optional GPU override for `cv-worker` only.
   - Use `docker-compose.gpu.yml` or documented GPU-only override.
   - Validate combined Compose config with `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config` when the override exists.
   - Verify frontend, backend, and postgres do not request GPU.

6. `@role/developer-devops` Add storage bootstrap helper and/or `Makefile` target.
   - Create only required empty folders: `uploads`, `results`, `reports`, `models`, `temp`, `datasets`.
   - Verify helper runs locally and folders exist.

7. `@role/developer-devops` Add minimal placeholder service build files for buildable services.
   - Add build/start placeholders for backend, cv-worker, and frontend when Compose builds those services.
   - Keep backend/frontend/cv placeholders free of product routes, UI, database schema, worker queue, and training logic.
   - Verify placeholders do not claim implemented features.

8. `@role/docs-maintainer` Add README initial setup section.
   - Document `.env` creation from `.env.example`, storage bootstrap, Docker Compose config/start expectations, CPU default, optional GPU note, and current scaffold limitations.
   - Keep README honest that product APIs/UI/CV are not implemented in Phase 1.

9. `@role/docs-maintainer` Update component index files only if new files or commands are added inside those folders.
   - Keep indexes narrow and current.
   - Do not modify product docs under `docs/`.

10. `@role/tester` Run Phase 1 gates.
    - `docker compose --env-file .env.example config` or documented copied `.env` config check -> expected `PASS`.
    - `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config` when GPU override exists -> expected `PASS`.
    - GPU config inspection: only `cv-worker` requests GPU -> expected `PASS`.
    - `.env.example` secret-placeholder inspection -> expected `PASS`.
    - storage bootstrap command -> expected `PASS`.
    - `git status --short` generated-storage check -> expected `PASS`.
    - backend/frontend/cv tests -> `not available yet` unless real commands were added.

11. `@role/code-reviewer` Review changed files against Phase 1 docs.
    - Check no product business logic was added.
    - Check service boundaries, shared storage mount, GPU isolation, ignore rules, env placeholder safety, and README honesty.
