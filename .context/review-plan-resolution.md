# Phase 28 Planning Review Resolution - Claude

## Verdict: READY_FOR_IMPLEMENTATION

Claude review found no blocking product-doc conflict. Accepted changes tighten Phase 28 frontend implementation and tests only. No source code changed.

## Resolution table

| ID | Claude item | Resolution | Reason | Contract update |
|---|---|---|---|---|
| I1 | Required model display fields are not fully test-covered. | accepted | `docs/phase.md`, `docs/FRONTEND_UX.md`, `docs/TRAINING_EXPERIMENTS.md`, and `docs/TESTING_QA.md` require model name, family, variant, active state, dataset description, key metrics, model size when known, and YOLO11 fallback metadata when used. | Updated `.context/design.md` and `.context/plan.md` test coverage. |
| I2 | Admin weights-path form behavior needs explicit relative-path handling. | accepted | Product docs require existing storage-relative model paths, no absolute path exposure, and backend authority. Client guard is allowed as UX/security defense while backend remains final validator. | Updated `.context/design.md` and `.context/plan.md` form/test contract. |
| I3 | Activation success path should prove visible active-state update. | accepted | `docs/phase.md` requires active model visually clear; `docs/TESTING_QA.md` requires admins can activate one model version. Test must catch stale active-state UI. | Updated `.context/design.md` and `.context/plan.md` activation assertions. |
| O1 | Use one fixture with missing metrics and one with known metrics/model size. | accepted | Low-risk way to prove missing and present metric behavior separately. | Added to `.context/plan.md`. |
| O2 | Keep admin form labels precise; no absolute path examples. | duplicate | Covered by accepted I2. | No separate change. |
| O3 | Keep `GET /models?limit=100` acceptable, preserve helper shape for later pagination. | duplicate | Existing plan already uses `GET /models?limit=100` through focused API helpers and avoids endpoint changes. Pagination extension is outside Phase 28 unless implementation needs a small typed helper option. | No separate change. |
| Q1 | Confirm MEDIUM vs HIGH risk if team wants stronger gates. | rejected | User gave no HIGH-risk requirement. Current contract already marks MEDIUM assumption and includes relevant frontend lint/test/build gates. Asking would add no needed decision for Phase 28. | No change. |

## Accepted changes applied

- `.context/design.md`: added explicit fixture/display coverage for dataset description, model size, metrics, and YOLO11 fallback metadata.
- `.context/design.md`: added admin weights-path client validation requirements for absolute-looking Unix paths, Windows drive paths, and traversal-looking paths, while preserving backend authority.
- `.context/design.md`: added safe Ukrainian rendering requirement for backend validation errors.
- `.context/design.md`: added activation refetch/update assertion requiring newly active model to be visually active and previous active state not misleading.
- `.context/plan.md`: expanded `ModelPageParts.tsx` scope to include required display fields and weights-path helper/client guard.
- `.context/plan.md`: expanded `models-page.test.tsx` scope for required fields, split metric fixtures, unsafe path rejection, and active-state update after activation.

## Rejected items

- Q1 risk confirmation: rejected as unnecessary. Phase remains MEDIUM assumption with frontend lint/test/build gates. No broader HIGH-risk gates added.

## Duplicate items

- O2 is duplicate of I2.
- O3 is already covered by existing focused model API helper plan and documented endpoint use.

## Items needing user decision

- None.

## Final contract status

- Final implementation contract is scoped to Phase 28 only.
- Source code must not change during this planning-resolution step.
- Implementation may touch only the model registry frontend surface, model API helper/types, focused tests, and required frontend index/docs updates during the later implementation phase if repository policy requires them.
- Backend, database, CV worker, training, experiments page, admin page, and product docs remain out of scope for Phase 28 implementation unless a later review finds a direct Phase 28 blocker.
