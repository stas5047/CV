# Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 23 direction: backend-worker integration smoke only, no frontend/schema/API/product behavior. Main architecture boundary is respected: backend API creates jobs, worker processes through PostgreSQL/shared storage, backend serves results/downloads.

Changes needed before implementation: make clean DB/shared-storage smoke explicit, expand ownership checks to all result subroutes, and verify no-detection annotated media download when worker can create it.

## Blocking issues

None.

## Important issues

1. Clean integration environment is under-specified.
   - Evidence: `docs/phase.md` scope says "Run clean database and shared storage with backend and worker."
   - Plan evidence: steps 2 and 16 cover Compose config and a new smoke command, but no explicit clean database/shared-storage setup or teardown contract for the smoke harness.
   - Risk: smoke can pass against dirty local state, stale result files, or pre-existing model/job rows. Add explicit clean test database/schema and isolated temp/shared storage setup for automated smoke, or document exact Docker/local blocker.

2. Ownership smoke misses named result subroutes.
   - Evidence: `AUTH_SECURITY.md` says ownership checks apply to summaries, detections, tracks, annotated media downloads, CSV downloads, JSON downloads. `API.md` lists result endpoints: summary, detections, tracks, result metadata, media download, CSV download, JSON download.
   - Plan evidence: step 11 says "second user attempts job detail/result/download" and "all cross-owner result/detail/download requests"; it does not explicitly include `/summary`, `/detections`, and `/tracks`.
   - Risk: protected result data could leak even if main detail/download endpoints pass. Add explicit cross-owner checks for job detail, summary, detections, tracks, result metadata, media download, CSV download, and JSON download.

3. No-detection smoke does not verify annotated media download.
   - Evidence: `CV_PIPELINE.md` says no-detection jobs still create annotated output media when possible. `API.md` says completed no-detection jobs must keep CSV and JSON downloads, and result downloads serve annotated output media.
   - Plan evidence: step 9 verifies completed status, zero detections, CSV headers, and JSON empty detections, but not annotated media/result media availability.
   - Risk: no-detection flow can pass exports while breaking user-visible annotated output/download behavior. Add media result/download assertion when output creation is possible; document exact blocker if codec/image writer prevents it.

## Optional improvements

1. Step 7 fake-model strategy should state what is still real.
   - Keep fake model acceptable for deterministic automated smoke, but require real backend routes, real DB queue rows, real worker dispatch/write path, real export/download checks. This prevents a mock-heavy smoke from bypassing integration risk.

2. Failed-job smoke can be stronger if it checks both API and storage safety.
   - Current plan checks safe status/error. Also assert no absolute path or stack trace in job detail/result payload for missing-model/corrupt-media failures.

## Questions for resolution

1. Risk level placeholder was not resolved by user (`<MEDIUM | HIGH>`). Review treats Phase 23 as high risk because it spans backend API, PostgreSQL queue, shared storage, worker processing, downloads, ownership, and local model availability.

2. Should implementation require a Docker-backed smoke for Phase 23, or is a pytest smoke with real backend routes, PostgreSQL, shared storage, and worker `run_poll_iteration()` enough when real model weights are unavailable?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
