# Phase Design

## Phase goal

Add reusable backend security primitives for protected product APIs before media, jobs, results, models, experiments, and admin APIs are implemented.

## Intended behavior from docs

Confirmed:

- Protected routes require valid JWT authentication.
- Inactive users must be rejected on protected routes.
- Admin-only routes must enforce `role = admin`.
- Regular users may access user-owned resources only when resource belongs to them or to a media/job record owned by them.
- Admins may access global resources through admin-authorized routes and permissions.
- Backend must prevent path traversal.
- Database-facing file references must be relative to `STORAGE_ROOT`.
- API responses and downloads must not expose unsafe absolute host/container paths.
- Safe download endpoints must verify ownership or admin access before serving files.
- Uploaded filenames must be sanitized and must not control internal storage paths.
- CORS must use configured explicit origins; wildcard is not allowed in non-local configuration.
- Logs must not include passwords, password hashes, tokens, JWT secrets, database passwords, or sensitive environment values.
- API responses must not expose stack traces.

Assumptions:

- Phase 6 creates reusable primitives and tests only; it does not implement media upload, job creation, results downloads, admin APIs, or frontend behavior.
- Existing `/api/auth/me` remains enough to prove missing/invalid token rejection.
- Security utilities should avoid storing or returning absolute paths.

## Architecture decisions

- Backend remains authorization authority.
- No frontend, CV worker, Docker service, database schema, or product endpoint work belongs in this phase.
- Role and ownership checks should live in backend dependency/service helper layer, not frontend.
- Path safety should be centralized so later upload/download code cannot repeat ad hoc path logic.
- Storage helpers should resolve paths under `STORAGE_ROOT` only at runtime and return safe filesystem paths internally while keeping database/API references relative.
- Logging helpers should redact sensitive values and sensitive key names before emission.
- Error handling should preserve FastAPI-compatible errors without exposing stack traces or secrets.

## Backend impact

- Add or extend reusable auth/security dependencies for:
  - active-user requirement.
  - admin-role requirement.
  - ownership-or-admin checks for existing model instances, direct owner IDs, and indirect ownership through media/job records.
- Add or extend path safety helpers for:
  - relative path validation.
  - traversal rejection.
  - safe join under configured storage root.
  - safe download filename generation.
  - upload filename sanitization.
- Add tests proving helpers reject unsafe inputs and preserve safe inputs.
- Do not add public product API routes.

## Frontend impact

- None in this phase.

## DB impact

- No schema or migration changes planned.
- Existing relative-path database checks remain useful defense-in-depth, but Phase 6 must add service-level validation too.

## API impact

- No new product endpoints planned.
- Existing protected auth behavior may be tested.
- Future endpoints will consume new dependencies/utilities.

## Security/privacy impact

- Positive impact: reusable enforcement for role checks, ownership checks, active accounts, safe paths, safe filenames, CORS origin validation, safe errors, and secret-safe logs.
- Risk: weak helper semantics could later permit cross-owner resource access or path traversal. Tests must cover deny cases explicitly.
- Sensitive data must not appear in test logs, API error details, or helper outputs.

## Accepted review clarifications

- Ownership helper contract must support direct ownership and indirect ownership needed by later summaries, detections, tracks, and downloads:
  - direct owner ID checks for resources that carry `owner_id`/`user_id`;
  - predicate/callback or explicit owner lookup for resources owned through `media_files.user_id`;
  - predicate/callback or explicit owner lookup for resources owned through `processing_jobs.media_file.user_id`;
  - admin override only after authenticated active admin is known.
- Ownership denial policy for user-owned resources:
  - missing resources and cross-owner resources should return the same safe not-found style response where practical, to avoid leaking existence;
  - admin-role failures remain forbidden responses.
- CORS must have explicit test or existing-test verification for:
  - configured explicit origins accepted;
  - wildcard origin rejected;
  - empty origin configuration rejected when settings require configured origins.
- Error-response safety must be verified for Phase 6 helper paths:
  - safe `HTTPException` detail only;
  - no traceback exposure;
  - no secret, token, password, password hash, database password, or unsafe absolute storage path exposure.
- Filename/download-name tests should include Windows-hostile names in addition to path separator and traversal inputs:
  - reserved device names such as `CON` and `NUL`;
  - trailing dots/spaces;
  - empty or all-unsafe names.

## Test strategy

- Backend unit tests for admin dependency:
  - admin accepted.
  - regular user rejected with 403.
  - inactive user rejected through existing active-user dependency.
- Backend unit tests for ownership helper:
  - owner accepted.
  - admin accepted.
  - other user rejected with 404 or 403 according to existing helper contract.
  - missing resource rejected without leaking ownership.
- Backend unit tests for path safety:
  - safe relative paths accepted.
  - absolute Unix paths rejected.
  - Windows drive paths rejected.
  - UNC paths rejected.
  - `..` traversal rejected in slash and backslash forms.
  - safe join result stays under `STORAGE_ROOT`.
  - unsafe download names are sanitized.
- Backend tests for CORS/settings:
  - explicit origins accepted.
  - wildcard rejected.
  - empty origins rejected.
- Backend logging/error tests:
  - passwords, tokens, JWT secret, database URL/password values are redacted.
  - unsafe absolute storage paths are not returned by helper-facing API responses.
- Relevant gates only:
  - `cd backend; python -m ruff check .`
  - `cd backend; python -m pytest tests/test_auth.py tests/test_settings.py tests/test_logging.py`
  - `cd backend; python -m pytest` if shared auth/core helpers changed broadly.

## Ambiguities or conflicts

- No `WARNING: CONFLICT`.
- Ambiguity: docs do not prescribe internal module names or exact helper function signatures.
- Resolved ambiguity: user-owned missing/cross-owner denial should use the same safe not-found style response where practical; admin-role failures should use forbidden.
- Resolved ambiguity: Phase 6 should not add a central error envelope unless implementation discovers current FastAPI configuration exposes stack traces or secrets. Prove current helper errors are safe first.
