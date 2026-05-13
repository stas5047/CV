# Plan - Phase 13 Backend Contract Audit

1. `@role/developer-backend` Audit implemented route paths in `backend/app/api/*` against `docs/API.md`; record any mismatch before editing. Verifiable: route checklist covers every documented Phase 13 endpoint group.

2. `@role/developer-backend` Add or adjust backend route/OpenAPI tests for `/api` prefix and documented paths, including health, auth, media, jobs/results, downloads, models, experiments, and admin. Verifiable: test fails if a documented path is missing or unprefixed.

3. `@role/developer-backend` Resolve documented path mismatches with smallest route changes, especially result downloads if OpenAPI exposes only `/download/{kind}`. Verifiable: concrete documented download URLs work and `/api/jobs/{job_id}/download/media`, `/api/jobs/{job_id}/download/csv`, and `/api/jobs/{job_id}/download/json` appear in OpenAPI, without adding new product behavior.

4. `@role/developer-backend` Audit list endpoints for consistent `items`, `total`, `limit`, `offset` responses and documented filters where already in scope. Verifiable: tests cover media, jobs, detections, tracks, models, experiments, admin jobs, and admin users pagination shape.

5. `@role/developer-auth-security` Audit authentication and authorization behavior across implemented route groups. Verifiable: tests prove guest rejection, invalid-token rejection, inactive-user rejection, regular-user ownership limits, and admin-only route rejection for regular users.

6. `@role/developer-auth-security` Add focused tests for filter/ID bypass risks on user-owned resources. Verifiable: regular user cannot use `owner_id`, direct IDs, or download URLs to access another user's records/results.

7. `@role/developer-backend` Audit error response safety and consistency for frontend localization. Minimal accepted Phase 13 standard: FastAPI-compatible `detail` payloads may remain, including string HTTP error details and list validation details, if they are safe, predictable, and frontend-consumable. Verifiable: representative 400/401/403/404/422 responses have expected `detail` forms and no stack traces, secrets, tokens, password hashes, DB URLs, absolute storage paths, or forbidden CV-boundary fields. Add a new error envelope only if current behavior cannot meet this standard.

8. `@role/developer-backend` Audit OpenAPI usability for frontend development. Verifiable: generated schema has documented paths, explicit concrete download paths, tags, request/response schemas for JSON routes, auth-protected operations, and no unsafe internal path exposure.

9. `@role/developer-auth-security` Audit API response/output boundary for implemented responses. Verifiable: reusable test helper or fixture scans representative API JSON responses and confirms no forbidden CV-boundary fields and no absolute filesystem paths.

10. `@role/tester` Run backend lint from `backend/`: `python -m ruff check .`. Verifiable: command exits 0 or blocker recorded with exact failure.

11. `@role/tester` Run backend test suite from `backend/`: `python -m pytest`. Verifiable: command exits 0 or blocker recorded with exact failing tests.

12. `@role/docs-maintainer` Audit and update existing README/API notes so current backend endpoint groups and backend commands match verified implementation state. This is required because current README is stale against implemented backend APIs. Verifiable: docs mention current backend contract state honestly and do not duplicate product docs.

13. `@role/code-reviewer` Review Phase 13 diff against `docs/API.md`, `docs/AUTH_SECURITY.md`, `docs/TESTING_QA.md`, and `docs/PROJECT_CONTEXT.md`. Verifiable: review confirms no new APIs, roles, schema fields, worker behavior, frontend work, training launch, unsafe path exposure, or CV-boundary violation.
