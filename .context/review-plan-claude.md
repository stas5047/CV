# Phase 29 Planning Review

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches main Phase 29 contract: protected `/experiments`, existing backend REST API, Recharts, Ukrainian UI, prototype used as visual reference only, backend remains visibility authority, no training launch, no forbidden tracker metrics. Changes needed before implementation: make FPS/latency chart explicit, tighten confusion-matrix artifact handling, and avoid copying wrong empty-state literal from `.context/design.md`.

## Blocking issues

None.

## Important issues

1. Missing explicit FPS/latency chart implementation step.
   - Evidence: `docs/phase.md` and `docs/FRONTEND_UX.md` require an FPS/latency chart for `/experiments`.
   - Evidence: `.context/plan.md` step 4 names model comparison, threshold analysis, tracker behavior, false-positive summary, metric cards, and optional confusion matrix, but does not name an FPS/latency chart.
   - Risk: implementation may satisfy metric cards/table only and miss required chart surface.
   - Required change: add explicit FPS/latency chart component and test: chart renders when data exists; exact experiment empty state renders when data missing.

2. Confusion matrix artifact handling under-specified.
   - Evidence: `docs/FRONTEND_UX.md` requires confusion matrix image if available.
   - Evidence: `docs/API.md` requires no unsafe absolute paths in API responses/UI and file access through safe routes.
   - Evidence: `.context/research.md` says current API exposes `artifacts_path`, but no documented safe frontend image/download URL exists for experiment artifacts.
   - Risk: implementation may use or display `artifacts_path` directly, causing broken image src, internal path exposure, or path-bound frontend behavior.
   - Required change: render confusion matrix only from a documented safe URL or safe metadata field; otherwise show required empty state. Test must assert no raw `artifacts_path`, `/app/storage`, `C:\`, or storage-relative path is shown or used as image src.

3. WARNING: CONFLICT: empty-state literal differs between `.context/design.md` and docs.
   - Evidence: `docs/phase.md`, `docs/FRONTEND_UX.md`, and `docs/TESTING_QA.md` require exact text `Р”Р°РЅС– РµРєСЃРїРµСЂРёРјРµРЅС‚Сѓ С‰Рµ РЅРµ Р·Р°РІР°РЅС‚Р°Р¶РµРЅРѕ`.
   - Evidence: `.context/design.md` quotes a different double-encoded string beginning `Р вЂќР В°...`.
   - Risk: implementer copying from design will fail required exact-text checks.
   - Required change: implementation and tests must copy empty-state literal from product docs, not from `.context/design.md`.

## Optional improvements

- Add a focused visual smoke check against `prototype/experiments.jsx` after build, limited to layout structure: tabs, comparison split, threshold chart/table, tracker table, false-positive section, and empty state. Do not treat prototype mock metrics as contract.
- Add case-insensitive text assertions for forbidden tracker terms: `MOTA`, `IDF1`, `HOTA`, `tracking accuracy`, `targeting`, `navigation`, `interception`, plus Ukrainian equivalents if implementation introduces them.

## Questions for resolution

- Should confusion matrix display be deferred until backend/API exposes a safe experiment artifact URL, with required empty state shown meanwhile?

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
- `docs/TESTING_QA.md`
- `prototype/index.md`
- `prototype/experiments.jsx`
