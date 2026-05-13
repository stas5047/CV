# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 6 plan matches current phase scope: backend/security primitives only, no product API, no frontend, no CV worker, no schema migration. Consulted docs support planned admin dependency, ownership helper, path safety helpers, filename/download-name helpers, CORS review, logging/error safety review, and targeted backend gates.

Plan needs small tightening before implementation: ownership helper must cover indirect ownership through media/job records, CORS and error-response checks need explicit test or existing-test verification, and validation commands must run any new security test files.

## Blocking issues

None.

## Important issues

1. Indirect ownership path not explicit enough.
   - Evidence: `docs/AUTH_SECURITY.md` says regular users may access resource when resource belongs to user or belongs to job/media record owned by user. Same section lists detections, tracks, summaries, and downloads under mandatory ownership checks. `docs/API.md` results endpoints require user access limited to own jobs.
   - Plan evidence: `.context/plan.md` steps 6-7 test and implement owner-id based helper, with owner/admin/other/missing cases. It says generic enough for later media/job/result/download services, but no test or contract covers resources owned indirectly through `media_file` or `processing_job`.
   - Risk: later detections/tracks/download checks may use direct `owner_id` logic where no direct owner field exists, causing weak or duplicated ownership enforcement.
   - Needed change: add helper/test coverage for ownership via resource owner id, job owner/media owner lookup, or a documented predicate-based helper used by later services.

2. CORS validation has review step but weak explicit test step.
   - Evidence: Phase 6 scope in `docs/phase.md` includes CORS validation using explicit configured origins. `docs/AUTH_SECURITY.md` requires configured origins and forbids wildcard in non-local configs. `docs/TESTING_QA.md` security tests include explicit CORS verification.
   - Plan evidence: `.context/plan.md` step 14 reviews CORS behavior; step 13 mentions `tests/test_settings.py`, but no step says add or verify CORS tests if current coverage is absent.
   - Risk: implementation can pass plan while CORS remains under-tested.
   - Needed change: add explicit "verify existing CORS tests or add tests for explicit origins, empty origins, wildcard rejection" step.

3. Secure error response pattern not verified.
   - Evidence: `docs/AUTH_SECURITY.md` says API responses must not expose stack traces. `docs/API.md` says errors must be clear and never expose secrets or unsafe absolute paths.
   - Plan evidence: `.context/plan.md` step 15 reviews logging/error safety and preserves current API style, but no test or concrete check verifies stack traces stay out of responses in configured runtime.
   - Risk: new dependencies/helpers can be safe, but app-level error exposure remains unverified.
   - Needed change: add narrow test or inspection for safe HTTPException details and no traceback/internal path exposure in error responses relevant to new helpers.

4. Validation commands may miss new tests depending on file placement.
   - Evidence: `.context/plan.md` adds new admin, ownership, path, and filename tests, but targeted commands name only `tests/test_auth.py`, `tests/test_settings.py`, and `tests/test_logging.py`.
   - Risk: if implementation puts path/security tests in new files such as `tests/test_path_safety.py`, targeted phase commands may skip them until optional full suite.
   - Needed change: validation must include exact new test file paths, or always run `cd backend; python -m pytest -q` after adding shared security helpers.

## Optional improvements

1. State ownership denial policy once.
   - Evidence: `.context/design.md` notes 403 vs 404 ambiguity. Plan says avoid leaking cross-owner existence.
   - Improvement: implementation plan can choose 404 for missing/cross-owner user resources or centralize this in helper docstring/test names. Admin-only role failures can stay 403.

2. Include Windows reserved filename cases in filename tests.
   - Evidence: path safety plan already includes Windows drive and UNC path rejection.
   - Improvement: add `CON`, `NUL`, trailing dots/spaces if helper runs on Windows developer machines and produces download names.

## Questions for resolution

1. Should ownership helper return 404 for cross-owner user resources to avoid existence leaks, while admin-role failures return 403?
2. Should Phase 6 add one central error handler now, or only prove current FastAPI/error configuration does not expose stack traces for new helper errors?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
