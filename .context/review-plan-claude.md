# Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 11 scope: admin-only backend routes, no frontend/worker/training/schema creep, admin dependency required, safe responses, targeted backend tests.

Changes needed before implementation: tighten cleanup protection model and tests. Risk sits in filesystem deletion, not route scaffolding.

## Blocking issues

None.

## Important issues

1. Active model card protection too vague.
   - Evidence: `docs/AUTH_SECURITY.md` says admin cleanup must not remove active model weights or model cards. `docs/API.md` repeats active model weights safety. `docs/ARCHITECTURE.md` documents model layout with `models/{model_version_id}/weights.pt` and `models/{model_version_id}/model_card.json`. `docs/DATA_MODEL.md` stores only `model_versions.weights_path`, no explicit model-card path.
   - Plan evidence: `.context/plan.md` steps 8-9 say protect active model artifacts/weights/cards, but do not say how to derive/protect `model_card.json` when DB has only `weights_path`; test wording says "when represented by documented paths", which can skip real active model cards.
   - Required change: implementation plan/checks must explicitly protect active model card path or whole active model directory derived from active model `weights_path`.

2. Referenced directory paths need prefix protection, not exact-path protection only.
   - Evidence: `docs/DATA_MODEL.md` lists `experiment_runs.artifacts_path` as relative path field. `docs/ARCHITECTURE.md` stores reports under directories like `reports/{experiment_id}/metrics.json` and `reports/{experiment_id}/confusion_matrix.png`.
   - Plan evidence: `.context/plan.md` step 8 says collect relative paths from documented DB fields. Exact file-path protection can miss descendants under referenced artifact directories.
   - Required change: cleanup protection set must treat referenced artifact directories and derived active model directories as protected prefixes, with tests proving child files remain.

3. Recent user-result safety lacks direct test.
   - Evidence: `docs/API.md` and `docs/AUTH_SECURITY.md` both say cleanup must not delete recent user results accidentally. `docs/DATA_MODEL.md` allows physical deletion only through safe admin cleanup and warns against deleting recent user results.
   - Plan evidence: `.context/plan.md` tests protect referenced files, active model artifacts, visible completed jobs, and path escape, but no explicit recent orphan/unreferenced result file test.
   - Required change: add targeted cleanup test where a fresh file under `results/` remains untouched, or make cleanup dry-run/no-delete outside `temp/` until retention policy exists.

## Optional improvements

- Make `backend/index.md` update non-optional if new backend files are created, because `docs/index.md` says component index files track current contents. Product docs need no change.
- Prefer cleanup response with counts and categories over path lists. If paths are returned, keep only relative/logical paths.

## Questions for resolution

- What retention window defines "recent" for cleanup? If unresolved, safest implementation is dry-run/no-delete for `uploads/`, `results/`, `reports/`, `models/`, and `datasets/`, with possible narrow cleanup of unreferenced `temp/`.
- Should cleanup physically delete files in Phase 11, or only report eligible files until retention policy exists?

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
- `docs/AUTH_SECURITY.md`
- `docs/DATA_MODEL.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING_QA.md`
