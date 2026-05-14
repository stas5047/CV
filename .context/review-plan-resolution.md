# Phase 29 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review is resolved. No item needs user decision because product docs already decide safe behavior for all blocking/important points.

## Resolution table

| ID | Claude item | Resolution | Rationale | Contract update |
|---|---|---|---|---|
| I1 | Missing explicit FPS/latency chart implementation step | accepted | `docs/phase.md` and `docs/FRONTEND_UX.md` require FPS/latency chart for `/experiments`. | `.context/plan.md` now names FPS/latency chart component, empty-state behavior, tests, and review check. `.context/design.md` now includes FPS/latency visual structure and tests. |
| I2 | Confusion matrix artifact handling under-specified | accepted | `docs/API.md` forbids unsafe path exposure; no documented safe experiment artifact image route exists. | `.context/plan.md` and `.context/design.md` now allow image rendering only from documented safe API-served URL/safe metadata field; otherwise required empty state. Tests must assert no raw path or unsafe image `src`. |
| I3 | Empty-state literal differs between `.context/design.md` and docs | accepted | Product docs are authoritative and require exact text from `docs/FRONTEND_UX.md` / `docs/TESTING_QA.md`. | `.context/design.md` now uses exact `Дані експерименту ще не завантажено`; `.context/plan.md` points tests to product docs. |
| O1 | Optional visual smoke against prototype layout | accepted | User explicitly requires frontend based on `@prototype`; smoke stays visual only and does not promote mock metrics to contract. | `.context/plan.md` review step now includes focused prototype layout comparison after build. |
| O2 | Optional forbidden-term assertions, including tracker/targeting terms | accepted | Aligns with CV-only boundary and tracker metric restrictions in docs. | `.context/plan.md` now requires text search/test coverage for forbidden English terms and Ukrainian equivalents if introduced. |
| Q1 | Should confusion matrix be deferred until backend/API exposes safe artifact URL? | duplicate | Same safe artifact policy as I2. Display is deferred unless safe documented URL/metadata exists; empty state is rendered meanwhile. | Same as I2. |

## Accepted changes applied

- Added explicit FPS/latency chart requirement to final implementation plan and design test strategy.
- Tightened confusion matrix contract: no raw `artifacts_path`, no storage-relative image `src`, no absolute paths; render image only from documented safe API-served URL/safe metadata field.
- Corrected exact experiment empty-state literal in `.context/design.md`.
- Added test expectations for FPS/latency chart, confusion matrix empty state, unsafe path absence, and exact empty text.
- Added review expectation for focused prototype visual comparison without accepting prototype mock metric semantics.
- Expanded forbidden tracker/safety wording checks.

## Rejected items

- None.

## Duplicate items

- Q1 duplicates I2 after resolution: both are same safe confusion matrix artifact policy.

## Items needing user decision

- None.

## Final contract status

- Implementation remains scoped to Phase 29 only.
- No source code changes made.
- Backend/API contract unchanged.
- Frontend must consume existing `/api/experiments?limit=100`, use Recharts, preserve Ukrainian visible UI, and keep backend as visibility authority.
- Final implementation may proceed using updated `.context/research.md`, `.context/design.md`, `.context/plan.md`, and this resolution file.
