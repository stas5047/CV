# Phase 11 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review is resolved. All review items are either accepted or resolved by tightening the Phase 11 contract. No item conflicts with product docs. No user decision is required for this phase because ambiguous cleanup deletion is constrained to the safest documented behavior.

## Resolution table

| ID | Claude item | Resolution | Rationale | Contract updates |
|---|---|---|---|---|
| I1 | Active model card protection too vague. | accepted | `docs/AUTH_SECURITY.md` requires active model cards to remain. `docs/ARCHITECTURE.md` documents `models/{model_version_id}/model_card.json`; `docs/DATA_MODEL.md` stores only `model_versions.weights_path`, so implementation must derive protection from the active model directory or `weights_path`. | `.context/design.md`, `.context/plan.md` |
| I2 | Referenced directory paths need prefix protection, not exact-path protection only. | accepted | `experiment_runs.artifacts_path` can reference a report artifact directory. Exact-path-only cleanup can delete referenced descendants. | `.context/design.md`, `.context/plan.md` |
| I3 | Recent user-result safety lacks direct test. | accepted | Product docs require cleanup not delete recent user results accidentally, but no retention window exists. Contract now forbids physical deletion from `uploads/`, `results/`, `reports/`, `models/`, and `datasets/` in Phase 11 unless a future retention policy is approved; tests must prove a fresh unreferenced `results/` file remains. | `.context/design.md`, `.context/plan.md` |
| O1 | Make `backend/index.md` update non-optional if new backend files are created. | accepted | `docs/index.md` says component index files track current contents. Phase 11 creates backend admin files, so backend index must be updated. | `.context/plan.md` |
| O2 | Prefer cleanup response with counts/categories over path lists. | accepted | Count/category response reduces path exposure risk and satisfies safe reporting. If any paths are returned, they must be relative/logical only. | `.context/design.md`, `.context/plan.md` |
| Q1 | What retention window defines "recent"? | accepted | No retention window is documented. Phase 11 must not invent one; cleanup must not physically delete user result/media/report/model/dataset files. | `.context/design.md`, `.context/plan.md` |
| Q2 | Should cleanup physically delete files in Phase 11, or only report eligible files until retention policy exists? | accepted | Phase 11 may physically delete only clearly safe, unreferenced `temp/` files. Other folders are dry-run/report-only until product docs define retention. | `.context/design.md`, `.context/plan.md` |

## Accepted changes applied

- Cleanup protection must include active model `weights_path` and the derived active model directory, including `model_card.json`.
- Cleanup protection must treat referenced directories as protected prefixes, not just exact paths.
- `experiment_runs.artifacts_path` descendants must remain protected.
- Phase 11 cleanup must not physically delete files from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/` without a future documented retention policy.
- Phase 11 may physically delete only unreferenced `temp/` files after safe path validation.
- Cleanup response should use counts/categories; any returned path-like value must be relative/logical and never absolute.
- Tests must cover active model card/directory protection, referenced directory prefix protection, fresh result preservation, no absolute path exposure, and `temp/`-only physical deletion behavior.
- `backend/index.md` update is required if Phase 11 creates backend files or changes backend command/file listings.

## Rejected items

None.

## Duplicate items

None.

## Items needing user decision

None for Phase 11.

Future product decision, not a Phase 11 blocker: define a concrete retention window and deletion eligibility policy if cleanup should remove old `uploads/`, `results/`, `reports/`, `models/`, or `datasets/` files.

## Final contract status

`.context/research.md`, `.context/design.md`, and `.context/plan.md` are updated only for accepted review items. Final Phase 11 implementation contract is ready for implementation and remains scoped to admin backend APIs plus conservative storage cleanup.
