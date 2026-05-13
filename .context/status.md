# Status - Phase 13 Backend Contract Audit

## Current Phase

- Phase: `Phase 13 - Backend contract, pagination, OpenAPI, and security test audit`.
- Mode: Implementation.
- Risk assumption: HIGH, from `.context/research.md`.

## Completed

- Read required agent files, phase docs, context contracts, planning resolution, mistake logs, and relevant product docs.
- Added `backend/tests/test_api_contract.py` for:
  - documented `/api` route coverage;
  - concrete documented download paths in OpenAPI;
  - paginated list schema shape;
  - safe FastAPI-compatible `detail` error payloads.
- Verified RED before implementation: `python -m pytest tests/test_api_contract.py` failed because concrete download routes were absent from OpenAPI.
- Replaced dynamic documented download exposure with concrete route functions:
  - `/api/jobs/{job_id}/download/media`;
  - `/api/jobs/{job_id}/download/csv`;
  - `/api/jobs/{job_id}/download/json`.
- Re-ran targeted contract/job tests after implementation.
- Updated `README.md` current backend state and API notes.
- Updated `backend/index.md` test summary for Phase 13 contract tests.
- Resolved OpenAI code review important item by adding representative successful API JSON response boundary scans for media, jobs/results, models, experiments, and admin endpoints.
- Updated `.context/review-code-resolution.md`.
- Logged the missed successful-response boundary scan in `docs/mistakes-codex.md`.

## Quality Gates Run

- `python -m pytest tests/test_api_contract.py` - RED observed before implementation.
- `python -m pytest tests/test_api_contract.py tests/test_jobs_api.py` - PASS after implementation.
- `python -m ruff check .` - PASS.
- `python -m pytest` - PASS, 168 passed.
- `python -m pytest tests/test_api_contract.py` - PASS after final fix, 4 passed.
- `python -m ruff check .` - PASS after final fix.
- `python -m pytest` - PASS after final fix, 169 passed.

## Security/Privacy

- Result downloads still require active JWT user and owner/admin access through existing `resolve_job_download` service path.
- Concrete download routes expose no internal storage paths in OpenAPI.
- Error contract tests scan representative `detail` payloads for stack traces, secrets, tokens, database passwords, absolute storage roots, and forbidden CV-boundary terms.
- Successful API contract tests now scan representative JSON responses for absolute storage roots, internal path fields, secrets, and forbidden CV-boundary terms.
- No training launch, frontend, worker polling, CV processing, new role, or out-of-scope safety behavior was added.

## Index/Docs

- Updated `README.md` backend current state and endpoint group notes.
- Updated `backend/index.md` Phase 13 test summary.
- Updated `docs/index.md` README description and current implementation state.
- No index update required after final fix: `backend/index.md` already describes Phase 13 API contract/OpenAPI/pagination/error-safety behavior, and no new files/folders were created.

## Deviations

- Final fix aligns with `.context/design.md`, `.context/plan.md`, and `.context/review-plan-resolution.md`; no deviations remain.

## Remaining Risks

- Phase 13 audit confirms backend contract shape only; worker-generated files and real CV exports still arrive in later phases.
