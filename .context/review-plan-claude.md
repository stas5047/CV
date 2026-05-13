# Independent Planning Review - Phase 13 Backend Contract Audit

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 13 direction and stays inside backend/QA scope. It covers route audit, `/api` prefix, OpenAPI, pagination, auth/ownership, response safety, CV-only boundary, backend lint, and backend tests.

Two important gaps should be fixed before implementation: README/API notes update is too conditional despite known stale README state, and error-shape normalization needs clearer acceptance criteria than only safe `detail` strings.

## Blocking issues

None.

## Important issues

1. README/API notes update may be skipped even though current README is already stale.

Evidence: `docs/phase.md` Phase 13 scope says "Update README/API notes with current commands and endpoint groups." `.context/research.md` says `README.md` current-state wording appears older than backend implementation state. `README.md` still says auth, uploads, jobs, downloads, and admin APIs are "Not available yet", while `backend/index.md` says these endpoint groups exist through Phase 12.

Risk: Implementation could pass backend tests but leave onboarding/API notes false for frontend/worker follow-on phases.

Required plan change: make README/backend API notes audit/update a required Phase 13 step, not only "if commands, endpoint groups, or current implementation state changed during Phase 13."

2. Error response normalization is under-specified for Phase 13 scope.

Evidence: `docs/phase.md` scope requires "Normalize error response shapes for frontend Ukrainian localization." `docs/API.md` requires clear predictable errors suitable for frontend Ukrainian localization and safe errors for unauthorized, forbidden, missing resource, upload, parameter, model, failed job, missing result, and DB connectivity cases. Plan step 7 checks representative `400/401/403/404/422` responses for safe `detail` content, but does not define what "normalized shape" means or require a fix if FastAPI/Pydantic default shapes differ.

Risk: Frontend may still face inconsistent error payload shapes after Phase 13, especially HTTPException `{"detail": "..."}` versus validation `{"detail": [...]}`.

Required plan change: add explicit acceptance criteria for normalized implemented error responses, or state a documented minimal standard such as FastAPI default `detail` accepted for this MVP plus tested frontend-consumable handling for string/list details. Apply small fixes only where current behavior violates that standard.

## Optional improvements

1. Add OpenAPI assertions for documented concrete download paths.

Evidence: `docs/API.md` documents `/api/jobs/{job_id}/download/media`, `/csv`, and `/json`; `.context/research.md` says current implementation likely exposes dynamic `/api/jobs/{job_id}/download/{kind}` in OpenAPI. Plan step 3 covers this, but explicit OpenAPI path assertions would prevent future drift.

2. Include one response scan fixture that checks JSON responses for absolute path prefixes and forbidden CV-boundary field names.

Evidence: `docs/API.md`, `docs/AUTH_SECURITY.md`, and `docs/PROJECT_CONTEXT.md` all ban unsafe absolute paths and targeting/navigation/control outputs. Plan step 9 covers this generally; fixture-based scanning would make it cheaper to reuse.

## Questions for resolution

1. Should Phase 13 keep FastAPI/Pydantic default error payload forms if tests prove frontend can consume both string and list `detail`, or should implementation introduce a small shared error envelope now?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `docs/PROJECT_CONTEXT.md`
- `backend/pyproject.toml`
- `backend/index.md`
- `README.md`
