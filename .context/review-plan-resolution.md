# Planning Review Resolution - Phase 17 Image Processing Pipeline

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review was evaluated against `docs/CV_PIPELINE.md`, `docs/DATA_MODEL.md`, `docs/API.md`, `docs/TESTING_QA.md`, `docs/phase.md`, and existing Phase 17 `.context` contract files.

No source code changes are authorized by this resolution. Accepted items update only the Phase 17 implementation contract.

## Resolution table

| ID | Claude item | Resolution | Reason | Applied to |
|---|---|---|---|---|
| IMPORTANT-1 | Valid video jobs may be marked failed during image-only phase. | accepted | Product docs support video jobs, but Phase 17 is image-only. Valid video jobs must not become failed only because video processing is later-phase work. | `.context/design.md`, `.context/plan.md`, `.context/research.md` |
| IMPORTANT-2 | Summary metric plan omits `original_filename`, source file size, and model size MB. | accepted | `docs/CV_PIPELINE.md` requires these summary metrics when available. Data is available from `media_files` and model metadata/weights path where practical. | `.context/design.md`, `.context/plan.md`, `.context/research.md` |
| IMPORTANT-3 | Failure tests do not cover output media, CSV, or JSON creation failures. | accepted | `docs/CV_PIPELINE.md` requires safe handling for failed output media creation and failed CSV/JSON export creation. | `.context/design.md`, `.context/plan.md` |
| OPTIONAL-1 | Add assertion/finalization handling for `updated_at`. | accepted | `docs/DATA_MODEL.md` defines `processing_jobs.updated_at` as last update timestamp. Phase 17 finalization should preserve this contract through existing DB mechanism or explicit update. | `.context/plan.md` |
| OPTIONAL-2 | Clean up stale result files on retry. | rejected | Physical stale artifact cleanup is not required by Phase 17 docs and can expand scope. Job-scoped DB/result-reference cleanup remains required to avoid duplicate rows/refs. Later safe storage cleanup remains documented admin/runtime work. | none |
| QUESTION-1 | Should non-image jobs be skipped or left queued instead of failed? | duplicate | Resolved by IMPORTANT-1. Final contract: Phase 17 must not fail valid video jobs; implementation should claim/filter image jobs only where practical, leaving video jobs queued for later video phase. | `.context/design.md`, `.context/plan.md` |

## Accepted changes applied

- Phase 17 contract now requires non-image/video jobs to avoid false failure during image-only implementation.
- Plan now prefers image-only worker claiming/filtering; valid video jobs remain queued for later video phase where practical.
- Plan now forbids marking valid video jobs failed only because Phase 17 does not implement video processing.
- Summary contract now includes sanitized original filename, source file size, and model size MB when available.
- Tests now include output media write failure, CSV export write failure, and JSON export write failure or a documented reason if a specific failure cannot be simulated.
- Completion/failure finalization now must keep `processing_jobs.updated_at` correct through existing DB behavior or explicit update, with assertion where practical.

## Rejected items

- OPTIONAL-2: physical cleanup of stale result files on retry. Rejected as phase creep. Phase 17 still must avoid duplicate DB detections/result references for job-scoped retry behavior.

## Duplicate items

- QUESTION-1 duplicates IMPORTANT-1 after choosing image-only queue filtering / non-failing deferral.

## Items needing user decision

None.

## Final contract status

Phase 17 implementation contract is ready.

Scope remains worker-only image processing:

- no backend API changes;
- no database schema/migration changes;
- no frontend changes;
- no video/tracking implementation;
- no training utilities;
- no new runtime service;
- no CV output beyond image-space detection data;
- no source code changes during planning review resolution.
