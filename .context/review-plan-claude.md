# Independent Planning Review - Phase 27

## Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 27 contract is mostly aligned with documented frontend/API/CV boundaries. Plan keeps work frontend-only, uses backend REST endpoints, preserves Ukrainian UI rules, avoids admin/global scope creep, and includes relevant unit/build gates.

Changes needed before implementation are verification and one implementation-detail hardening item: route protection coverage, authenticated preview/download behavior, and manual UI/download smoke.

## Blocking issues

None.

## Important issues

1. Authenticated media preview is not explicit enough in the numbered plan.
   - Evidence: `docs/API.md` says result downloads are protected and must validate ownership/admin before serving files. `docs/FRONTEND_UX.md` requires processed media preview and download buttons. `.context/design.md` correctly notes preview may need authenticated blob fetching, but `.context/plan.md` step 5 only says "media metadata and preview/download notice" and step 2 only covers authenticated download.
   - Risk: implementation may use direct `<img>`/`<video src>` against protected endpoints without `Authorization`, causing preview failure, or may be tempted to expose unsafe paths.
   - Required change: add an implementation step or acceptance check for authenticated blob preview URLs for image/video when preview is available, with object URL cleanup, and Ukrainian unavailable-preview fallback when browser preview cannot be provided.

2. Route protection test coverage is underspecified for the new routes.
   - Evidence: `docs/FRONTEND_UX.md` requires protected routes to redirect guests. `docs/TESTING_QA.md` frontend route tests explicitly include `/jobs` and `/jobs/:jobId`. `.context/plan.md` tests verify data rendering, filters, links, and details states, but not guest redirect/unauthenticated access for `/jobs` and `/jobs/:jobId`.
   - Risk: new route wiring in `App.tsx` could accidentally bypass existing guard.
   - Required change: either add focused tests for guest redirect on both new routes or explicitly verify existing protected-route tests cover these exact route entries after route rewiring.

3. Manual UI/download smoke is present in design but missing from execution steps.
   - Evidence: Phase 27 validation in `docs/phase.md` requires "Downloads work from UI." `docs/TESTING_QA.md` includes manual E2E download checks. `.context/design.md` lists manual browser smoke, but `.context/plan.md` steps 10-12 stop at lint/test/build.
   - Risk: authenticated blob downloads, video-preview fallback, table overflow, and polling transitions may pass unit tests but fail in browser.
   - Required change: add a tester step for manual browser smoke of `/jobs` and `/jobs/:jobId`, including completed, no-detection, failed, and processing states where fixtures/mocks make practical, plus download button behavior.

## Optional improvements

1. Clarify local filename search scope.
   - `.context/plan.md` allows client-side search on the loaded page. If pagination remains server-backed, label behavior clearly or omit search to avoid implying whole-history search.

2. Keep model filter conditional.
   - `.context/plan.md` already says model filter only if backed by `/models`. Preserve this during implementation; do not add inert/fake filter UI.

## Questions for resolution

None.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
