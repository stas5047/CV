# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 12 plan matches main docs: protected `/api/experiments` routes, admin-only import, published-only user visibility, nullable metrics, safe artifact paths, no training launch, no frontend/worker scope creep.

Approval needs small plan changes before implementation. Issues below are real phase risks, not broad release checks.

## Blocking issues

None.

## Important issues

1. Tracker behavior wording guard too narrow.
   - Evidence: `docs/phase.md` requires API/UI-facing data use tracker behavior wording, not absolute tracking accuracy. `docs/TRAINING_EXPERIMENTS.md` says tracker comparison is not absolute tracking accuracy and must not require MOTA, IDF1, HOTA, or manually annotated track identity metrics.
   - Plan evidence: step 4 rejects unsupported experiment type `tracking_accuracy`, but does not cover metric names or metric metadata inside valid `tracker_comparison` imports.
   - Risk: admin can import a valid `tracker_comparison` with API-facing metric names like `tracking_accuracy`, `MOTA`, `IDF1`, or `HOTA`, causing product-doc mismatch.
   - Needed change: add explicit validation/test for tracker-comparison metric names/metadata wording, or document allowed tracker behavior metric names from `TRAINING_EXPERIMENTS.md`.

2. Invalid `model_version_id` lacks explicit test.
   - Evidence: `docs/API.md` lists missing model version as an error case. `docs/DATA_MODEL.md` defines `experiment_runs.model_version_id -> model_versions.id`.
   - Plan evidence: step 7 says validate optional `model_version_id` exists before commit, but test steps do not include invalid model reference.
   - Risk: raw FK/DB error or stack detail leaks instead of safe API error.
   - Needed change: add test where admin import uses nonexistent UUID and receives safe 400/404 without storage root, stack trace, or DB internals.

3. List pagination/filter behavior not explicit in implementation/test steps.
   - Evidence: `docs/API.md` says list endpoints should support pagination when lists can grow and recommends experiment filters by experiment type and published status for admins.
   - Plan evidence: design assumes existing collection shape, but ordered steps do not require `limit`/`offset`, `experiment_type`, or admin `published` filter behavior/tests.
   - Risk: `/api/experiments` may ship as unbounded or without documented filters, causing API drift and poor frontend support.
   - Needed change: add list implementation/tests for pagination and relevant filters, with visibility enforced before returning rows.

## Optional improvements

- Add one response-shape assertion that experiment responses never include absolute `STORAGE_ROOT`, including nested metric metadata if metadata is echoed.
- In code-review checklist, include "no new experiment type aliases" so `tracker_behavior_comparison` or `tracking_accuracy` does not creep in beside documented `tracker_comparison`.

## Questions for resolution

None blocking. If implementation wants `artifacts_path` outside `reports/`, resolve before coding because current design constrains it to `reports/`.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/FRONTEND_UX.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `C:/Users/Kotletka/.codex/skills/caveman/SKILL.md`
