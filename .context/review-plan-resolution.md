# Planning Review Resolution - Phase 13 Backend Contract Audit

## Verdict: READY_FOR_IMPLEMENTATION

Claude review found no blockers. All doc-consistent items are accepted. No item needs user decision.

## Resolution Table

| ID | Claude item | Resolution | Reason | Contract update |
|---|---|---|---|---|
| I1 | README/API notes update may be skipped despite stale README. | accepted | `docs/phase.md` requires README/API notes update, and `README.md` is stale against implemented backend endpoint groups. | Plan step 12 now makes README/API notes audit/update required. Research records stale README fact. Design marks ambiguity resolved. |
| I2 | Error response normalization under-specified. | accepted | `docs/API.md` requires clear predictable errors but does not require custom envelope. | Design and plan define minimal Phase 13 standard: FastAPI-compatible `detail` forms acceptable if tested safe, predictable, and frontend-consumable; new envelope only if current behavior fails that standard. |
| O1 | Add OpenAPI assertions for documented concrete download paths. | accepted | `docs/API.md` documents concrete `/download/media`, `/download/csv`, `/download/json` routes. | Plan steps 3 and 8 now require explicit concrete download paths in OpenAPI. Design test strategy includes assertions. |
| O2 | Include reusable response scan fixture for absolute paths and forbidden CV-boundary fields. | accepted | `docs/API.md`, `docs/AUTH_SECURITY.md`, and `docs/PROJECT_CONTEXT.md` ban unsafe paths and forbidden output fields. | Plan step 9 and design test strategy now require reusable scan helper/fixture for representative JSON responses. |
| Q1 | Keep FastAPI/Pydantic default error payloads or introduce shared envelope? | accepted | Product docs do not mandate envelope; adding one now may create unnecessary API churn. | Final contract keeps FastAPI-compatible `detail` payloads if tests prove string/list details are safe and frontend-consumable. |

## Accepted Changes Applied

- `.context/research.md`
  - Added accepted planning-review facts for required README/API notes update, minimal error-response standard, concrete download OpenAPI assertions, and reusable response boundary scan.
- `.context/design.md`
  - Added Phase 13 error-response design decision.
  - Added explicit download OpenAPI assertion requirement.
  - Added string/list `detail` test criterion.
  - Added reusable response scan fixture/helper requirement.
  - Resolved README and error-envelope ambiguities.
- `.context/plan.md`
  - Updated step 3 to require concrete documented download paths in OpenAPI.
  - Updated step 7 to define minimal accepted error-response standard.
  - Updated step 8 to require concrete download paths in OpenAPI usability audit.
  - Updated step 9 to require reusable response/output boundary scan helper or fixture.
  - Updated step 12 to make README/API notes audit/update required.

## Rejected Items

None.

## Duplicate Items

None.

## Items Needing User Decision

None.

## Final Contract Status

- Scope remains Phase 13 only: backend contract audit, pagination, OpenAPI, error response normalization, security test audit, and README/API notes.
- No source-code implementation performed in this resolution step.
- No product-doc conflicts found.
- Implementation may proceed under updated `.context/plan.md`.
