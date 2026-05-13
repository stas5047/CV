# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 10 planning contract matches docs in main shape: backend-only jobs/results/download API, ownership/admin checks, safe downloads, soft deletion, no-detection success behavior, CV-only outputs, and focused backend/security tests.

No blocking issue found. Two important changes should be made before implementation: prove inactive users cannot use the new result/download routes, and tighten download association beyond trusting a stored job path alone.

Risk level placeholder was not filled in the prompt. Treated as HIGH because this phase exposes protected result data and file downloads.

## Blocking issues

None.

## Important issues

1. Phase 10 tests do not explicitly prove inactive users are rejected on the new job/result/download routes.
   - Evidence: `docs/AUTH_SECURITY.md` Account Activity says inactive users must not upload, create jobs, view results, download exports, or access authenticated endpoints. Ownership checks list summaries, detections, tracks, and downloads. `.context/design.md` includes inactive-user route tests, but `.context/plan.md` step 3 omits inactive-user cases for Phase 10 endpoints and step 17 only runs existing auth/security regression tests.
   - Risk: a new route could accidentally depend on token validity only, bypass active-account enforcement for result metadata or file downloads.
   - Required change: add at least one focused Phase 10 inactive-user test covering a representative result route and a download route, or explicitly apply the same active-user dependency across every route and assert it through parametrized tests.

2. Download association rule is underspecified for stored paths that point outside the requested job's own result area.
   - Evidence: `docs/API.md` Download and File Serving Rules require the API to ensure the requested file belongs to the requested job/resource. `docs/AUTH_SECURITY.md` Path Traversal Prevention requires serving files only after verifying ownership and resource association. `.context/design.md` says association means the path is read from the authorized `processing_jobs` row. `.context/plan.md` step 13 validates relative path and safe-joins under `STORAGE_ROOT`, but does not require a job-specific result namespace/prefix check or another association proof.
   - Risk: if a worker bug or bad seed/test row stores `results/other-job/export.csv` on this job row, an authorized user could download a file not produced for that job. Safe-join prevents traversal, but not cross-job file association drift.
   - Required change: define and test a concrete association rule for Phase 10 downloads, such as requiring result paths to live under a generated job-specific directory containing the `job_id`, or another documented predicate that rejects a path associated with another job.

## Optional improvements

1. Make `GET /api/jobs/{job_id}/result` availability semantics explicit.
   - Evidence: `.context/plan.md` step 12 says metadata may not require files to exist. That is acceptable if fields mean "DB path present", but unclear if fields mean "download is currently available".
   - Low-risk improvement: name fields so clients can distinguish path-recorded vs file-present, or check file existence for availability without exposing paths.

2. Add one assertion that result/detail JSON never contains raw storage field names.
   - Evidence: `docs/API.md` forbids unsafe absolute paths and asks for download URLs or logical references instead of internal paths. Plan already covers path secrecy; checking raw names like `result_media_path`, `csv_path`, and `json_path` would make regression obvious.

## Questions for resolution

1. What exact download association rule should implementation enforce: job-specific result directory/prefix, `job_id` embedded in generated path, or another predicate?

2. Should result metadata `available` mean the DB path exists on the job row, or the file exists on disk and can be downloaded now?

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
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`
