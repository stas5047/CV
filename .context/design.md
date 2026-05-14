# Phase 19 Design - Worker CSV/JSON exports and no-detection contracts

## Phase goal

Generate and persist worker CSV/JSON exports for completed image and video jobs according to documented export contracts, including no-detection jobs.

## Intended behavior from docs

Confirmed facts:

- CSV export contains one row per detection.
- CSV required columns:
  - `job_id`
  - `media_id`
  - `frame_index`
  - `timestamp_ms`
  - `class_id`
  - `class_name`
  - `confidence`
  - `bbox_x1`
  - `bbox_y1`
  - `bbox_x2`
  - `bbox_y2`
  - `center_x`
  - `center_y`
  - `bbox_width`
  - `bbox_height`
  - `frame_width`
  - `frame_height`
  - `track_id`
  - `model_version`
  - `tracker_type`
- Derived export values come from corner coordinates:
  - `center_x = bbox_x1 + bbox_width / 2`
  - `center_y = bbox_y1 + bbox_height / 2`
  - `bbox_width = bbox_x2 - bbox_x1`
  - `bbox_height = bbox_y2 - bbox_y1`
- JSON export contains top-level:
  - `job`
  - `media`
  - `model`
  - `parameters`
  - `summary`
  - `detections`
  - `tracks`
- No-detection jobs are successful completed jobs.
- No-detection CSV exists with headers only.
- No-detection JSON has `detections: []`.
- No-detection summary has `total_detections = 0`, `frames_with_detections = 0`, `average_confidence = null`, `maximum_confidence = null`.
- `processing_jobs.csv_path` and `processing_jobs.json_path` store relative paths only.
- Exports must remain CV-only: image-space detections, confidence, class label, timestamps, track IDs, model data, and performance metrics.
- Exports must not include targeting, navigation, geospatial, physical-control, payload, weapon, or engagement data.

Assumptions:

- Existing `results/{job_id}/detections.csv` and `results/{job_id}/detections.json` path pattern remains.
- Export helper functions may be shared/refined only inside `cv/aerovision_worker/`; no new top-level folders needed.
- Internal `frame_stride` may remain in worker JSON `parameters` because docs only forbid standard UI exposure; do not add any frontend exposure.

## Architecture decisions

- Keep export generation in CV worker, not backend, because `docs/CV_PIPELINE.md` says worker generates CSV/JSON exports.
- Keep PostgreSQL as metadata store only; export files stay in shared filesystem storage.
- Keep DB writes atomic at job completion: detections/tracks and `processing_jobs` result paths update in completion persistence.
- Keep image and video export behavior aligned through same CSV column order and same detection export field names.
- Keep video track summaries in `tracks` only for detections with tracker-provided IDs.
- Keep path safety through existing storage path helpers before file writes.
- Keep failures secret-safe: failed export writes mark job failed with generic worker error message, not absolute path.

## Backend impact

Touched only if worker contract reveals backend result/download mismatch.

Current expected backend impact:

- None for Phase 19 implementation.
- Backend result/download endpoints consume `csv_path` and `json_path` already stored by worker.

## Frontend impact

Current expected frontend impact:

- None. Frontend phases happen later.
- No Ukrainian UI work in Phase 19.

## DB impact

Current expected DB impact:

- No schema changes.
- Worker updates existing `processing_jobs.csv_path`, `processing_jobs.json_path`, `summary_json`, status/progress/completion fields.
- Worker inserts/clears existing `detections` and `tracks` rows as needed.
- Relative path invariant must remain intact.

## API impact

Current expected API impact:

- No route or schema changes.
- Exports must match API contract so existing download endpoints can serve files safely.

## Security/privacy impact

Touched security/privacy surfaces:

- Export contents must omit absolute host/container paths.
- Export contents must omit forbidden CV-boundary fields.
- Worker error messages must not include `STORAGE_ROOT`, model paths, secrets, tokens, or DB credentials.
- Relative `csv_path` and `json_path` only.

Not touched:

- Auth, role checks, ownership checks, CORS, upload validation, seeded admin.

## Test strategy

Focused required checks:

- Run image export contract tests:
  - `python -m pytest tests/test_image_processing.py -q`
- Run video export contract tests:
  - `python -m pytest tests/test_video_processing.py -q`
- Run worker lint for changed worker/test files:
  - `python -m ruff check aerovision_worker tests`

Targeted assertions to keep/add:

- CSV fieldnames exactly match documented required columns.
- CSV has one row per detection.
- No-detection CSV has headers only.
- JSON top-level keys exactly include documented objects/arrays.
- No-detection JSON has empty `detections`.
- Video JSON has `tracks`, image JSON has `tracks: []`.
- Derived center-size values are correct.
- Export paths are relative and under `results/{job_id}/`.
- Export JSON text does not contain forbidden terms such as `targeting`, `navigation`, `interception`, `geospatial`, `engagement`, `payload`, `weapon`, `motor`, `autopilot`, or absolute `storage_root`.
- Export write failures mark job failed with safe generic message.

Broader checks not required for this phase:

- Full backend suite, unless backend result/download code changes.
- PostgreSQL queue integration tests, unless queue claim/persistence semantics change.
- Docker Compose smoke, unless runtime service config changes.
- Frontend build/tests, because frontend untouched.

## Ambiguities or conflicts

No `WARNING: CONFLICT` found.

Ambiguities:

- Docs define JSON top-level keys but do not enumerate all nested JSON fields. Implementation should avoid expanding nested fields beyond already available documented CV metadata.
- Docs forbid `frame_stride` in standard UI, but Phase 19 JSON `parameters` may include actual processing parameters. If reviewers decide export JSON is also user-facing enough to hide `frame_stride`, that needs explicit decision because API docs list `parameters` broadly.
- Current implementation appears to already include Phase 19 behavior. Implementation should verify first, then only patch proven gaps.
