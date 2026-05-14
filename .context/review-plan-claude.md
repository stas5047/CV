# Phase 28 Planning Review - Frontend Model Registry Page

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan is mostly aligned with Phase 28: protected `/models`, authenticated model list, admin-only register/activate controls, backend REST-only calls, Ukrainian UI, no training launch, no new backend/database scope.

Changes needed before implementation: tighten test/implementation plan around required model display fields and relative weights-path behavior. No blocking product-doc conflict found.

## Blocking issues

None.

## Important issues

1. Required model display fields are not fully test-covered.
   - Evidence: `docs/phase.md` and `docs/FRONTEND_UX.md` require `/models` to show model name, family, variant, active status, dataset description, key metrics, and model size when known.
   - Evidence: `docs/TRAINING_EXPERIMENTS.md` requires YOLO26 primary and YOLO11 fallback metadata represented when fallback is used.
   - Plan step 3 mentions metric extraction and fallback badge, but plan step 6 omits explicit tests for dataset description, model size when known, and YOLO11 fallback rendering. Add model fixture coverage for these fields so implementation does not pass with partial cards.

2. Admin weights-path form behavior needs explicit relative-path handling.
   - Evidence: `docs/phase.md` requires admin model registration form using existing relative storage paths.
   - Evidence: `docs/API.md` says first implementation registers existing relative paths under model storage.
   - Evidence: `docs/AUTH_SECURITY.md` and `docs/TESTING_QA.md` require no absolute path exposure and model weights paths to be relative.
   - Plan hides `weights_path` from display, but does not explicitly require form helper text/client validation for absolute/traversal-looking paths or a test that submitted payload uses a storage-relative path. Backend remains authority, but frontend plan should prevent obvious unsafe input and safely render backend validation errors in Ukrainian.

3. Activation success path should prove visible active-state update.
   - Evidence: `docs/phase.md` validation requires active model to be visually clear, and `docs/TESTING_QA.md` model registry tests require admins can activate one model version.
   - Plan tests activation PATCH call, but does not explicitly test refetch/update makes newly active model visually active and old state no longer misleading. Add a focused assertion after activation mutation/refetch.

## Optional improvements

- Add one test fixture with missing metrics and one with known metrics/model size, instead of overloading a single fixture.
- Keep admin form labels precise: storage-relative model weights path, no examples with `/app/storage`, drive letters, or host paths.
- Keep `GET /models?limit=100` acceptable for this phase, but preserve API helper shape so pagination can be extended later without page rewrite.

## Questions for resolution

- User prompt left risk as `<MEDIUM | HIGH>`. Existing research assumes MEDIUM. Confirm only if team wants HIGH-risk gates beyond frontend lint/test/build.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
