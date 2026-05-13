# Phase 9 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review found no blocking issues. Accepted changes are applied to the Phase 9 `.context/` implementation contract only. No source code changed.

## Resolution table

| Review item | Resolution | Rationale | Contract update |
|---|---|---|---|
| Important 1: tracker validation is not media-type-specific | accepted | `docs/API.md` and `docs/CV_PIPELINE.md` make `tracker_type` user-configurable for video. `docs/AUTH_SECURITY.md` requires tracker type be allowed for the media type. | Updated `.context/research.md`, `.context/design.md`, and `.context/plan.md` to reject client-supplied `tracker_type` for image media and test video-only tracker selection. |
| Optional 1: response-shape assertion for no filesystem path-looking fields | accepted | Phase 9 create response does not need result/download paths, and `docs/API.md` forbids unsafe absolute paths. | Updated `.context/design.md` and `.context/plan.md` to exclude result/export path fields from create response and assert response path safety. |
| Optional 2: make inactive-model policy explicit | accepted | `docs/CV_PIPELINE.md` prioritizes job-specific model selection, and docs use `is_active` for default selection. `docs/TESTING_QA.md` allows inactive selection when intended by API policy. | Updated `.context/research.md`, `.context/design.md`, and `.context/plan.md` to state explicit inactive registered model selection is intended Phase 9 API policy and must be tested. |
| Question 1: image `tracker_type` behavior | accepted | Resolved from product docs: tracker selection is user-facing for video only; image jobs must not behave like tracked video jobs. | Chosen behavior: reject any client-supplied `tracker_type` for image media. |
| Question 2: explicit inactive model selection | accepted | Resolved from product docs: explicit job-specific model selection is separate from active default model selection. | Chosen behavior: allow explicit selection of any existing registered model, including inactive registered models. |

## Accepted changes applied

- Image media requests with client-supplied `tracker_type` are rejected.
- Video media may omit `tracker_type` and receive default `bytetrack`.
- Unknown or unsupported tracker values are rejected.
- Phase 9 create response excludes result/export path fields and must not expose absolute paths or path-like result fields.
- Explicit `model_version_id` may select an inactive registered model version by intended Phase 9 API policy.
- Tests must cover media-type-aware tracker validation, response path safety, and explicit inactive model selection.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

- `.context/research.md`: updated for media-type-aware tracker policy and explicit inactive-model policy.
- `.context/design.md`: updated for image tracker rejection, response path-field exclusion, and inactive-model policy.
- `.context/plan.md`: updated with concrete test and implementation requirements for accepted items.
- Final Phase 9 implementation contract remains scoped to `POST /api/jobs` and backend model-selection resolution only.
- Verdict: READY_FOR_IMPLEMENTATION.
