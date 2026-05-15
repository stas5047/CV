# Phase 33 Plan

## Scope

Phase only: `Phase 33 - Final full-stack QA, security audit, and release readiness`.

Do not add product behavior. Do not add new endpoints, schema fields, runtime services, queues, UI flows, or CV outputs. Fix only confirmed doc-backed defects found by this phase; otherwise document blockers.

## Ordered Atomic Steps

1. `@role/tester` - Capture baseline repo state.
   - Verify: run `git status --short`.
   - Output: list pre-existing modified files before any QA or fix work.

2. `@role/tester` - Verify storage and Git ignore policy.
   - Verify: inspect `.gitignore`, `storage/`, and `git status --short`.
   - PASS when generated storage contents are ignored and not staged/tracked.

3. `@role/developer-devops` - Validate safe environment example.
   - Verify: inspect `.env.example`.
   - PASS when values are placeholders and required documented env groups exist.

4. `@role/developer-devops` - Validate base Compose config.
   - Verify: run `docker compose --env-file .env.example config`.
   - PASS when config renders with `postgres`, `backend`, `cv-worker`, `frontend`.

5. `@role/developer-devops` - Validate GPU Compose config.
   - Verify: run `docker compose -f docker-compose.yml -f docker-compose.gpu.yml --env-file .env.example config`.
   - PASS when GPU access is isolated to `cv-worker`.

6. `@role/developer-devops` - Verify storage bootstrap.
   - Verify: run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-storage.ps1`.
   - PASS when required storage folders exist and remain ignored.

7. `@role/tester` - Run dependency/setup preflight.
   - Verify: confirm Python tooling for `backend/`, `cv/`, and `training/`; confirm frontend dependencies for `frontend/`; confirm Docker daemon and Compose availability.
   - PASS when required toolchains/dependencies are available, or report exact `not available yet` / blocker before running dependent gates.

8. `@role/tester` - Run backend lint.
   - Verify: from `backend/`, run `python -m ruff check .`.
   - PASS when lint exits 0.

9. `@role/tester` - Run backend tests.
   - Verify: from `backend/`, run `python -m pytest`.
   - PASS when backend test suite exits 0.

10. `@role/tester` - Run CV worker lint.
   - Verify: from `cv/`, run `python -m ruff check .`.
   - PASS when lint exits 0.

11. `@role/tester` - Run CV worker tests.
    - Verify: from `cv/`, run `python -m pytest`.
    - PASS when worker test suite exits 0.

12. `@role/tester` - Run frontend lint.
    - Verify: from `frontend/`, run `npm run lint`.
    - PASS when lint exits 0.

13. `@role/tester` - Run frontend tests.
    - Verify: from `frontend/`, run `npm test`.
    - PASS when Vitest exits 0.

14. `@role/tester` - Run frontend build.
    - Verify: from `frontend/`, run `npm run build`.
    - PASS when TypeScript/Vite build exits 0.

15. `@role/tester` - Run training utility tests.
    - Verify: from repo root, run `python -m pytest training/tests`.
    - PASS when tests exit 0.

16. `@role/developer-training` - Validate placeholder artifacts.
    - Verify: run `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json`.
    - PASS when artifact schema validation exits 0.

17. `@role/developer-devops` - Build base Docker runtime.
    - Verify: run `docker compose --env-file .env.example build`.
    - PASS when all base service images build.

18. `@role/developer-devops` - Start clean-volume CPU runtime smoke.
    - Verify: require configured local `.env` without reading or logging secret values; run detached startup with an isolated project name, for example `docker compose --project-name aerovision_phase33 --env-file .env up --build -d`.
    - PASS when `postgres`, `backend`, `cv-worker`, and `frontend` become healthy/reachable from a fresh isolated PostgreSQL volume. If `.env` is absent, Docker is unavailable, ports conflict, model artifacts are missing, or startup fails, record exact blocker.

19. `@role/developer-backend` - Verify backend health endpoints.
    - Verify: request `GET http://localhost:8000/api/health` and `GET http://localhost:8000/api/health/db`.
    - PASS when responses are successful and reveal no secrets.

20. `@role/developer-db` - Verify migrations and seed/setup in runtime.
    - Verify: inspect backend startup logs or run isolated-project container commands for `alembic upgrade head` and `python -m app.setup` using `.env` without printing secret values.
    - PASS when migrations apply and seed is idempotent with one configured admin.

21. `@role/developer-cv-worker` - Verify worker startup and queue readiness.
    - Verify: inspect worker logs for selected device and successful startup; run `python -m aerovision_worker.main --check-once` if needed.
    - PASS when worker can connect to DB/storage and logs selected device without secrets.

22. `@role/developer-auth-security` - Verify auth and registration toggle.
    - Verify: exercise registration enabled/disabled, login, `/api/auth/me`, missing/invalid token, inactive user behavior where tests or runtime setup allow.
    - PASS when behavior matches `AUTH_SECURITY.md` and `API.md`.

23. `@role/developer-auth-security` - Verify upload validation and path safety.
    - Verify: test accepted image/video types plus rejection of unsupported extension, invalid MIME type, oversized image, oversized video, unsafe filename, path traversal, and user-submitted storage-path attempts.
    - PASS when backend rejects unsafe uploads before storage/job creation and stores only generated relative paths.

24. `@role/developer-auth-security` - Verify ownership/admin/download security.
    - Verify: test regular user own-only media/jobs/results/downloads, admin global access, regular-user admin denial, and path traversal rejection on download routes.
    - PASS when backend enforces all access server-side.

25. `@role/developer-backend` - Verify API/export contracts.
    - Verify: inspect API contract tests and runtime downloads for CSV/JSON shape when jobs complete.
    - PASS when CSV and JSON include documented fields and no forbidden external output fields.

