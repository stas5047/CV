# Independent Planning Review - Phase 33

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 33 direction and keeps work as QA/release audit, not product redesign. Main structure covers backend, worker, frontend, Docker, training artifacts, security, CV-only boundary, and failure triage.

Changes needed before implementation: runtime smoke must use documented first-launch setup, clean-volume requirement must be explicit and safe, upload-validation checks need full coverage, and UI download smoke must be called out.

## Blocking issues

None.

## Important issues

1. Runtime smoke uses `.env.example` where docs require configured `.env`.
   - Evidence: `.context/plan.md` steps 17, 19, and related runtime steps use `docker compose --env-file .env.example up --build`.
   - Doc reference: `README.md` says copy `.env.example` to `.env`, replace placeholders, then start with `docker compose --env-file .env up --build`. `docs/ARCHITECTURE.md` says initial setup includes creating `.env` from `.env.example`.
   - Risk: QA can pass against placeholder/demo config and miss real first-launch/env behavior. Also risks seeding placeholder admin credentials during release smoke.
   - Required change: use `.env` for runtime launch/seed/admin smoke while avoiding reading or logging real secrets. Keep `.env.example` for config/build validation only.

2. Clean-volume Docker startup smoke is missing.
   - Evidence: `docs/phase.md` scope requires "Run clean-volume Docker startup smoke"; `.context/plan.md` step 17 starts Compose but does not specify clean volumes or isolated project/volume handling.
   - Doc reference: `docs/ROADMAP.md` Phase 33 scope and `docs/TESTING_QA.md` Docker launch tests require full-stack launch and setup from initial state.
   - Risk: existing DB/storage state can mask migration, seed, storage bootstrap, and first-launch defects.
   - Required change: add safe clean-volume smoke approach, preferably isolated Compose project name/storage temp path or explicit user-safe cleanup strategy. Do not destructively remove existing user volumes without approval.

3. Upload-validation QA is incomplete.
   - Evidence: `.context/plan.md` step 22 mentions path traversal rejection, but no step covers unsupported extension, invalid MIME, oversized image/video, unsafe filename, or user-submitted storage-path attempts.
   - Doc reference: `docs/TESTING_QA.md` Upload Validation Tests and `docs/AUTH_SECURITY.md` Upload Validation require extension, MIME, file size, category, filename safety, and path traversal checks.
   - Risk: Phase 33 could miss a high-value security boundary around untrusted files.
   - Required change: add targeted backend/API upload-validation checks or confirm existing tests cover every documented rejection case.

4. UI download flow is not explicitly verified.
   - Evidence: `.context/plan.md` step 23 checks API/export contracts and downloads, while step 26 checks routes/guards. No step explicitly clicks UI download buttons for annotated media, CSV, and JSON after completed jobs.
   - Doc reference: `docs/TESTING_QA.md` acceptance says downloads work from UI; manual E2E scenarios require CSV/JSON downloads. `docs/FRONTEND_UX.md` requires job detail download buttons.
   - Risk: backend downloads can pass while frontend wiring, auth headers, URLs, or button states are broken.
   - Required change: include frontend/manual browser download smoke for annotated media, CSV, and JSON when completed job artifacts exist; otherwise record exact blocker.

## Optional improvements

1. Add dependency/setup preflight before local component gates.
   - Evidence: `.context/plan.md` runs `python -m ruff`, `python -m pytest`, `npm test`, and training module commands but does not state dependency installation or "not available" handling.
   - Doc reference: component indexes and `README.md` list install commands before local gates.
   - Value: avoids confusing missing-dependency failures with product failures.

2. Make Compose smoke lifecycle explicit.
   - Evidence: `.context/plan.md` step 17 uses foreground `docker compose ... up --build`.
   - Value: detached start, health/log checks, then controlled shutdown gives clearer evidence and avoids leaving services running after review.

## Questions for resolution

1. Should Phase 33 use an existing local `.env`, or should implementation create a temporary QA env file from `.env.example` with safe non-placeholder values?

2. Are real YOLO model weights and tiny image/video/no-detection fixtures available for manual E2E, or should missing artifacts be recorded as release blockers?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/FRONTEND_UX.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `README.md`
- `backend/index.md`
- `cv/index.md`
- `frontend/index.md`
- `training/index.md`
- `prototype/index.md`
- `git status --short`
