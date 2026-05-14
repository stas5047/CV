# Phase 25 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review verdict was `APPROVED_WITH_CHANGES`. All review items were resolved. No item needs user decision and no product-doc conflict was found.

## Resolution table

| ID | Claude item | Resolution | Rationale | Applied updates |
|---|---|---|---|---|
| I1 | Dashboard metric derivation is under-specified and can misrepresent required stats. | accepted | `docs/FRONTEND_UX.md` requires processed files, detections, average confidence, and average FPS. Existing admin stats exposes count stats, not confidence/FPS averages. Plan must prevent invented totals or averages. | `.context/research.md`, `.context/design.md`, `.context/plan.md` |
| I2 | Prototype visual verification is conditional even though phase is prototype-driven. | accepted | User instruction requires frontend built from `@prototype`; browser smoke is necessary unless tooling is truly unavailable. | `.context/research.md`, `.context/design.md`, `.context/plan.md` |
| O1 | Add assertion that active model UI does not display `weights_path` or storage-like paths. | accepted | Model API includes `weights_path`; docs forbid exposing filesystem paths. Dashboard only needs display metadata. | `.context/research.md`, `.context/design.md`, `.context/plan.md` |
| O2 | Add assertion that regular-user dashboard code does not call `/api/admin/*`. | accepted | Backend remains authorization authority, but frontend must not intentionally fetch admin routes for regular users. | `.context/design.md`, `.context/plan.md` |

## Accepted changes applied

- Added metric derivation contract:
  - `total processed files` means completed jobs only.
  - Admin total detections may use `GET /api/admin/stats`.
  - Regular-user detections may use completed visible job summaries when numeric data exists.
  - Average confidence and average FPS must come only from available completed-job `summary_json` numeric values.
  - Missing derivable values render Ukrainian unavailable placeholders.
  - Limited recent admin rows must not be used to invent global averages.
- Made manual browser/prototype verification required unless dev-server or browser tooling is genuinely unavailable; exact blocker must be recorded if skipped.
- Added dashboard rule to avoid displaying `weights_path` or storage-like paths.
- Added dashboard test/review rule that regular-user fetch logic must not call `/api/admin/*`.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

Phase 25 implementation contract is ready and remains scoped to frontend dashboard/authenticated shell only. No backend, database, CV worker, training, Docker, route-contract, or product-doc changes are authorized by this resolution.
