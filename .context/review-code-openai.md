# OpenAI Code Review - Phase 16

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 16 worker implementation matches documented scope: model metadata resolution, relative model weights path handling, lazy Ultralytics loading, selected-device application, model cache reuse, and worker poll model preflight. No backend API, DB schema, frontend, training, inference, tracking, export, or result-writing scope creep found.

One non-source defect remains in the reviewed change set: `.context/status.md` reports the `--check-once` gate as unavailable for a mutation reason that no longer matches worker code.

## Critical issues

None.

## Important issues

1. `.context/status.md` gives a false reason for skipping `python -m aerovision_worker.main --check-once`.
   - Evidence: `.context/status.md:33` says the gate is `not available yet` because no isolated DB/empty queue precondition exists and the Phase 16 placeholder can mutate claimed jobs.
   - Evidence: `cv/aerovision_worker/main.py:116` returns immediately when `check_once` is true, before poll loop starts at `cv/aerovision_worker/main.py:123`; it does not call `run_poll_iteration` or claim queued jobs.
   - Evidence: `cv/index.md:26` describes `--check-once` as startup smoke checks and exit.
   - Impact: quality-gate status is inaccurate. If the command is unavailable, the reason should be missing env/DB/model prerequisites, not queue mutation risk.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for review input. Shows only `.context/design.md`, `.context/plan.md`, `.context/research.md`, `.context/review-plan-claude.md`, `.context/review-plan-resolution.md`, and `.context/status.md` modified.
- `rtk git diff --stat`: PASS for review input. Current diff is `.context` only: 6 files, 273 insertions, 285 deletions.
- `rtk git diff`: PASS for review input. No source-code diff currently pending; Phase 16 source inspected from current tree.
- `rtk git diff --check`: PASS.
- `python -m pytest tests/test_device.py tests/test_storage_paths.py tests/test_model_runtime.py tests/test_startup.py` from `cv/`: PASS, 35 passed, 18 SQLite datetime adapter warnings.
- `python -m pytest` from `cv/`: PASS, 59 passed, 64 SQLite datetime adapter warnings.
- `python -m pytest -m postgres` from `cv/`: PASS, 3 passed, 56 deselected.
- `python -m ruff check .` from `cv/`: PASS, `All checks passed!`.
- Real Ultralytics model-load smoke: not available yet; `.context/status.md:32` says no `.pt` or `.onnx` artifact exists under `storage/models/`.

## Security/privacy assessment

- Model weight paths are validated as relative paths and resolved under storage roots before loading.
- Missing/unsafe weight errors use stable safe strings and do not expose absolute paths.
- Model loading logs include model id, family, variant, and device only.
- No DB URLs, tokens, passwords, JWT secrets, absolute paths, API responses, downloads, frontend displays, or exports were added by this phase.

## Positive findings

- Model selection priority matches `docs/CV_PIPELINE.md`: job model, then active DB model, then `ACTIVE_MODEL_ID` only when no active DB model exists.
- Documented `models/...` paths resolve under `STORAGE_ROOT`; bare paths under `MODELS_ROOT` remain compatibility behavior only.
- Cache key separates model id and selected device.
- YOLO family metadata is preserved; no silent YOLO11 substitution found.
- Worker loads model before current placeholder failure, keeping later inference/tracking/export work out of Phase 16.
- PostgreSQL queue tests cover `FOR UPDATE SKIP LOCKED` claim behavior.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/review-plan-claude.md`
- `.context/status.md`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/settings.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/device.py`
- `cv/aerovision_worker/queue.py`
- `cv/tests/test_model_runtime.py`
- `cv/tests/test_startup.py`
- `cv/tests/test_device.py`
- `cv/tests/test_storage_paths.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_queue_postgres.py`
- `cv/index.md`
- `backend/app/db/models.py`
- `backend/app/services/jobs.py`
- `backend/app/services/models.py`
