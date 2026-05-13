# Phase Contract Research

## Current Phase

- Phase: `Phase 1 - Repository scaffold, environment, and Docker baseline`.
- Direction: DevOps / Repository setup.
- Goal: Create project skeleton and minimal Compose runtime without product business logic.
- Risk: not supplied in prompt; assumed `MEDIUM` for planning because phase touches Docker, env placeholders, storage layout, and secret-handling defaults.

## Docs Consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/status.md`
- existing `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/review-plan-claude.md`, `.context/review-plan-resolution.md`

## Confirmed Repository Facts

- Git checkout exists.
- `git status --short` shows:
  - `M docs/phase.md`
  - `?? .idea/`
- Existing top-level project files/folders:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `backend/`
  - `frontend/`
  - `cv/`
  - `training/`
  - `docs/`
  - `.context/`
  - `.venv/`
  - `.idea/`
- `backend/`, `frontend/`, `cv/`, and `training/` contain only `index.md` files.
- `docs/index.md` states no implementation scaffolds, dependency manifests, Dockerfiles, local scripts, or runnable commands exist yet.
- Root `README.md`, `.env.example`, `.gitignore`, `docker-compose.yml`, `docker-compose.gpu.yml`, `Makefile`, `scripts/`, and `storage/` are not present in `rg --files` output.
- Existing `.context/status.md`, `.context/research.md`, `.context/design.md`, `.context/plan.md`, `.context/review-plan-claude.md`, and `.context/review-plan-resolution.md` were empty at read time.

## Existing Implementation State

- Documentation set exists.
- Component folders exist as documented placeholders.
- No backend FastAPI app exists yet.
- No frontend Vite app exists yet.
- No CV worker scaffold exists yet.
- No training utilities exist yet.
- No Docker Compose runtime exists yet.
- No env example exists yet.
- No storage bootstrap helper exists yet.
- No README setup flow exists yet.

## Unknowns And Assumptions

- Prompt placeholder did not provide explicit phase number/title or risk. Assumption: `docs/phase.md` is source for current phase.
- Assumption: Phase 1 may create `scripts/` and `storage/` because `docs/ROADMAP.md` and `docs/ARCHITECTURE.md` list them for this phase/layout.
- Assumption: service Dockerfiles may be minimal placeholders only; no product routes, UI, database schema, or worker logic should be added.
- Unknown: exact preferred helper style for storage bootstrap, because docs allow setup script or Makefile target.
- Unknown: exact placeholder backend/frontend/worker commands, because no scaffolds exist yet.
- No doc conflict found.

## Files Likely Relevant For Implementation

- `.gitignore`
- `.env.example`
- `docker-compose.yml`
- `docker-compose.gpu.yml`
- `Makefile`
- `README.md`
- `scripts/`
- `storage/`
- `backend/index.md`
- `frontend/index.md`
- `cv/index.md`
- `training/index.md`
- possible minimal service placeholder files under:
  - `backend/`
  - `frontend/`
  - `cv/`
