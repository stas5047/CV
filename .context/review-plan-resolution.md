# Verdict: READY_FOR_IMPLEMENTATION

Claude planning review resolved. No item conflicts with product docs. Accepted items applied only to Phase 6 planning contract files. No source code changes.

## Resolution table

| ID | Claude item | Resolution | Rationale | Contract update |
|---|---|---|---|---|
| I1 | Indirect ownership path not explicit enough. | accepted | `AUTH_SECURITY.md` requires ownership through direct resource ownership and media/job-owned resources for summaries, detections, tracks, and downloads. | `.context/design.md`, `.context/plan.md` now require direct and indirect ownership helper/test coverage. |
| I2 | CORS validation has review step but weak explicit test step. | accepted | Phase 6 scope includes CORS validation and `TESTING_QA.md` requires explicit CORS security tests. | `.context/plan.md` now requires verify-or-add CORS tests for explicit origins, wildcard rejection, and empty-origin rejection. |
| I3 | Secure error response pattern not verified. | accepted | `AUTH_SECURITY.md` and `API.md` require no stack traces, secrets, tokens, passwords, database passwords, or unsafe absolute paths in API responses. | `.context/design.md`, `.context/plan.md` now require helper-path error-response verification. |
| I4 | Validation commands may miss new tests depending on file placement. | accepted | Security helper tests may land in new files; targeted gates must not skip them. | `.context/plan.md` now requires explicit new test file inclusion plus full backend pytest because shared security/core helpers are touched. |
| O1 | State ownership denial policy once. | accepted | Docs require ownership enforcement and safe errors; choosing same not-found style response for missing/cross-owner user resources avoids existence leaks without changing product behavior. | `.context/design.md`, `.context/plan.md` now define denial policy. |
| O2 | Include Windows reserved filename cases in filename tests. | accepted | Phase 6 includes filename/download-name helpers; Windows-hostile names matter on current Windows checkout and do not conflict with docs. | `.context/design.md`, `.context/plan.md` now include `CON`, `NUL`, trailing dot/space cases. |
| Q1 | Should ownership helper return 404 for cross-owner user resources while admin-role failures return 403? | duplicate | Covered by accepted O1. | Same as O1. |
| Q2 | Should Phase 6 add one central error handler now, or only prove current FastAPI/error configuration? | duplicate | Covered by accepted I3. Contract chooses verification first; central handler only if current behavior exposes unsafe details. | Same as I3. |

## Accepted changes applied

- Ownership contract tightened for direct owner IDs plus indirect ownership through media/job records.
- Ownership denial policy added: missing and cross-owner user resources should use same safe not-found style response where practical; admin-role failures stay forbidden.
- CORS test obligation made explicit.
- Error-response safety verification added for Phase 6 helper paths.
- Filename/download-name tests expanded for Windows reserved/hostile names.
- Validation gates updated to include any new test files and full backend pytest for shared security/core helper changes.

## Rejected items

None.

## Duplicate items

- Q1 duplicates accepted O1 ownership denial policy.
- Q2 duplicates accepted I3 secure error-response verification.

## Items needing user decision

None.

## Final contract status

- Final implementation contract is Phase 6 only: authorization dependencies, ownership helpers, CORS validation, path safety, filename/download-name helpers, logging/error safety checks, and relevant backend tests.
- No product API, frontend, CV worker, Docker, database schema/migration, training, or later media/job/result/model/experiment behavior is authorized by this resolution.
- Ready for implementation after re-reading Phase 6 docs at implementation start.
