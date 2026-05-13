# Phase 6 Implementation Plan

Scope: Authorization, ownership, CORS, path safety, and security utilities only. No source changes in this planning phase. Implementation must not add product APIs, frontend work, CV worker work, database migrations, or later-phase media/job/result behavior.

1. [@role/developer-auth-security] Re-read `docs/AUTH_SECURITY.md`, `docs/API.md`, `docs/ARCHITECTURE.md`, and `docs/TESTING_QA.md`.
   - Verify Phase 6 scope before edits.
   - Stop with `WARNING: CONFLICT` if docs disagree with current code.

2. [@role/developer-backend] Inspect existing backend auth, dependency, CORS, logging, config, model, and test files.
   - Verify current `/api/auth/me` still enforces valid token and active account.
   - Identify smallest existing module boundaries for helpers.

3. [@role/tester] Add failing Phase 6 tests for admin role enforcement.
   - Regular user must be rejected by admin-only dependency.
   - Admin user must be accepted.
   - Missing/invalid token must remain rejected through protected-route dependency.
   - Inactive user must remain rejected.

4. [@role/developer-auth-security] Implement reusable admin-only dependency.
   - Reuse existing current-active-user dependency.
   - Enforce exactly documented roles: `user` and `admin`.
   - Return safe HTTP error without passwords, hashes, tokens, or stack traces.

5. [@role/tester] Run targeted auth/security tests for admin dependency.
   - Command: `cd backend; python -m pytest tests/test_auth.py -q`
   - Expected: admin dependency tests pass; existing auth tests still pass.

6. [@role/tester] Add failing ownership-helper tests.
   - Owner accepted.
   - Admin accepted.
   - Other active user rejected.
   - Missing resource rejected safely.
   - Indirect ownership through a media owner is accepted for the owner and admin.
   - Indirect ownership through a job/media owner is accepted for the owner and admin.
   - Cross-owner indirect resources are rejected with the same safe not-found style response as missing resources where practical.
   - Test must not require new product endpoints.

7. [@role/developer-auth-security] Implement reusable ownership helper.
   - Support owner-id based resources from current SQLAlchemy models.
   - Support predicate/callback or explicit lookup patterns for indirect ownership through media and job records.
   - Support admin override.
   - Avoid leaking cross-owner resource existence in response detail.
   - Use forbidden response for admin-only role failures; use safe not-found style denial for user-owned missing/cross-owner resources where practical.
   - Keep helper generic enough for later media, job, result, and download services without adding those services now.

8. [@role/tester] Run targeted ownership tests.
   - Command: `cd backend; python -m pytest tests/test_auth.py -q`
   - Expected: ownership helper tests pass; existing auth tests still pass.

9. [@role/tester] Add failing path safety tests.
   - Safe relative path accepted.
   - Empty path rejected where database-facing path is required.
   - Absolute Unix path rejected.
   - Windows drive path rejected.
   - UNC path rejected.
   - `../`, `..\\`, nested slash traversal, and nested backslash traversal rejected.
   - Safe join result stays inside configured `STORAGE_ROOT`.

10. [@role/developer-auth-security] Implement path safety utilities.
    - Validate database-facing paths are relative to `STORAGE_ROOT`.
    - Prevent traversal before joining paths.
    - Safely join relative path under configured storage root.
    - Do not return absolute paths in API-facing structures.

11. [@role/tester] Add failing filename safety tests.
   - Normal filenames preserve safe display value.
   - Path components are stripped.
   - Traversal names are neutralized.
   - Empty/unsafe names produce safe fallback display name.
   - Download filename helper emits safe name without path separators.
   - Windows reserved or hostile names such as `CON`, `NUL`, trailing dots, and trailing spaces are neutralized.

12. [@role/developer-auth-security] Implement filename and download-name helpers.
    - Sanitize original filename for display metadata.
    - Ensure raw user filename never controls internal storage path.
    - Ensure suggested download names cannot traverse paths.

13. [@role/tester] Run targeted path/filename tests.
    - Command: `cd backend; python -m pytest tests/test_auth.py tests/test_settings.py -q`
    - Expected: path, filename, CORS/settings, and auth tests pass.

14. [@role/tester] Verify or add explicit CORS validation tests.
    - Explicit configured origins are accepted.
    - Wildcard origin is rejected.
    - Empty origin configuration is rejected when settings require configured origins.
    - If these tests live outside `tests/test_settings.py`, include their exact file path in targeted gate commands.

15. [@role/developer-auth-security] Review CORS validation against docs.
    - Keep configured explicit origins required.
    - Keep wildcard rejection unless implementation introduces a documented local-only exception.
    - Do not use broad wildcard CORS for non-local configuration.

16. [@role/tester] Verify secure error response behavior for Phase 6 helper paths.
    - Add a narrow test route only inside tests if needed; do not add product API surface.
    - Assert helper-raised HTTP errors expose safe detail only.
    - Assert responses do not expose tracebacks, secrets, tokens, passwords, password hashes, database passwords, or unsafe absolute storage paths.

17. [@role/developer-auth-security] Review logging and error safety.
    - Ensure new helpers do not log passwords, hashes, tokens, JWT secrets, database passwords, or sensitive environment values.
    - Ensure new HTTP errors use safe details.
    - Preserve current API response style; do not invent new public error envelope unless needed for stack-trace prevention.

18. [@role/tester] Run relevant backend gates.
    - Command: `cd backend; python -m ruff check .`
    - Expected: PASS.
    - Command: `cd backend; python -m pytest tests/test_auth.py tests/test_settings.py tests/test_logging.py -q`
    - Expected: PASS.
    - Include any new test files explicitly if they are not in the listed files.
    - Because shared security/core helpers are touched, run `cd backend; python -m pytest -q`.

19. [@role/code-reviewer] Phase 6 scope review.
    - Confirm no frontend/CV worker/source-of-truth docs changed.
    - Confirm no media/job/result/model/experiment/admin product API added.
    - Confirm no migration/schema change was introduced.
    - Confirm CV-only boundary unaffected.
    - Confirm security utilities match consulted docs.

20. [@role/docs-maintainer] Documentation/index decision.
    - Do not update product docs unless implementation changes documented commands, env variables, folder structure, or file paths.
    - If no such change, record docs update skipped in final implementation report.
