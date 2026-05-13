# Phase 10 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude planning review found no blocking issues. Accepted changes are applied to the Phase 10 `.context/` implementation contract only. No source code changed.

## Resolution table

| Review item | Resolution | Rationale | Contract update |
|---|---|---|---|
| Important 1: Phase 10 tests do not explicitly prove inactive users are rejected on new result/download routes | accepted | `docs/AUTH_SECURITY.md` requires inactive users be blocked from protected API routes, including result viewing and export downloads. | Updated `.context/research.md`, `.context/design.md`, and `.context/plan.md` to require inactive-user rejection tests for at least one representative result route and one download route. |
| Important 2: download association rule is underspecified for stored paths pointing outside requested job result area | accepted | `docs/API.md` requires file/resource association before serving. `docs/AUTH_SECURITY.md` forbids serving files without ownership and resource association. `docs/ARCHITECTURE.md` documents result artifacts under `results/{job_id}/`. | Updated `.context/research.md`, `.context/design.md`, and `.context/plan.md` to require selected job paths to live under `results/{job_id}/` for the requested job, in addition to authorization, relative-path validation, safe join, and file existence checks. |
| Optional 1: make `GET /api/jobs/{job_id}/result` availability semantics explicit | accepted | Explicit semantics prevent clients from treating a recorded DB path as downloadable when the file is missing. This stays within `docs/API.md` missing-file and safe-download rules. | Updated `.context/research.md`, `.context/design.md`, and `.context/plan.md` to define `available` as file-present availability after association and safe path checks. |
| Optional 2: add assertion that result/detail JSON never contains raw storage field names | accepted | `docs/API.md` requires logical references or download URLs instead of internal storage paths. Raw field names create easy regression surface. | Updated `.context/design.md` and `.context/plan.md` to assert JSON excludes `result_media_path`, `csv_path`, and `json_path`. |
| Question 1: exact download association rule | accepted | Resolved from product docs, no user decision needed. | Chosen rule: selected result/export path must come from the authorized job row and live under `results/{job_id}/` for the requested job. |
| Question 2: `available` means DB path present or file exists on disk | accepted | File-present semantics are safer for download UI/API behavior and align with missing-file handling. | Chosen rule: `available` means path recorded, associated with the job, safely resolved under `STORAGE_ROOT`, and file exists on disk. |

## Accepted changes applied

- Inactive-user tests required for representative Phase 10 result and download routes.
- Download association now requires `results/{job_id}/` path namespace for the requested job.
- Download helper must reject wrong-job result directories even if the stored path is relative and safe-joined under `STORAGE_ROOT`.
- Result metadata availability now means file exists and can be safely downloaded now.
- Result/detail JSON must not expose raw storage field names `result_media_path`, `csv_path`, or `json_path`.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

- `.context/research.md`: updated for job-specific result namespace, file-present availability, and inactive-user test requirement.
- `.context/design.md`: updated for result/download association, availability semantics, raw storage field-name assertions, and inactive-user route coverage.
- `.context/plan.md`: updated with concrete test and implementation requirements for accepted items.
- Final Phase 10 implementation contract remains scoped to backend jobs/results/detections/tracks/download APIs only.
- Verdict: READY_FOR_IMPLEMENTATION.
