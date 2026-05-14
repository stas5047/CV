# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 17 plan matches image-processing scope and key docs: worker-only image path, shared-storage reads/writes, YOLO inference through existing runtime, original-pixel boxes, image detection invariants, no-detection success, CSV/JSON exports, and relative result paths.

Changes needed before implementation: remove risky valid-video failure option, add required summary fields, and add tests for output/export failure handling.

## Blocking issues

None.

## Important issues

1. Valid video jobs may be marked failed during image-only phase.

Evidence: `.context/plan.md` step 8 says non-image jobs may be rejected with safe failed status. `docs/CV_PIPELINE.md` defines video as supported runtime input and has separate video processing flow. `docs/API.md` allows jobs for uploaded image or video media. `docs/phase.md` scopes Phase 17 to image processing only, not changing valid video-job semantics. Failing a valid queued video job because Phase 17 image implementation claimed it would create false processing failures. Plan should require image-only claiming/filtering or explicit deferral behavior that does not convert valid future video work into failed processing errors.

2. Summary metric plan omits available required fields.

Evidence: `.context/plan.md` step 16 lists summary values but omits `original_filename`, source file size, and model size MB. `docs/CV_PIPELINE.md` Processing Summary Metrics requires original filename, file size, and model size MB when available. `docs/DATA_MODEL.md` stores `media_files.original_filename`, `media_files.file_size_bytes`, and `model_versions` metadata/weights path needed to calculate or source these values. Add these to implementation and tests, with model size nullable only when not available.

3. Failure tests do not cover output/export write failures.

Evidence: `.context/plan.md` step 6 covers missing and corrupted inputs only. `docs/CV_PIPELINE.md` CV Runtime Error Handling explicitly requires handling failed output media creation, failed CSV export creation, and failed JSON export creation. Since Phase 17 creates annotated image, CSV, and JSON artifacts, plan needs relevant mocked failure tests or a documented reason a specific failure cannot be simulated.

## Optional improvements

1. Add assertion that completed/failed finalization updates `updated_at` if this is not already handled by SQLAlchemy/server defaults. `docs/DATA_MODEL.md` defines `processing_jobs.updated_at` as last update timestamp.

2. In retry cleanup, consider job-scoped stale result-file cleanup or overwrite behavior. `.context/plan.md` step 17 handles duplicate detection rows/result refs, but stale artifact files can still accumulate. This is optional because docs require safe storage cleanup later, not immediate physical deletion.

## Questions for resolution

1. For Phase 17, should worker queue selection skip non-image jobs until video phase, or should non-image jobs remain queued with a safe "not processed by this phase" behavior? Plan should pick one non-failing behavior before coding.

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
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`
- `git status --short`
