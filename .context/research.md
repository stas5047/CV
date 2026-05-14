# Research - Phase 17 Image Processing Pipeline

## Current phase

Confirmed current phase from `docs/phase.md`: **Phase 17 - Image processing pipeline**.

Phase direction: CV Worker / Image Processing.

Phase goal: implement end-to-end image job processing.

Risk level: not provided by user. Assumption: **HIGH**, because worker will write DB records, result files, exports, and final job status.

## Docs consulted

Required first reads:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`

Relevant docs from phase:

- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

Existing `.context` artifacts checked:

- `.context/status.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-claude.md`
- `.context/review-plan-resolution.md`

Confirmed fact: checked `.context` files above were empty at read time.

## Planning review resolution facts

Claude planning review items were resolved in `.context/review-plan-resolution.md`.

Accepted facts that affect implementation research:

- Phase 17 must not mark valid video jobs as failed only because video processing is later-phase work.
- Image-only queue behavior should prefer claiming/filtering image jobs only, leaving video jobs queued for the later video phase where practical.
- Completed image-job summaries must include sanitized original filename, source file size, and model size MB when available.
- Artifact creation failures for annotated output, CSV export, and JSON export are required worker error cases for this phase.

## Confirmed repository facts

- Git checkout exists.
- `git status --short` before this contract showed modified `.context/*` files and modified `docs/phase.md`.
- Repository has root `docker-compose.yml`, `docker-compose.gpu.yml`, `.env.example`, `Makefile`, `README.md`, `backend/`, `cv/`, `frontend/`, `training/`, `scripts/`, and `docs/`.
- `frontend/` is still placeholder-only for product UI.
- `training/` contains only `index.md`.
- `backend/` contains implemented FastAPI APIs, SQLAlchemy models, Alembic migration, result/download APIs, and tests.
- `cv/pyproject.toml` already includes `numpy`, `opencv-python-headless`, `pandas`, `torch`, `ultralytics`, SQLAlchemy, psycopg, Pydantic, pytest, and Ruff.
- `cv/index.md` states worker currently has settings, logging, device selection, DB connectivity, storage path safety, startup checks, PostgreSQL queue claiming, heartbeat/progress helpers, stale recovery, polling, model metadata resolution, safe model weights path handling, lazy Ultralytics loading, model caching, and placeholder failure after model preflight.
- `cv/aerovision_worker/main.py` currently claims jobs, loads model metadata/runtime, then fails claimed jobs with `PLACEHOLDER_PROCESSING_ERROR`.
- `cv/aerovision_worker/queue.py` provides `claim_next_job`, `update_job_heartbeat`, `recover_stale_jobs`, and `fail_processing_job`.
- `cv/aerovision_worker/model_runtime.py` resolves model priority: job model, active DB model, then `ACTIVE_MODEL_ID`; resolves safe weights path; loads and caches Ultralytics model.
- `cv/aerovision_worker/storage_paths.py` validates relative paths and joins under configured storage roots.
- `backend/app/db/models.py` has required tables/fields for `processing_jobs`, `detections`, `tracks`, and path checks.

## Existing implementation state

Confirmed implemented for this phase dependency chain:

- Queue claim exists and uses PostgreSQL `FOR UPDATE SKIP LOCKED` when dialect is PostgreSQL.
- Claim transaction is short; processing happens after claim.
- Worker has heartbeat update helper with progress bounds.
- Worker can fail owned processing jobs with safe error message.
- Worker can recover stale processing jobs.
- Worker can select/load/cache model by documented priority.
- Worker can reject unsafe and missing model weights paths without logging absolute paths.
- Backend result APIs already consume `summary_json`, `result_media_path`, `csv_path`, `json_path`, `detections`, and `tracks`.

Confirmed not implemented yet:

- Image decode/read in worker.
- YOLO inference execution for image jobs.
- Detection normalization into DB `detections` rows.
- Annotated image output generation.
- CSV export generation.
- JSON export generation.
- Completed image job status update with result/export paths and summary.
- No-detection image completion.
- Corrupted/missing/unreadable image handling inside worker image pipeline.
- Worker tests specific to image processing outputs.

## Unknowns and assumptions

Confirmed unknowns:

- Installed Ultralytics result object details must be handled behind a small adapter or mocked in tests.
- Exact annotated-image drawing method is not specified beyond producing annotated image when possible.
- Exact output image extension is not specified. Assumption: preserve uploaded image extension when safe, or write `.jpg`/`.png` consistently under `results/{job_id}/` if implementation documents only relative DB path.
- Exact JSON export internal field detail is not exhaustively specified beyond required top-level keys and CV-only boundary.
- Exact summary key names are not fully fixed by docs. Assumption: use documented metric names converted to stable snake_case keys already expected by backend tests where present.
- Phase 17 is image-only. Video tracking, track summaries, and video progress cadence are later-phase work.

Assumptions for implementation:

- Worker may use existing SQLAlchemy raw SQL style from `queue.py` and `model_runtime.py`.
- Image jobs are identified by joined `media_files.media_type = 'image'`; non-image jobs should not be processed by Phase 17 image path.
- DB writes for detections, result paths, exports, summary, and final status should happen in short transactions after media/model processing, not while running inference.
- Tests should use mocked model output and small in-memory image fixtures, not real YOLO weights.
- No-detection jobs still create annotated output if decode succeeds, headers-only CSV, JSON with empty `detections`, `status = completed`, `progress_percent = 100`, and null confidence summary values.

## Files likely relevant for implementation

Existing files:

- `cv/aerovision_worker/main.py`
- `cv/aerovision_worker/queue.py`
- `cv/aerovision_worker/model_runtime.py`
- `cv/aerovision_worker/storage_paths.py`
- `cv/aerovision_worker/settings.py`
- `cv/pyproject.toml`
- `cv/tests/test_startup.py`
- `cv/tests/test_model_runtime.py`
- `cv/tests/test_queue.py`
- `cv/tests/test_storage_paths.py`
- `backend/app/db/models.py`
- `backend/app/services/results.py`
- `backend/tests/test_jobs_api.py`

Potential new worker/test files may be justified for decomposition, but exact new file names are not dictated by docs and should be chosen only during implementation.
