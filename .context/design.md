# Phase 18 Design Contract

## Phase goal

Implement Phase 18 only: video job processing in the CV worker, including readable video validation, frame-by-frame inference, ByteTrack default tracking, optional BoT-SORT when runtime support exists, progress/heartbeat updates, annotated MP4 result output, detection rows, track summary rows, CSV/JSON exports, summary metrics, safe errors, and no-detection success.

## Intended behavior from docs

Confirmed:

- Worker reads uploaded video from shared storage using relative DB paths only.
- Worker must handle missing, corrupted, unreadable, or decode-failing videos as failed jobs with safe `error_message`.
- Worker reads or verifies frame count, FPS, width, height, and duration when available.
- Worker processes frames in order.
- Worker uses YOLO detection frame by frame.
- ByteTrack is default for video.
- BoT-SORT is supported only when runtime support is available.
- Tracking must preserve tracker state across frames for each video job so stable IDs can produce meaningful track summaries.
- Annotated video should be MP4 when possible.
- Progress and heartbeat update every configured 30 frames or 2 seconds by default, whichever comes first.
- Video detections include frame index, timestamp in milliseconds, bbox in original frame pixel coordinates, class `drone`, confidence, model data, tracker type, and `track_id` when available.
- Track IDs may be null when the tracker does not associate an ID.
- Worker creates one `tracks` summary row per job/track ID when tracks exist.
- No-detection video jobs complete successfully and still create annotated output when possible, CSV headers, JSON with empty `detections`, zero summaries, and no error.
- Worker writes only CV/image-space data. No targeting, navigation, geospatial, interception, or hardware-control outputs.

Assumptions:

- Use OpenCV for video decode/encode because dependency already exists and docs require `opencv-python-headless`.
- Use generated test videos rather than committed fixtures.
- Use worker-local fakes for model/tracking tests; do not require real model weights in unit tests.

## Architecture decisions

- Add media-type dispatch in the worker after job claim. The queue should claim queued jobs for supported media, then `main.py` dispatches images to existing image processor and videos to the new video processor.
- Keep video processing out of `image_processing.py` because that file is already over 500 lines and image/video processing have separate responsibilities.
- Reuse existing model loading, safe path, heartbeat, and job failure helpers.
- Keep all processing outside the claim transaction. Existing `claim_next_job` already commits before processing; Phase 18 must preserve this.
- Write result paths under `results/{job_id}/`: `annotated.mp4`, `detections.csv`, `detections.json`.
- Initialize and keep tracker runtime/configuration for the whole video job, not as independent per-frame stateless calls.
- Use a small internal representation for video detections and track summaries so CSV/JSON exports and DB inserts use one consistent source.
- Clear stale detection/track rows for the job before inserting final rows, matching image reprocessing behavior.
- Do not add Celery, Redis, REST worker polling, frontend changes, API changes, training changes, or live/RTSP input.

## Backend impact

Confirmed no backend product behavior change is intended.

Backend may be inspected because:

- Existing schema and result endpoints are the contract for detection/track rows and download paths.
- Existing job creation already stores video tracker parameters.

No backend route/schema change should be part of this phase unless implementation discovers a direct contract mismatch. If such mismatch appears, stop and report `WARNING: CONFLICT`.

## Frontend impact

No frontend code is touched in this phase.

## DB impact

No migration is intended.

Worker writes existing tables only:

- `processing_jobs`
- `detections`
- `tracks`

Required DB invariants:

- Result paths remain relative.
- `detections` rows use original frame pixel coordinates.
- `tracks` rows summarize video tracker IDs only and do not represent physical trajectories.
- No binary video/export data is stored in PostgreSQL.

## API impact

No API route or response schema change is intended.

Existing results endpoints should begin returning real video detections/tracks/download availability once worker writes documented rows and artifacts.

## Security/privacy impact

Touched:

- Shared-storage reads/writes.
- DB path fields.
- Worker logs/errors.
- JSON/CSV exports.

Rules:

- Reject unsafe source/result paths.
- Never store or expose absolute host/container paths.
- Safe job errors must not include storage root, model path, raw traceback, secrets, tokens, or DB URL.
- JSON exports must not include forbidden external fields such as targeting, navigation, interception, geospatial data, motor/payload/flight-control commands, or engagement decisions.
- User-uploaded media is decoded only, never executed.

## Test strategy

Worker tests:

- Update queue tests so video jobs are claimable in Phase 18.
- Add dispatcher tests that image jobs still call image processor and video jobs call video processor.
- Add video unit tests with generated tiny videos and fake model/tracker outputs:
  - successful video job writes annotated MP4, CSV, JSON, detections, tracks, summary, progress 100;
  - detections include frame indices and millisecond timestamps;
  - track IDs are stored when provided and may be null;
  - one fake track persists across multiple frames and produces one summary row with correct first frame, last frame, and frame count;
  - track summary rows aggregate first/last frame, frame count, average confidence, max confidence;
  - no-detection video completes with empty exports and zero summaries;
  - missing/corrupt/unreadable video fails safely;
  - output writer failure fails safely;
  - unsupported tracker runtime behavior fails safely and does not silently claim BoT-SORT ran;
  - progress/heartbeat updates during multi-frame processing;
  - JSON export `tracks` content matches persisted track summaries;
  - exports contain only API contract keys and no absolute paths or forbidden safety-boundary text.

Relevant gates:

- `cd cv; python -m ruff check .`
- `cd cv; python -m pytest`
- `cd cv; python -m pytest -m postgres` when PostgreSQL is reachable, because queue claiming changes.

Not planned:

- Frontend build/tests.
- Backend full suite unless implementation changes backend files.
- Docker Compose smoke unless runtime/dependency/container files change.

## Ambiguities or conflicts

- No doc conflict found.
- Risk level was not supplied in prompt; assumed `HIGH`.
- Docs do not define exact internal file names. Proposed new worker module names are implementation-owned, not product/API contracts.
- Docs do not define exact MP4 codec. Implementation should try a broadly available OpenCV codec and fail safely if writer cannot open.
- Docs allow BoT-SORT only when supported. Implementation should not silently claim BoT-SORT worked when runtime support is absent.
