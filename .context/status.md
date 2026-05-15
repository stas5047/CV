# Phase 32 Status

## Implemented

- Finalized `frontend/Dockerfile` to install dependencies, build the Vite app with `VITE_API_BASE_URL`, and serve it on port `5173`.
- Added `frontend/.dockerignore`.
- Added frontend `preview` script.
- Updated `docker-compose.yml` with frontend build args, frontend port publishing, backend healthcheck, frontend healthcheck, and health-based service ordering.
- Kept backend and CV worker shared storage mount at `/app/storage`.
- Kept `docker-compose.gpu.yml` GPU reservation and `CV_DEVICE=cuda` isolated to `cv-worker`.
- Expanded `Makefile` with setup, config, build, CPU/GPU up, down, logs, migrate, seed, aggregate test, and per-surface test targets.
- Updated `README.md`, `docs/index.md`, and `frontend/index.md` to match current runtime and implementation state.

## Final Fixes

- Added `libglib2.0-0`, `libgl1`, and `libxcb1` to `cv/Dockerfile` so OpenCV imports in the slim worker container.
- Kept the worker Python dependency layer before the OS-library layer so existing Docker cache can still avoid reinstalling heavy Python dependencies.
- Updated `cv/index.md` to reflect Dockerfile native runtime library responsibility.
- Removed trailing whitespace from `docs/phase.md`.
- Updated `.context/review-code-resolution.md` with accepted review item resolutions and final verification.

## Quality Gates

| Command | Result | Notes |
|---|---|---|
| `docker compose --env-file .env.example config` | PASS | Base config renders services `postgres`, `backend`, `cv-worker`, `frontend`. |
| `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config` | PASS | GPU reservation appears only under `cv-worker`. |
| `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1` | PASS | Required storage folders ready. |
| `npm run build` from `frontend/` | PASS | Vite build passed; non-failing chunk-size warning only. |
| `npm run lint` from `frontend/` | PASS | ESLint passed. |
| `npm test` from `frontend/` | PASS | 8 files, 51 tests passed. |
| `git diff --check` | PASS | No whitespace errors; Git emitted line-ending warnings only. |
| `docker compose --env-file .env.example build cv-worker` | PASS | Worker image built with OpenCV native runtime libraries. |
| `docker compose --env-file .env.example run --rm --no-deps cv-worker python -c "import cv2; print(cv2.__version__)"` | PASS | Printed `4.13.0`. |
| `docker compose --env-file .env.example up --build -d` | PASS | `postgres`, `backend`, `cv-worker`, and `frontend` started. |
| `docker compose --env-file .env.example ps -a` | PASS | `postgres`, `backend`, and `frontend` healthy; `cv-worker` stayed up. |
| Backend `/api/health` smoke | PASS | Returned `{"status":"ok","service":"backend"}`. |
| Backend `/api/health/db` smoke | PASS | Returned `{"status":"ok","database":"available"}`. |
| Seeded admin smoke | PASS | Login returned `token_present=true`, `token_type=bearer`; token not printed. |
| Frontend reachability smoke | PASS | `http://localhost:5173` returned HTTP 200. |
| Worker selected-device log smoke | PASS | Worker logged `device_selected requested_device=cpu selected_device=cpu`. |
| `docker compose --env-file .env.example down` | PASS | Runtime stack stopped and removed. |

## Security And Privacy

- `.env.example` uses placeholder secret values only.
- README instructs replacing placeholder secrets, not committing `.env`, and passing admin JWT through environment variable for artifact helper examples.
- Seeded-admin smoke checked token presence without printing the token.
- No real credentials, tokens, model weights, uploads, reports, or generated results were added.
- GPU access remains isolated to `cv-worker` in rendered GPU config.

## Deviations

- None from `.context/design.md` or `.context/plan.md` after final fix.

## Remaining Risks

- Real processing still depends on local model artifacts being placed and registered under documented `storage/models/` paths.
- GPU launch still depends on host NVIDIA container runtime; only GPU Compose config isolation was verified.
