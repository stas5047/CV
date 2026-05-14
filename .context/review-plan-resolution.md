# Phase 22 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude review has no blocking issue. Accepted items update only Phase 22 implementation contract. No source code changes allowed or made in this resolution step.

## Resolution table

| ID | Claude review item | Resolution | Reason |
|---|---|---|---|
| I1 | Experiment type conflict resolution is too permissive; canonical training schema/templates and backend-facing payloads must use doc slugs. | accepted | Matches `docs/DATA_MODEL.md` required experiment types and `docs/API.md` experiment import contract. |
| I2 | Path-safety scope misses path-like metadata fields that can leak absolute paths inside model cards and metrics artifacts. | accepted | Matches API/security rules forbidding unsafe absolute path exposure and database/storage path leakage. |
| I3 | Backend API gates should always run for Phase 22, even when backend source does not change. | accepted | Phase 22 depends on existing admin model/experiment API behavior; docs require registration/import validation. |
| O1 | Add CLI smoke test using placeholder model card and metrics template through mocked HTTP transport. | accepted | In scope for helper verification and does not change product behavior. |
| O2 | Add docs note that helper registers existing files under storage and never uploads `.pt` weights or starts training. | accepted | Matches training workflow and storage rules. |
| Q1 | Should helper accept legacy `confidence_threshold_analysis` / `tracker_behavior_comparison` aliases? | rejected | Product docs define canonical slugs only. Compatibility aliases are extra behavior and not needed for Phase 22. |

## Accepted changes applied

- `.context/research.md`
  - Added review-resolution notes binding implementation to canonical experiment slugs, path-like metadata validation, unconditional backend API gates, mocked CLI smoke test, and docs note.
- `.context/design.md`
  - Replaced permissive "align or mapper" decision with canonical schema/template/payload requirement.
  - Added explicit rejection of legacy aliases for Phase 22.
  - Added path-like metadata validation before backend mutation.
  - Made targeted backend API gates unconditional.
  - Added mocked CLI smoke and docs-note expectations.
- `.context/plan.md`
  - Updated task 3 to require canonical doc slugs in schema/templates/backend payloads.
  - Updated helper/security tests for nested path-like metadata.
  - Added mocked CLI smoke coverage.
  - Made backend tests mandatory for Phase 22.
  - Updated completion criteria.

## Rejected items

- Q1 legacy alias support: rejected for Phase 22. Implementation should correct current training schema/templates to canonical docs slugs and reject legacy input unless user explicitly approves compatibility behavior later.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

- Phase scope remains Phase 22 only: model artifact registration and experiment artifact import utilities.
- No frontend work.
- No CV worker work.
- No database migration unless documented schema gap is proven during implementation.
- No new public API route unless existing documented routes cannot support Phase 22 after evidence.
- Training is not launched from helper, API, or UI.
- Backend remains authorization authority for model registration, activation, and experiment import.
- Canonical experiment slugs for Phase 22 are:
  - `model_comparison`
  - `threshold_analysis`
  - `tracker_comparison`
  - `false_positive_analysis`
- Helper must validate top-level relative paths and path-like metadata inside imported artifacts before any backend mutation.
- Targeted backend API tests must run in Phase 22 even when backend source files are unchanged.
