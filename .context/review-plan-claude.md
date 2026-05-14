# Phase 22 Planning Review

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan fits Phase 22 scope: training/backend integration helper, no frontend, no CV worker, no training launch, no schema/API changes unless proven needed. Main changes needed before implementation: tighten experiment slug conflict resolution, validate path-like metadata, and always run targeted backend API gates because helper depends on existing admin endpoints.

## Blocking issues

None.

## Important issues

1. Experiment type conflict resolution is too permissive.

   Evidence: `.context/research.md` reports conflict between `training/aerovision_training/schemas.py` / `training/templates/metrics.placeholder.json` and doc slugs. `docs/DATA_MODEL.md` requires `model_comparison`, `threshold_analysis`, `tracker_comparison`, `false_positive_analysis`; `docs/API.md` uses same experiment import contract. Plan step 3 allows "align template/schema identifiers ... or add a narrow mapper." Mapper alone can leave canonical training schema/templates doc-inconsistent.

   Required change: make backend-facing payloads, current templates, and validated canonical schema use doc slugs. Legacy mapper acceptable only as compatibility layer, with tests proving output slugs are `threshold_analysis` and `tracker_comparison`.

2. Path-safety scope misses metadata fields that can leak absolute paths.

   Evidence: `docs/API.md` says API must never expose unsafe absolute filesystem paths. `docs/AUTH_SECURITY.md` forbids exposing absolute host/container paths and sensitive paths in logs. `docs/TRAINING_EXPERIMENTS.md` requires model cards include `split_manifest` and metrics/report artifacts. Plan covers relative `weights_path` and `artifacts_path`, but not path-like values inside `metrics_json`, `config_json`, or `metadata_json`.

   Required change: add helper validation/tests for path-like artifact fields inside model cards and metrics artifacts before any backend mutation. Reject absolute paths, traversal, and cloud/local absolute path leaks in imported metadata, not only top-level DB path fields.

3. Backend gates should not be conditional on backend source changes.

   Evidence: Phase 22 validation requires "Valid model card registers a model version", "Valid experiment artifact imports run and metrics are queryable", and invalid/absolute paths reject. `docs/TESTING_QA.md` requires model registry and experiment authorization tests. Plan step 11 runs backend tests only if backend code/API behavior touched, but helper uses existing `POST /api/models`, `PATCH /api/models/{model_id}/activate`, and `POST /api/experiments/import`.

   Required change: always run targeted backend API tests for model registration, experiment import, and API contract in Phase 22, even if implementation only changes training helper code. Fake HTTP helper tests are useful but not enough for this phase.

## Optional improvements

- Add one CLI smoke test using placeholder model card and metrics template through mocked HTTP transport. It should verify route, method, headers redaction, and exact JSON payload shape.
- Add docs note that helper registers existing files under storage and never uploads `.pt` weights or starts training.

## Questions for resolution

- Should helper accept legacy `confidence_threshold_analysis` / `tracker_behavior_comparison` input as compatibility aliases after canonical templates are corrected, or reject them outright?

## Files consulted

- `C:\Users\Kotletka\.codex\skills\caveman\SKILL.md`
- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
