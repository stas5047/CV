# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 9 plan matches core docs: backend-only `POST /api/jobs`, authenticated job creation for own non-deleted media, queued status, no synchronous media processing, model priority resolution, `ACTIVE_MODEL_ID` fallback limits, internal `frame_stride = 1`, and focused backend tests.

No blocking issue found. One important correction needed before implementation: make tracker validation media-type-aware and test it.

## Blocking issues

None.

## Important issues

1. Tracker validation is not media-type-specific in plan.
   - Evidence: `docs/API.md:279` says `tracker_type` is user-configurable for video. `docs/CV_PIPELINE.md:154` says tracker type is user-facing for video. `docs/CV_PIPELINE.md:233-235` defines ByteTrack/BoT-SORT for video jobs. `docs/AUTH_SECURITY.md:291` requires tracker type be allowed for the media type. `.context/plan.md` steps 5 and 7 validate unknown tracker values and store a tracker default, but do not define image-job behavior when a client sends `tracker_type`.
   - Risk: image jobs may accept and persist video-only tracker choices, creating confusing worker input and drifting from documented parameter boundaries.
   - Required change: before implementation, define Phase 9 behavior for image requests with client-supplied `tracker_type` and add tests. Conservative options: reject `tracker_type` for image media, or accept only default/ignore client value while still storing internal default. Whichever behavior is chosen must ensure user input cannot make image jobs behave as tracked video jobs.

## Optional improvements

1. Add one response-shape assertion that job creation response contains no filesystem path-looking fields.
   - Evidence: `docs/API.md:30-31` and `docs/API.md:54` forbid unsafe absolute paths and require only relative/logical file references or download URLs. Phase 9 should not return result paths yet, so this is low-cost regression coverage.

2. Make inactive-model policy explicit in implementation notes or tests.
   - Evidence: `docs/TESTING_QA.md:194` says inactive model selection is allowed only if intended by API policy. `.context/design.md` assumes explicit `model_version_id` may reference inactive registered models because `is_active` controls default selection. This is reasonable, but should be visible in tests so future reviewers know it is intentional.

## Questions for resolution

1. For image media, should `POST /api/jobs` reject client-supplied `tracker_type`, or ignore it and store internal default `bytetrack` without treating it as user-controlled behavior?

2. Is explicit selection of inactive registered model versions intended API policy for Phase 9? Current plan assumes yes.

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
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
