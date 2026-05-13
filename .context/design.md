# Phase 10 Design

## Phase goal

Implement Phase 10 only: backend job history, job details, result metadata, detections, tracks, summary, and safe download endpoints.

Required result:

- authenticated users can list/view own jobs and results;
- admins can view all jobs/results through the same documented permissions or admin-visible filters;
- every result and download route enforces ownership or admin access;
- job lists hide soft-deleted jobs from normal user lists;
- downloads serve only files referenced by the requested job, under that job's documented result directory, and never expose absolute paths;
- no-detection completed jobs remain successful with empty detection/track data and downloadable CSV/JSON when files exist.

## Intended behavior from docs

Confirmed:

- Endpoints in scope:
  - `GET /api/jobs`
  - `GET /api/jobs/{job_id}`
  - `DELETE /api/jobs/{job_id}`
  - `GET /api/jobs/{job_id}/summary`
  - `GET /api/jobs/{job_id}/detections`
  - `GET /api/jobs/{job_id}/tracks`
  - `GET /api/jobs/{job_id}/result`
  - `GET /api/jobs/{job_id}/download/media`
  - `GET /api/jobs/{job_id}/download/csv`
  - `GET /api/jobs/{job_id}/download/json`
- All endpoints are protected by JWT and active-account checks.
- Regular users can access only own jobs, results, detections, tracks, and downloads.
- Admins can access all jobs/results where admin permissions allow it.
- Job list supports pagination and filters.
- Soft-deleted jobs are hidden from normal user lists.
- Job detail returns status, progress, heartbeat, timestamps, summary, and safe result/download references.
- Result endpoints must not expose unsafe absolute filesystem paths.
- Downloads require ownership/admin access and must verify file association with requested job.
- Missing result files return clear errors without internal paths.
- No-detection completed jobs are successful results, not errors.
- CSV export contains one row per detection; no-detection CSV has headers only.
- JSON export contains job, media, model, parameters, summary, detections, and tracks.
- API/export outputs stay inside CV-only boundary.

Assumptions:

- Existing `POST /api/jobs` response can remain compatible; Phase 10 may extend job schemas for list/detail/result responses if needed.
- Result metadata response can expose booleans and safe download endpoint URLs/references, not stored relative paths.
- Result metadata `available` means the job path is recorded, passes the job-specific association rule, resolves safely under `STORAGE_ROOT`, and exists as a file on disk.
- Download association requires the selected path to come from the authorized job row and live under `results/{job_id}/` for the requested job, matching `docs/ARCHITECTURE.md` artifact layout.
- Download filenames should use sanitized media/job/model context and safe extensions; exact filename text is not specified by docs.
- Detections response should include derived values `center_x`, `center_y`, `bbox_width`, and `bbox_height` calculated from stored bbox corners.
- Admin owner filter on `GET /api/jobs` is allowed because docs list owner filtering for admins; regular users cannot broaden visibility with owner filters.
- DELETE behavior should be conservative: queued jobs can be cancelled and soft-deleted; completed/failed/cancelled jobs can be soft-deleted; processing jobs are soft-deleted or marked for hidden visibility without requiring worker interruption. Exact implementation should stay within docs and tests.

## Architecture decisions

- Keep route handlers thin in `backend/app/api/jobs.py`.
- Put job visibility, filtering, result shaping, soft deletion/cancellation, and download lookup in service/domain helpers.
- Use existing ORM models; no new database fields planned.
- Use `ensure_owner_or_admin` or equivalent safe not-found behavior for every job-derived resource.
- Query detections and tracks by `job_id` only after authorized job lookup.
- Compute derived bbox values in API/service response shaping, not database.
- Build result/download metadata from job row fields and existing API endpoint routes; do not expose `result_media_path`, `csv_path`, or `json_path` directly.
- Assert response bodies do not contain raw storage field names such as `result_media_path`, `csv_path`, or `json_path`.
- Use `safe_join_storage_path(settings.storage_root, relative_path)` before file serving.
- Before serving, require the selected relative path to match the requested job's result namespace: `results/{job_id}/...`.
- Use `safe_download_filename` for `Content-Disposition` filenames.
- Use FastAPI file response support for downloads after association and existence checks pass.
- Do not implement worker export generation, CV processing, frontend pages, experiments, admin dashboard, or storage cleanup.

## Backend impact

Touched:

- Jobs API module for list/detail/delete/result/download routes.
- Jobs service module or a new result service module.
- Jobs/result schemas.
- Jobs API tests and possibly dedicated result/download tests.
- Backend index if file inventory changes.

Not touched:

- Auth implementation.
- Media upload validation.
- Model registry mutation behavior.
- CV worker queue claiming or export generation.
- Frontend.
- Product docs.
- Database migration unless a verified schema mismatch blocks implementation.

## API impact

Implemented endpoints:

- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `DELETE /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/summary`
- `GET /api/jobs/{job_id}/detections`
- `GET /api/jobs/{job_id}/tracks`
- `GET /api/jobs/{job_id}/result`
- `GET /api/jobs/{job_id}/download/media`
- `GET /api/jobs/{job_id}/download/csv`
- `GET /api/jobs/{job_id}/download/json`

