# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 8 plan matches main product docs: backend-only model registry API, authenticated reads, admin-only registration/activation, no weight upload, no training launch, no frontend/CV-worker scope creep.

No blocking issue found. Important changes needed before implementation: tighten inactive-user tests, resolve `weights_path` relative-root ambiguity, and make YOLO11 fallback handling prove actual documented fallback metadata rather than plain enum acceptance.

## Blocking issues

None.

## Important issues

1. Inactive-user access is not tested for new model endpoints.
   - Evidence: `docs/AUTH_SECURITY.md` says inactive users must not use protected API routes. `docs/API.md` says model endpoints are protected. `.context/plan.md` step 9 covers guests and regular-user admin rejection, but not inactive authenticated accounts.
   - Risk: route could use valid-token auth without active-user enforcement and still pass Phase 8 API tests.
   - Required change: add at least one inactive-user test for `GET /api/models`, and preferably one admin mutation path too if inactive admin fixtures exist.

2. `weights_path` accepted/storage form remains ambiguous.
   - Evidence: `docs/DATA_MODEL.md` says `model_versions.weights_path` is relative and first implementation registers paths under `STORAGE_ROOT/models`; it also allows interpretation under `STORAGE_ROOT` or documented sub-root such as `MODELS_ROOT`. `.context/design.md` and `.context/research.md` both identify ambiguity. `.context/plan.md` step 5 says resolve under configured model storage, but does not state whether API/db value is `models/yolo26s/weights.pt` or `yolo26s/weights.pt`.
   - Risk: implementation may double-prefix `models/`, accept a path valid under wrong root, or produce DB values inconsistent with later worker model loading.
   - Required change: before coding, choose one canonical wire/db form for Phase 8 and add a positive test with that exact form plus negative tests for absolute/traversal/outside-root paths.

3. YOLO11 fallback test is too weak as written.
   - Evidence: `docs/CV_PIPELINE.md` and `docs/TRAINING_EXPERIMENTS.md` say YOLO11 is fallback only after YOLO26 unavailability is reported/documented, and actual family must be recorded in model metadata. `.context/plan.md` step 9 only says `YOLO11 accepted as metadata`.
   - Risk: implementation may allow undocumented YOLO11 registrations as normal primary models, weakening product policy.
   - Required change: test should verify YOLO11 is represented accurately in `model_family` and accompanying metadata. If API cannot enforce fallback documentation yet, record that as an explicit limitation in implementation status, not as silent normal behavior.

## Optional improvements

1. Add a small list-response shape test for pagination/filter parameters.
   - Evidence: `docs/API.md` recommends pagination for growing list endpoints and model filters for active status, family, and variant. `.context/plan.md` makes filters conditional and does not mention pagination tests.
   - Why optional: model registry size is likely small in MVP, and docs use "recommended" rather than mandatory language.

2. Add a response-body assertion that no field contains configured absolute storage/model root.
   - Evidence: `docs/API.md`, `docs/AUTH_SECURITY.md`, and `docs/DATA_MODEL.md` forbid absolute filesystem path exposure.
   - Plan already says no absolute paths in response body; explicit assertion would make this harder to regress.

## Questions for resolution

1. Should Phase 8 store `weights_path` relative to `STORAGE_ROOT` as `models/<model>/weights.pt`, or relative to `MODELS_ROOT` as `<model>/weights.pt`?

2. For YOLO11 registration, should backend require a specific metadata field or model-card evidence documenting fallback, or only store/report `model_family = YOLO11` accurately for now?

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
- `docs/CV_PIPELINE.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
