# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 16 plan matches documented scope: worker-side model selection, relative weights path handling, model loading/cache, `CV_DEVICE` behavior, safe model-load failure, and no backend/frontend/schema/training work unless verified drift appears.

Plan keeps architecture boundaries intact: worker uses PostgreSQL and shared storage, does not add HTTP worker API coupling, does not launch training, does not add inference/tracking/export scope, and preserves YOLO26 primary / YOLO11 documented fallback metadata.

Changes needed are validation-safety and evidence gaps, not product redesign.

## Blocking issues

None.

## Important issues

1. Environment-dependent `--check-once` gate can mutate real queued jobs.
   - Evidence: `.context/plan.md` step 8 says successful model preflight keeps later-phase placeholder failure: `Processing not implemented in this phase`.
   - Evidence: `.context/plan.md` step 12 runs `python -m aerovision_worker.main --check-once` when env/database are configured.
   - Evidence: `docs/ARCHITECTURE.md` says worker claims oldest queued job and marks it processing, then completed/failed after processing.
   - Risk: running optional smoke against non-isolated configured DB can claim a real queued job and fail it after successful model load, even though phase does not implement processing.
   - Required change: constrain this gate to isolated test data / empty queue / disposable DB, or document exact expected mutation before running. If safe preconditions are absent, report `not available yet`.

2. Plan does not require evidence for real Ultralytics model load when weights exist.
   - Evidence: `docs/phase.md` validation requires worker loads configured model from relative path when weights exist.
   - Evidence: `.context/plan.md` targeted tests can pass with mocked `YOLO`; real artifact smoke is only optional in `.context/design.md`, not in ordered plan.
   - Risk: path/file existence and cache logic may pass unit tests while actual `ultralytics.YOLO(weights)` fails in environment or with documented artifact layout.
   - Required change: add environment-dependent smoke when a documented local `.pt` artifact exists; otherwise report `not available yet` with missing artifact reason.

## Optional improvements

- Add explicit assertion that model-load logs and stored job errors omit `STORAGE_ROOT`, `MODELS_ROOT`, database URL, and env-derived secret values. Plan has log-safety review, but direct tests reduce privacy drift.
- Add test naming that separates documented `models/...` paths under `STORAGE_ROOT` from bare compatibility paths under `MODELS_ROOT`, so future edits do not reintroduce `models/models/...`.

## Questions for resolution

- Prompt risk value was literal `<MEDIUM | HIGH>`, not selected. Review treats phase as MEDIUM because scope touches external model artifacts, DB-backed queue state, and device/runtime failure behavior.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
- `git status --short`