Access:

- Guest: 401.
- Inactive user: 401.
- Regular user: own jobs only.
- Admin: all jobs/results allowed by documented permissions.
- Cross-owner/missing/hidden resource: safe not-found behavior.

List filters:

- Pagination: `limit`, `offset`, same backend style as media/models.
- Phase filters from docs when practical: status, media type, date, model version, owner for admins.
- Invalid filter values reject with clear 422/400 behavior.

Responses:

- Job detail includes job ids, status, progress, heartbeat/lock-safe timestamps, input params, summary, error message, created/updated/start/completion timestamps, media/model references where useful.
- Result metadata includes safe file-present availability and download references for annotated media, CSV, and JSON.
- Detection rows include stored fields plus derived center/size values.
- Track rows include documented track summary fields.
- No response includes absolute filesystem paths, password hashes, tokens, secrets, or forbidden CV outputs.

## Database impact

- Use existing tables only:
  - `processing_jobs`
  - `media_files`
  - `detections`
  - `tracks`
  - `model_versions`
- Normal user list filters `processing_jobs.deleted_at IS NULL`.
- Soft-delete/cancel sets documented status/deletion fields without physical file removal.
- Download association uses paths already stored on the authorized `processing_jobs` row plus the documented `results/{job_id}/` path namespace.
- No media/result/export binaries stored in PostgreSQL.

## Frontend impact

- No frontend source changes in this phase.
- Future frontend job pages can consume this backend API.
- API response text remains developer/API English; future visible UI Ukrainian is frontend responsibility.

## Security/privacy impact

Touched:

- Protected result/detail/download access.
- Ownership/admin checks for every job-derived endpoint.
- Safe missing/cross-owner responses.
- Path traversal prevention during download resolution.
- No absolute storage paths in JSON.
- No secrets/tokens/password data in responses or logs.
- File serving only after job association and existence verification.

Security invariant:

- Result/download endpoints must re-check authorization even if job id was obtained elsewhere.

## Test strategy

Relevant automated checks:

- From `backend/`: `python -m pytest tests/test_jobs_api.py`
- From `backend/`: `python -m pytest tests/test_media_api.py tests/test_auth.py tests/test_security_utils.py`
- From `backend/`: `python -m ruff check .`

Required Phase 10 test cases:

- Guest cannot list, view, delete, fetch result data, or download.
- Inactive user cannot access protected job/result/download routes.
- Inactive-user tests must cover at least one representative result route and one download route.
- Regular user lists only own non-deleted jobs.
- Admin can list/view all jobs; owner filter applies only to admin.
- Status/media/model/date filters work without bypassing ownership.
- Regular user cannot view another user's job detail.
- Regular user cannot fetch another user's summary, detections, tracks, result metadata, or downloads.
- `GET /api/jobs/{job_id}` returns status, progress, heartbeat, timestamps, summary, and safe references.
- `DELETE /api/jobs/{job_id}` hides job from normal list; queued job cancellation/soft-delete behavior matches chosen doc-consistent rule.
- Soft-deleted jobs are hidden from normal lists and blocked or hidden from regular detail access according to chosen safe behavior.
- Detections endpoint returns job detections only and includes derived center/size fields.
- Tracks endpoint returns job tracks only; image/no-track jobs return empty list.
- Summary endpoint handles null confidence values for no-detection completed jobs without error.
- Result metadata includes safe download URLs/references and no raw stored paths.
- Result metadata `available` values reflect file existence, not only DB path presence.
- Result/detail JSON does not contain raw storage field names: `result_media_path`, `csv_path`, or `json_path`.
- Download media/csv/json succeeds only when corresponding job path exists and file belongs to job.
- Download media/csv/json rejects a path recorded on the job row when it does not live under `results/{job_id}/`.
- Missing download file returns clear 404 or equivalent safe error without internal path.
- Completed no-detection job with CSV/JSON paths returns empty detections/tracks and allows CSV/JSON download.
- API responses and JSON body checks do not include absolute paths, `STORAGE_ROOT`, tokens, password hashes, or forbidden CV-only boundary fields.

Skipped as out of scope:

- Worker processing/export creation tests.
- CV inference tests.
- Frontend tests/build/manual browser flow.
- Docker Compose smoke unless backend runtime wiring changes.
- Admin storage cleanup tests.

## Ambiguities or conflicts

- WARNING: CONFLICT
  - `docs/index.md` current implementation state says backend remains placeholder-only.
  - Actual backend contains implemented app, tests, auth, media, models, and jobs creation.
  - This contract follows `docs/phase.md` plus actual repo state for implementation planning.
- Ambiguity: exact response schema is not fully specified. Use documented fields only and existing backend schema style.
- Ambiguity: exact DELETE behavior for processing jobs is not fully specified. Use conservative soft-delete/cancel behavior and test it.
- Resolved planning-review question: result metadata availability means file can be safely downloaded now, so file existence is checked without exposing paths.
- Resolved planning-review question: download association requires the selected job path to live under `results/{job_id}/` for the requested job.
- Ambiguity: result metadata format is not fully specified. Use safe availability/download references, not stored paths.
- Ambiguity: exact download filenames are not specified. Use sanitized filenames only.
