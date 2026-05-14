# Independent Planning Review - Phase 21 Training Pipeline Artifacts

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 21 plan is mostly aligned with `docs/phase.md`, `docs/ROADMAP.md`, and training docs. Scope stays offline-training only, preserves YOLO26 primary policy, keeps single-class `drone`, avoids backend/frontend/DB/runtime changes, and includes safety checks for relative artifact paths plus large-file Git hygiene.

Changes needed before implementation: make experiment artifact/schema coverage explicit for all four documented experiment types, and make training-tool dependencies/commands reproducible instead of leaving install path implicit.

## Blocking issues

None.

## Important issues

1. Experiment artifact coverage is incomplete in atomic steps.
   - Evidence: `docs/TRAINING_EXPERIMENTS.md` requires import/display support for four experiment records: model comparison, confidence threshold analysis, tracker behavior comparison, false-positive analysis. It also lists artifact schemas and import utilities as code-agent responsibilities.
   - Evidence: `.context/plan.md` step 8 broadly says "experiment metrics"; steps 13-14 explicitly cover only false-positive analysis and tracker behavior comparison. No explicit step covers model comparison or confidence threshold analysis artifact/schema guidance.
   - Risk: implementation may produce schemas/templates that pass narrow validation but omit two required experiment families.
   - Required plan change: add explicit implementation and validation coverage for model comparison and confidence threshold analysis artifacts/schemas, alongside tracker behavior and false-positive analysis.

2. Dependency and command reproducibility is under-specified.
   - Evidence: `docs/phase.md` validation requires dataset split script, model card schema validation, and training README clarity. `docs/index.md` says component index files should list commands and say `not available yet` only when no commands exist. `.context/plan.md` step 21 says "training dependency install or report `not available yet`" but no earlier step creates or chooses a training dependency manifest/runner strategy.
   - Risk: scripts/tests may depend on packages such as YAML/schema/Ultralytics tooling without documented install command, making validation non-reproducible.
   - Required plan change: add a step to define training-local dependency/install strategy if implementation adds non-stdlib dependencies, and include exact commands in `training/index.md`.

## Optional improvements

- Add explicit validation that notebook templates start from pretrained weights, not scratch. Docs require pretrained YOLO weights; plan step 9 says this, but listed checks do not assert it.
- Add a small schema fixture for each experiment type. This would keep validation narrow while preventing drift from documented experiment contracts.

## Questions for resolution

- Should Phase 21 include a minimal offline import/validation utility for model cards and metrics, or only schemas/templates? `TRAINING_EXPERIMENTS.md` lists import utilities as code-agent responsibility, while `docs/phase.md` validation focuses on scripts, schemas, README, and Git ignore.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
- `git status --short`
