# Planning Review Resolution - Phase 27

## Verdict: READY_FOR_IMPLEMENTATION

Claude review verdict was `APPROVED_WITH_CHANGES`. All required changes are accepted, doc-consistent, and applied only to the Phase 27 implementation contract. No source code modified.

## Resolution table

| ID | Claude item | Resolution | Reason | Contract update |
|---|---|---|---|---|
| I1 | Make authenticated media preview explicit. | accepted | Protected result/download endpoints require JWT, ownership checks, and no internal path exposure. Preview must use protected backend responses, not raw storage paths. | Updated `.context/design.md` and `.context/plan.md` to require authenticated blob preview URLs, object URL cleanup, and Ukrainian fallback notice. |
| I2 | Add/verify route protection tests for `/jobs` and `/jobs/:jobId`. | accepted | `docs/FRONTEND_UX.md` requires protected routes to redirect guests; `docs/TESTING_QA.md` includes protected route checks and Phase 27 routes. | Updated `.context/plan.md` test steps to verify unauthenticated redirects or explicit existing guard coverage for both routes. |
| I3 | Add manual UI/download smoke to execution steps. | accepted | Phase validation requires downloads work from UI; manual checks catch browser-only download, preview, overflow, and polling issues. | Updated `.context/plan.md` with manual browser smoke step for list/detail states, downloads, and video preview fallback. |
| O1 | Clarify local filename search scope. | accepted | Server pagination plus client-side search can mislead users if wording implies whole-history search. Clarification stays within "filters where practical." | Updated `.context/design.md` and `.context/plan.md` to limit filename search to currently loaded page and require clear Ukrainian wording. |
| O2 | Keep model filter conditional. | duplicate | Existing `.context/design.md` and `.context/plan.md` already require model filter only when backed by existing `/models`; no new change needed. | No update. |

## Accepted changes applied

- `.context/design.md`
  - Added authenticated blob preview requirement using protected backend responses.
  - Required object URL cleanup on cleanup/page change.
  - Required Ukrainian fallback notice when browser preview is unavailable.
  - Clarified filename search is only over the currently loaded page.
- `.context/plan.md`
  - Added API/client work for authenticated preview blobs and object URL cleanup.
  - Hardened job detail implementation step for authenticated preview or fallback notice.
  - Added guest redirect/route protection test checks for `/jobs` and `/jobs/:jobId`.
  - Added manual browser smoke step before review/docs steps.
  - Clarified client-side filename search scope.

## Rejected items

- None.

## Duplicate items

- O2: Conditional model filter. Already present in final contract before resolution; remains unchanged.

## Items needing user decision

- None.

## Final contract status

- Scope remains Phase 27 only: frontend jobs history and job details pages.
- No backend, database, CV worker, training, runtime, or product-doc changes added.
- Source-of-truth docs remain authoritative over `.context/`.
- Implementation may proceed using `.context/research.md`, `.context/design.md`, `.context/plan.md`, and this resolution.
