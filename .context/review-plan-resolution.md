# Phase 8 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review found no blocking issues. Accepted items are applied to the Phase 8 `.context/` contract only. No source code changed.

## Resolution table

| Review item | Resolution | Rationale | Contract update |
|---|---|---|---|
| Important 1: inactive-user access not tested for model endpoints | accepted | `docs/AUTH_SECURITY.md` requires inactive users to be blocked from protected API routes; model endpoints are protected in `docs/API.md`. | Added inactive-user model endpoint tests to `.context/design.md` and `.context/plan.md`. |
| Important 2: `weights_path` accepted/storage form ambiguous | accepted | `docs/DATA_MODEL.md` says first implementation registers existing relative paths under `STORAGE_ROOT/models`; current schema tests already use `models/...`. | Chose canonical `weights_path` form `models/.../weights.pt`, relative to `STORAGE_ROOT`, with resolved-file check under `MODELS_ROOT`. Updated `.context/research.md`, `.context/design.md`, `.context/plan.md`. |
| Important 3: YOLO11 fallback test too weak | accepted | Docs require YOLO11 to be represented as documented fallback and actual model family recorded. Product docs do not define a required fallback-evidence field for Phase 8. | Added contract to store/report `model_family = YOLO11` accurately and preserve supplied fallback metadata; no invented mandatory field. Updated `.context/research.md`, `.context/design.md`, `.context/plan.md`. |
| Optional 1: list-response shape test for pagination/filter parameters | rejected | `docs/API.md` recommends filters/pagination but does not define exact Phase 8 shape. Existing plan already allows practical filters. Adding mandatory pagination shape would expand contract beyond current docs. | No change. |
| Optional 2: explicit response assertion for no absolute storage/model root | duplicate | Existing plan already requires no absolute path in response body. | No new change beyond existing test contract. |
| Question 1: store `weights_path` relative to `STORAGE_ROOT` or `MODELS_ROOT` | accepted | Resolved without user decision from `docs/DATA_MODEL.md` first-implementation wording and existing tests. | Canonical API/db value is `models/<model>/weights.pt`, relative to `STORAGE_ROOT`; service verifies file is inside `MODELS_ROOT`. |
| Question 2: require specific YOLO11 fallback metadata field or store/report actual family only | accepted | Requiring a new specific field would invent API behavior absent from product docs. | Phase 8 stores/reports `model_family = YOLO11` and preserves supplied fallback metadata, but does not require a new field. |

## Accepted changes applied

- Added inactive-account coverage requirement for model endpoints.
- Fixed `weights_path` contract:
  - API/db value: `models/.../weights.pt`;
  - relative to `STORAGE_ROOT`;
  - resolved file must be under `MODELS_ROOT`;
  - absolute, traversal, outside-model-root, empty, and missing paths rejected.
- Strengthened YOLO11 fallback contract:
  - response must show `model_family = YOLO11`;
  - supplied fallback documentation metadata must be preserved;
  - Phase 8 does not invent new required metadata fields.

## Rejected items

- Mandatory pagination/list-response shape test for Phase 8 model list.
  - Reason: recommended by API docs, but exact response shape is not specified and would broaden this phase. Filters remain allowed when practical.

## Duplicate items

- Explicit no-absolute-path response assertion.
  - Already present in `.context/plan.md` test list and `.context/design.md` security/test strategy.

## Items needing user decision

- None.

## Final contract status

- `.context/research.md`: updated for canonical model path and YOLO11 fallback handling.
- `.context/design.md`: updated for path root, inactive-user tests, YOLO11 metadata preservation, and resolved ambiguity.
- `.context/plan.md`: updated with concrete accepted test/implementation requirements.
- Final Phase 8 implementation contract remains backend model registry API only.
- Verdict: READY_FOR_IMPLEMENTATION.
