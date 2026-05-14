# Phase 23 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review is resolved. Accepted items were applied only to Phase 23 planning contract. No source code changed.

## Resolution table

| ID | Claude item | Resolution | Reason | Applied to |
|---|---|---|---|---|
| I1 | Clean integration environment is under-specified. | accepted | `docs/phase.md` and `docs/ROADMAP.md` require clean database and shared storage. | `.context/design.md`, `.context/plan.md` |
| I2 | Ownership smoke misses named result subroutes. | accepted | `docs/API.md` and `docs/AUTH_SECURITY.md` require ownership on summary, detections, tracks, result metadata, and all downloads. | `.context/design.md`, `.context/plan.md` |
| I3 | No-detection smoke does not verify annotated media download. | accepted | `docs/CV_PIPELINE.md` says no-detection jobs still create annotated output media when possible. | `.context/design.md`, `.context/plan.md` |
| O1 | Fake-model strategy should state what is still real. | accepted | Clarifies deterministic smoke without weakening backend-route, DB-queue, worker-write, export, and download coverage. | `.context/design.md`, `.context/plan.md` |
| O2 | Failed-job smoke should check API and storage safety. | accepted | Consistent with API/security rules forbidding stack traces and unsafe absolute paths in API responses. | `.context/design.md`, `.context/plan.md` |
| Q1 | Risk level placeholder not resolved by user. | duplicate | `.context/research.md` already treats Phase 23 as high integration risk. No contract change needed. | none |
| Q2 | Docker-backed smoke vs pytest smoke. | accepted | Contract now says pytest smoke is sufficient when it uses real backend routes, PostgreSQL, isolated shared storage, and worker polling; Docker real-inference smoke remains optional/manual when model weights exist. | `.context/design.md`, `.context/plan.md` |

## Accepted changes applied

- Added clean integration environment requirement: isolated test database/schema and isolated temp/shared storage, or exact blocker if unavailable.
- Expanded ownership smoke to job detail, summary, detections, tracks, result metadata, annotated media download, CSV download, and JSON download.
- Added no-detection annotated media result/download assertion when output creation is possible, with blocker requirement when codec/image writer prevents it.
- Clarified fake-model boundary: only inference output may be faked; backend routes, DB queue rows, worker dispatch/write path, storage writes, exports, and downloads stay real.
- Strengthened failed-job safety checks: no stack traces or absolute paths in API payloads.
- Clarified Docker-backed real-inference smoke is not required without valid model weights if pytest smoke covers real backend routes, PostgreSQL, isolated shared storage, and worker polling.

## Rejected items

None.

## Duplicate items

- Risk level placeholder question. Existing research already classifies Phase 23 as high integration risk.

## Items needing user decision

None.

## Final contract status

- `.context/research.md`: unchanged; existing high-risk assumption remains valid.
- `.context/design.md`: updated for accepted review items.
- `.context/plan.md`: updated for accepted review items.
- Product docs: unchanged.
- Source code: unchanged.
- Phase scope: still Phase 23 only.

Implementation may proceed under updated `.context/design.md` and `.context/plan.md`.
