# Planning Review Resolution - Phase 21 Training Pipeline Artifacts

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review verdict was `APPROVED_WITH_CHANGES`. All blocking status: none. Accepted changes are applied only to `.context/` planning contract files. No source code changes are part of this resolution.

## Resolution table

| ID | Claude item | Resolution | Rationale | Applied update |
|---|---|---|---|---|
| I1 | Experiment artifact coverage incomplete: plan named tracker behavior and false-positive explicitly but did not explicitly cover model comparison or confidence threshold analysis. | accepted | `docs/TRAINING_EXPERIMENTS.md` requires all four experiment records: model comparison, confidence threshold analysis, tracker behavior comparison, false-positive analysis. No conflict with product docs. | `.context/plan.md` now has explicit steps and checks for all four experiment artifact families; `.context/design.md` and `.context/research.md` reflect same contract. |
| I2 | Dependency and command reproducibility under-specified. | accepted | Phase validation requires runnable split/schema checks, and component index rules require commands or `not available yet`. If non-stdlib dependencies appear, install path must be reproducible. | `.context/plan.md` adds dependency/command strategy step and validation; `.context/design.md` adds reproducibility decision; `.context/research.md` updates assumption. |
| O1 | Add explicit validation that notebook templates start from pretrained weights, not scratch. | accepted | `docs/TRAINING_EXPERIMENTS.md` requires training starts from pretrained YOLO weights. Validation should catch drift. | `.context/plan.md` adds notebook-template check; `.context/design.md` adds test strategy item. |
| O2 | Add small schema fixture for each experiment type. | duplicate | Covered by accepted I1 because all four experiment families now require explicit schema fixture validation. | Applied through I1 updates in `.context/plan.md` and `.context/design.md`. |
| Q1 | Decide whether Phase 21 includes minimal offline import/validation utility for model cards and metrics, or only schemas/templates. | accepted | `docs/TRAINING_EXPERIMENTS.md` lists import utilities as code-agent responsibility, but Phase 21 must stay offline and not add runtime app behavior. | `.context/plan.md` adds minimal offline artifact validation/import-readiness utility; `.context/design.md` scopes it away from backend routes, DB writes, frontend flows, and runtime training launch; `.context/research.md` records same. |

## Accepted changes applied

- Added explicit Phase 21 contract coverage for all four experiment artifact families: model comparison, confidence threshold analysis, tracker behavior comparison, false-positive analysis.
- Added dependency/install command strategy requirement when training scripts/tests introduce non-stdlib dependencies.
- Added notebook-template validation for pretrained YOLO weights and no train-from-scratch drift.
- Added all-four-experiment schema fixture validation.
- Scoped import utility work to offline artifact validation/import-readiness only.

## Rejected items

None.

## Duplicate items

- O2: schema fixture per experiment type. Duplicate of accepted I1 and applied through that broader experiment-coverage fix.

## Items needing user decision

None.

## Final contract status

Phase 21 implementation contract is ready. Scope remains offline training artifacts only:

- no backend API endpoints;
- no database migrations or writes from training utilities;
- no frontend routes or UI;
- no CV worker queue/inference changes;
- no web UI/backend training launch;
- no real datasets, weights, generated reports, or processed media committed;
- YOLO26 remains primary, YOLO11 fallback only when reported and documented;
- all outputs remain CV-only and image-space where applicable.
