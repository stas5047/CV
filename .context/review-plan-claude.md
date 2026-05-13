# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 3 plan fits documented scope: SQLAlchemy models, Alembic initial migration, constraints, indexes, and focused DB smoke tests only. No frontend, worker, auth endpoint, seed, upload API, Celery/Redis, or training scope creep found.

Main gaps are test/constraint specificity for DB rules that docs make mandatory. None block implementation, but implementer should address before final phase verdict.

## Blocking issues

None.

## Important issues

1. Media image invariants left optional.

Evidence: `docs/DATA_MODEL.md` requires image media to have `frame_count = 1`, `fps = null`, and `duration_seconds = null`. `.context/plan.md` step 5 says practical image/null checks are covered “if implemented,” and `.context/design.md` says these may be DB checks or service validation. Phase 3 validation allows DB constraints or documented service-validation TODO/tests, but plan does not require either concrete outcome. Risk: invalid image metadata can enter schema before upload service exists.

2. Relative path checks need stronger examples.

Evidence: `docs/DATA_MODEL.md` path fields must store relative paths only, and `docs/ARCHITECTURE.md` says paths are interpreted under `STORAGE_ROOT`; absolute host/container paths are invalid. `.context/plan.md` step 11 verifies only absolute path examples. Risk: Windows absolute paths, UNC paths, and traversal-like paths such as `../results/x` may pass smoke tests and become persistent unsafe references.

3. Active model uniqueness test should prove multiple inactive models are allowed.

Evidence: `docs/DATA_MODEL.md` requires only one active `model_versions` row at a time, not one inactive row. `.context/plan.md` step 6 tests that second active row is rejected, but does not state that multiple inactive rows remain valid. Risk: implementation may use overly broad `UNIQUE(is_active)` instead of partial unique index/constraint for active rows.

## Optional improvements

- Add one smoke test that all required table names are present in Alembic metadata before migration assertions. This catches missed model imports in `env.py`.
- Add one test that nullable `experiment_metrics.metric_value` is accepted, since frontend later depends on incomplete imports rendering safely.

## Questions for resolution

None.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