26. `@role/developer-cv-worker` - Verify model-selection and worker queue behavior.
    - Verify: run existing queue/model-selection tests and, if runtime artifacts exist, process jobs through PostgreSQL queue.
    - PASS when priority is job-specific model, active DB model, then `ACTIVE_MODEL_ID` fallback only.

27. `@role/developer-cv-worker` - Verify image, video, and no-detection E2E.
    - Verify: run manual or test-backed jobs for image, video, and no-detection cases when model/media artifacts exist.
    - PASS when jobs complete, progress updates, detections/tracks/summaries/exports/result media are correct; if artifacts missing, record blocker exactly.

28. `@role/developer-frontend` - Verify frontend route and role behavior.
    - Verify: browser/manual smoke for `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, `/admin`.
    - PASS when guest/user/admin visibility and route guards match docs.

29. `@role/developer-frontend` - Verify frontend download flow.
    - Verify: from `/jobs/:jobId`, click or otherwise exercise annotated media, CSV, and JSON download controls for a completed job when artifacts exist.
    - PASS when UI download controls reach the documented backend download endpoints with auth intact and downloads succeed; if completed artifacts are unavailable, record exact blocker.

30. `@role/developer-frontend` - Verify Ukrainian UX and frontend safety.
    - Verify: scan rendered UI and source for visible non-Ukrainian user text, raw `null`, absolute paths, visible `frame_stride`, and out-of-scope wording.
    - PASS when Ukrainian/state/safety rules hold.

31. `@role/developer-frontend` - Verify experiments UI.
    - Verify: inspect `/experiments` with data and missing-data states.
    - PASS when Recharts render with data and missing sections show exact documented empty-state text without raw `null`.

32. `@role/developer-training` - Verify training boundary.
    - Verify: inspect frontend/backend/training helpers for no API/UI-launched training.
    - PASS when only offline scripts/notebooks/helpers exist and large artifacts stay ignored.

33. `@role/developer-auth-security` - Verify logs and privacy.
    - Verify: inspect backend/worker/container logs from smoke run.
    - PASS when no passwords, password hashes, JWTs, JWT secrets, DB passwords, or sensitive env values appear.

34. `@role/developer-devops` - Shut down isolated runtime smoke.
    - Verify: run isolated-project shutdown such as `docker compose --project-name aerovision_phase33 --env-file .env down -v --remove-orphans` only for the Phase 33 project after evidence/logs are captured.
    - PASS when only the isolated Phase 33 Compose resources are stopped/removed; do not remove default project volumes or user data.

35. `@role/code-reviewer` - Run scope and CV-only boundary audit.
    - Verify: search source/API/UI/export code for forbidden behavior: interception, autopilot, navigation commands, motor/flight/hardware control, aiming, payload, geospatial targeting, autonomous engagement, RTSP/webcam/live-camera processing, Celery, Redis, Flask, Streamlit.
    - PASS when absent or present only as docs/prohibited text.

36. `@role/tester` - Triage failures.
    - Verify: for each failure, classify as `accepted`, `rejected`, `duplicate`, or `needs user decision`.
    - PASS when each issue has exact command/evidence and doc reference.

37. `@role/developer-backend` / `@role/developer-cv-worker` / `@role/developer-frontend` / `@role/developer-devops` - Apply only accepted doc-backed fixes.
    - Verify: each fix cites relevant doc and has targeted regression check.
    - PASS when no ambiguous behavior is implemented without user decision.

38. `@role/docs-maintainer` - Update README or known limitations only if QA changes commands, setup behavior, artifact layout, or exposes confirmed release blockers.
    - Verify: docs updates are narrow and consistent with product docs.
    - PASS when README remains truthful and no product spec is duplicated.

39. `@role/tester` - Re-run relevant failed gates after fixes.
    - Verify: run only gates affected by accepted fixes plus any release-critical smoke.
    - PASS when fixed checks pass or remaining blockers are documented.

40. `@role/code-reviewer` - Final changed-file review.
    - Verify: inspect `git diff --check`, `git diff --stat`, and changed files.
    - PASS when no debug artifacts, generated storage, secrets, broad refactors, or scope creep exist.

41. `@role/tester` - Write final QA evidence.
    - Verify: update `.context/status.md` with commands, `PASS`/`FAIL`/`not available`, blockers, and security/privacy result.
    - PASS when evidence is complete and exact.

42. `@role/tester` - Final verdict.
    - Verify: compare results against `docs/TESTING_QA.md` acceptance criteria and `docs/ROADMAP.md` Phase 33 validation.
    - PASS when release-ready verdict is evidence-backed; otherwise verdict lists blockers.

## Relevant Checks Only

- Backend: `python -m ruff check .`, `python -m pytest`, health/db health, migrations/seed, API contract/security tests.
- CV worker: `python -m ruff check .`, `python -m pytest`, startup smoke, queue/model/image/video/no-detection checks.
- Frontend: `npm run lint`, `npm test`, `npm run build`, manual route/UX smoke.
- Training: `python -m pytest training/tests`, artifact validation command.
- Runtime: Compose config/build with `.env.example`; clean-volume CPU runtime smoke with configured `.env`, isolated Compose project name, health/log checks, storage bootstrap, controlled isolated shutdown; GPU config isolation only unless host GPU available.

## Stop Conditions

- Stop before source changes if docs conflict.
- Stop before source changes if fix needs new product behavior.
- Stop and request user decision if Docker/ports/credentials require destructive cleanup or unsafe secret handling.
- Record exact blocker if `.env`, real model artifacts, media fixtures, Docker, or ports block required E2E without needing a product decision.
