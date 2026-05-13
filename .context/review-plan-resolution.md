# Review Plan Resolution - Phase 12 Experiment Import Backend API

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review verdict was `APPROVED_WITH_CHANGES`. All doc-backed changes were accepted and applied to the Phase 12 implementation contract. No source code was modified.

## Resolution table

| # | Claude item | Resolution | Contract update |
|---:|---|---|---|
| 1 | Tracker behavior wording guard too narrow; metric names/metadata could still expose absolute tracking-accuracy language. | accepted | `.context/design.md` now requires tracker-comparison metric wording validation. `.context/plan.md` adds failing tests and service/code-review checks for forbidden `tracking_accuracy`, `MOTA`, `IDF1`, and `HOTA` wording. |
| 2 | Invalid `model_version_id` lacks explicit test. | accepted | `.context/design.md` and `.context/plan.md` now require safe 400/404 behavior for nonexistent model references without DB internals, stack traces, or storage roots. |
| 3 | List pagination/filter behavior not explicit. | accepted | `.context/design.md` and `.context/plan.md` now require `items`, `total`, `limit`, `offset`, `experiment_type` filtering, admin published-status filtering, and visibility enforcement before rows return. |
| 4 | Optional response-shape assertion: no absolute `STORAGE_ROOT`, including nested metric metadata if echoed. | accepted | `.context/design.md` and `.context/plan.md` now require response/metadata safety checks for absolute storage roots and unsafe absolute paths. |
| 5 | Optional code-review checklist item: no new experiment type aliases. | accepted | `.context/plan.md` now explicitly checks that `tracker_comparison` remains the only documented tracker experiment type and no alias such as `tracker_behavior_comparison` is added. |
| 6 | Conditional question: if implementation wants `artifacts_path` outside `reports/`, resolve before coding. | rejected | Current design does not want paths outside `reports/`; keeping `reports/` constraint matches Phase 12 contract and avoids scope expansion. |

## Accepted changes applied

- Added tracker behavior metric wording guard to `.context/design.md`.
- Added allowed tracker behavior indicator examples and forbidden tracking-accuracy terms to `.context/plan.md`.
- Added explicit invalid `model_version_id` test/validation contract.
- Added list pagination and experiment filter tests/implementation contract.
- Added nested metric metadata path-safety response contract.
- Added no-alias code-review check for experiment types.

## Rejected items

- Artifact paths outside `reports/` were not adopted. Phase 12 remains scoped to existing report artifacts under storage `reports/`.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

Phase 12 implementation contract is ready. Implement only:

- `GET /api/experiments`;
- `GET /api/experiments/{experiment_id}`;
- `POST /api/experiments/import`;
- backend schemas/services/router/tests needed for those endpoints.

Do not implement frontend, CV worker, training execution, migrations, new top-level folders, new experiment types, or routes outside documented Phase 12 scope.
