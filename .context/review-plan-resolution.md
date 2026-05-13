# Verdict: READY_FOR_IMPLEMENTATION

## Resolution table

| ID | Claude item | Resolution | Contract update |
|---|---|---|---|
| I-1 | Media image invariants left optional. | accepted | `.context/design.md` and `.context/plan.md` now require Phase 3 DB/model tests to reject image media with `frame_count != 1`, non-null `fps`, or non-null `duration_seconds`. |
| I-2 | Relative path checks need stronger examples. | accepted | `.context/design.md` and `.context/plan.md` now require unsafe path examples for Unix absolute, Windows drive-letter, UNC-style, and `..` traversal segments where DB checks are implemented. |
| I-3 | Active model uniqueness test should prove multiple inactive models are allowed. | accepted | `.context/design.md` and `.context/plan.md` now require tests that second active model is rejected and multiple inactive model rows are accepted. |
| O-1 | Add smoke test that all required table names are present in Alembic metadata before migration assertions. | accepted | `.context/design.md` and `.context/plan.md` now require Alembic/SQLAlchemy metadata table-registration smoke coverage. |
| O-2 | Add test that nullable `experiment_metrics.metric_value` is accepted. | duplicate | Already present in `.context/design.md` test strategy and `.context/plan.md` step 10 before this resolution. Kept and reinforced in step 13 test summary. |

## Accepted changes applied

- Tightened Phase 3 media schema contract for documented image invariants.
- Tightened relative-path validation examples without moving Phase 6 service path utilities into Phase 3.
- Tightened active model uniqueness tests so implementation cannot use an overbroad `UNIQUE(is_active)` rule.
- Added Alembic/SQLAlchemy metadata table-registration smoke coverage to Phase 3 test plan.

## Rejected items

- None.

## Duplicate items

- O-2: nullable `experiment_metrics.metric_value` acceptance was already in the planning contract.

## Items needing user decision

- None.

## Final contract status

- Phase 3 implementation contract remains scoped to database schema, SQLAlchemy models, Alembic initial migration, and focused database smoke tests.
- No source code changes made.
- No product docs changed.
- No accepted item conflicts with `docs/DATA_MODEL.md`, `docs/ARCHITECTURE.md`, `docs/API.md`, or `docs/TESTING_QA.md`.
