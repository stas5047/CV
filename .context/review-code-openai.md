# OpenAI Code Review - Phase 13 Backend Contract Audit

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 13 makes documented concrete result-download routes visible in OpenAPI, keeps download handling on existing owner/admin-checked service path, adds contract tests for paths/pagination/error `detail` shape, and updates README/backend/docs index state.

One important validation gap remains: planned API output boundary scan was not implemented for representative successful API JSON responses.

## Critical issues

None.

## Important issues

1. API output boundary audit does not cover implemented success responses.
   - Evidence: `docs/phase.md:15` requires confirming API outputs do not expose absolute filesystem paths or forbidden CV-boundary fields, and `docs/phase.md:32` makes API/export boundary audit part of validation for implemented responses.
   - Plan evidence: `.context/plan.md:19` requires a reusable helper/fixture scanning representative API JSON responses for forbidden CV-boundary fields and absolute filesystem paths. `.context/design.md:88` repeats representative implemented JSON response/download metadata coverage.
   - Implementation evidence: `backend/tests/test_api_contract.py:64-70` defines the safety helper, but it is only used in `backend/tests/test_api_contract.py:94-108` against three error responses: unauthorized `/api/auth/me`, validation `/api/auth/login`, and missing route `/api/does-not-exist`.
   - Impact: Phase 13 does not verify successful implemented responses from media/jobs/results/models/experiments/admin endpoints against the output-boundary requirement, despite status claiming no deviations in `.context/status.md:46-48`.
   - Required change: add representative authenticated/admin success-response scans, reusing the helper, for implemented JSON endpoints and result metadata/download references. Existing fixtures in `test_jobs_api.py`, `test_models_api.py`, `test_experiments_api.py`, `test_admin_api.py`, and media tests can likely supply data.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for inspection. Changed Phase 13 docs/context plus `README.md`, `backend/app/api/jobs.py`, `backend/index.md`, `docs/index.md`, `backend/tests/test_api_contract.py`.
- `rtk git diff --stat`: PASS for inspection. Route/test/doc-only Phase 13 diff observed.
- `rtk git diff`: PASS for inspection. Note: command output included forbidden `.context/review-code-resolution.md` diff content; not used for findings.
- `python -m ruff check .` from `backend/`: PASS, `All checks passed!`.
- `python -m pytest` from `backend/`: PASS, 168 passed.

## Security/privacy assessment

Download route change preserves existing security path: `backend/app/api/jobs.py:197-242` injects `get_current_active_user`, then `_download_result_by_kind` calls `resolve_job_download` with `current_user` and `storage_root` at `backend/app/api/jobs.py:180-194`.

No new roles, training launch, worker HTTP loop, frontend storage access, absolute path response, or CV-boundary output behavior found in changed source. Security test gap above remains for successful response boundary scanning.

## Positive findings

- Concrete documented routes `/api/jobs/{job_id}/download/media`, `/csv`, and `/json` replace OpenAPI exposure of dynamic `/download/{kind}` without changing service behavior.
- OpenAPI path test explicitly rejects the old dynamic download path.
- README and docs index now describe current backend implementation state instead of stale scaffold-only state.
- Full backend ruff and pytest gates pass locally.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `README.md`
- `backend/index.md`
- `backend/app/api/jobs.py`
- `backend/tests/test_api_contract.py`
