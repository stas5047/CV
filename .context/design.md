# Design - Phase 13 Backend Contract Audit

## Phase Goal

Consolidate implemented backend API behavior before worker and frontend implementation depend on it. Phase output should make endpoint paths, `/api` prefix, OpenAPI schema, error shapes, pagination, access controls, and security tests match documented contracts.

## Intended Behavior From Docs

Confirmed facts:

- All API routes must be prefixed with `/api`.
- Health endpoints are public and must not leak secrets.
- Protected endpoints require valid JWT and active account.
- User-owned resources require ownership checks; admins can access broader/global data where docs allow.
- Admin-only routes require admin role.
- List endpoints that can grow should be paginated.
- API errors must be clear and safe for frontend Ukrainian localization.
- API responses and exports must not expose passwords, password hashes, JWT secrets, raw tokens, unsafe absolute filesystem paths, or forbidden CV-boundary fields.
- Download routes must enforce owner/admin access and serve files without exposing internal paths.
- No-detection results are completed jobs, not errors.
- Training must not be launched from API.
- API outputs may expose only CV data: image-space detection status, frame index, timestamp, bbox, center point, confidence, class label, track ID, FPS, model version, and summary metrics.

## Architecture Decisions

Confirmed facts:

- Backend remains public API and authorization authority.
- Route handlers should stay thin; business rules stay in services/domain helpers.
- Phase 13 should prefer auditing and focused contract fixes over feature growth.
- Test additions should target contract edges found by audit.

Assumptions:

- If route path mismatch is found, adjust implementation toward `API.md` rather than changing product docs.
- If OpenAPI lacks usable frontend metadata, add response models, route names, tags, summaries, or explicit documented routes without changing product behavior.
- If error shape normalization is needed, prefer one small shared schema/handler pattern and tests, only if docs can support it.

## Backend Impact

- Audit all implemented routes against `docs/API.md`.
- Ensure `/api` prefix remains centralized and no route bypasses it.
- Check dynamic download route against documented concrete download endpoints.
- Check OpenAPI generated paths, schemas, auth security scheme, tags, and list response models.
- Normalize unsafe or inconsistent error responses only where needed for frontend localization and security.
- Use this Phase 13 error-response standard unless implementation evidence shows it is insufficient: FastAPI-compatible `detail` payloads are acceptable for MVP, including string details for HTTP errors and list details for validation errors, when tests prove they are safe, predictable, and frontend-consumable.
- Do not add a new global error envelope in Phase 13 unless existing implemented behavior cannot satisfy `docs/API.md` and `docs/AUTH_SECURITY.md` with focused fixes.
- Keep route handlers thin and use existing services.

## Frontend Impact

- No frontend implementation in this phase.
- Backend OpenAPI and error response consistency should make later frontend API client and Ukrainian localization safer.

## DB Impact

- No schema or migration changes intended.
- DB is touched only through tests if needed for backend API contract coverage.

## API Impact

- Possible API contract fixes are limited to documented behavior:
  - concrete documented download routes;
  - consistent paginated response format;
  - safe documented errors;
  - OpenAPI usability.
- No new endpoint groups, schema fields, roles, resource types, worker behavior, or frontend flows.

## Security/Privacy Impact

- Phase explicitly touches security audit.
- Must verify guest, invalid-token, inactive-user, regular-user, admin, and cross-owner behavior across implemented route groups.
- Must verify API response text and OpenAPI-visible examples do not expose secrets, absolute storage paths, password hashes, tokens, or forbidden CV-boundary fields.
- Must preserve generic 404 for missing versus cross-owner user-owned resources where current pattern already avoids enumeration.

## Test Strategy

Relevant checks only:

- `python -m ruff check .` from `backend/`.
- `python -m pytest` from `backend/`.
- Targeted backend tests while implementing:
  - route/OpenAPI audit test for documented paths and `/api` prefix;
  - explicit OpenAPI assertions for documented concrete download paths `/api/jobs/{job_id}/download/media`, `/api/jobs/{job_id}/download/csv`, and `/api/jobs/{job_id}/download/json`;
  - pagination consistency tests for growable list endpoints;
  - error response safety/shape tests for selected 400/401/403/404/422 cases, including both string `detail` and validation-list `detail` forms when current FastAPI behavior is retained;
  - ownership/filter bypass tests for media/jobs/results/admin-visible lists;
  - reusable absolute-path and forbidden-field response scan fixture/helper for representative implemented JSON response bodies/download metadata.
- Optional manual OpenAPI check by loading app schema in a test, not by starting frontend.

## Ambiguities Or Conflicts

- No `WARNING: CONFLICT` found among consulted product docs for Phase 13.
- Resolved ambiguity: docs require "clear error messages suitable for frontend Ukrainian localization" but do not define an exact JSON error envelope; Phase 13 accepts FastAPI-compatible `detail` payloads if tested as safe and frontend-consumable.
- Ambiguity: `API.md` documents three concrete download routes, while current implementation uses one dynamic route. Implementation should resolve toward documented external contract.
- Resolved ambiguity: README current-state wording lags implementation; Phase 13 implementation must audit and update README/API notes to match verified endpoint groups and commands.
