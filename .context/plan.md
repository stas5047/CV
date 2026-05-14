# Phase 18 Implementation Plan

## Scope

Implement only `Phase 18 - Video processing and tracking pipeline`.

Do not implement frontend pages, backend API changes, database migrations, training utilities, Docker runtime changes, RTSP/live input, cancellation, or later-phase polish.

## Ordered atomic plan

1. `@role/developer-cv-worker` Update queue contract to claim supported media jobs.
   - Modify `cv/aerovision_worker/queue.py` so `ClaimedJob` includes `media_type`.
   - Remove image-only claim filter while keeping soft-delete checks, oldest-first ordering, and PostgreSQL `FOR UPDATE SKIP LOCKED`.
   - Verify with queue tests that image and video jobs can be claimed and deleted media/jobs are skipped.

2. `@role/tester` Update queue tests for Phase 18 behavior.
   - Modify `cv/tests/test_queue.py` to replace "video jobs remain queued" with "oldest supported queued job is claimed, including video".
   - Update `cv/tests/test_queue_postgres.py` fixture/query expectations if `ClaimedJob.media_type` affects assertions.
   - Verify queue helpers still keep claim transaction short.

3. `@role/developer-cv-worker` Add worker dispatch by media type.
   - Modify `cv/aerovision_worker/main.py` so claimed image jobs call `process_image_job` and claimed video jobs call video processing.
   - Unknown media type must fail the claimed job with a safe error.
   - Preserve model loading before processing and existing model-load failure handling.

4. `@role/tester` Add dispatcher tests.
   - Update `cv/tests/test_startup.py` to cover image dispatch, video dispatch, unsupported media failure, and model-load failure.
   - Verify no job processing runs inside queue claim transaction.

5. `@role/developer-cv-worker` Add video job metadata loading and path validation.
   - Create worker-local video processing code.
   - Load job/media fields from existing `processing_jobs` and `media_files`.
   - Require `media_type = 'video'`.
   - Validate `stored_path` with existing storage path helpers.
   - Fail safely for missing metadata, unsafe path, missing file, unreadable video, or failed decode.

6. `@role/tester` Add metadata and decode tests.
   - Add `cv/tests/test_video_processing.py`.
   - Generate tiny test videos in temp storage at runtime.
   - Cover missing source, corrupt source, unsafe source path, zero-frame/unreadable capture, and safe error messages with no absolute paths.

7. `@role/developer-cv-worker` Implement frame processing loop.
   - Read frames in order with OpenCV.
   - Use stored/captured FPS, width, height, frame count when available.
   - Compute timestamp as milliseconds from frame index and FPS when FPS is available.
   - Run YOLO detection/tracking per frame using confidence, IoU, image size, selected device, and tracker type from `input_params_json`, while preserving job-scoped tracker state across sequential frames.
   - Keep `frame_stride` internal and default to `1`.

8. `@role/developer-cv-worker` Implement tracker behavior.
   - Use ByteTrack as default tracker.
   - Support BoT-SORT only through runtime-supported tracker configuration.
   - Keep tracker state/configuration alive for the whole video job so repeated track IDs can persist across frames.
   - Store `track_id` when runtime result provides one; allow null when unassociated.
   - If requested tracker runtime support is unavailable, fail the job safely instead of silently falling back or reporting unsupported tracking as successful.
   - Do not compute physical trajectories or real-world coordinates.

9. `@role/tester` Add detection/tracking tests.
   - Fake model/tracker outputs for frames with and without IDs.
   - Verify frame index, timestamp, original pixel bbox coordinates, confidence, class `drone`, tracker type, and nullable track IDs.
   - Verify one fake track persists across multiple frames and creates one summary row with correct first frame, last frame, and frame count.
   - Verify requested `botsort` is passed to runtime when configured.
   - Verify unsupported tracker runtime behavior marks the job failed with a safe error.

10. `@role/developer-cv-worker` Write annotated MP4 output.
    - Write `results/{job_id}/annotated.mp4`.
    - Draw bounding boxes and labels on frames.
    - Fail safely if output directory or video writer creation/write fails.
    - Keep output path relative in DB.

11. `@role/tester` Add annotated output tests.
    - Verify completed video job creates a file at relative path `results/{job_id}/annotated.mp4`.
    - Verify writer failure marks job failed with safe error and no absolute path.

12. `@role/developer-cv-worker` Add heartbeat and progress updates.
    - During video processing, call existing heartbeat helper every configured frame interval or configured seconds, whichever comes first.
    - Calculate progress from processed frames and total frame count when total is known.
    - Ensure final completion sets progress to `100`.

13. `@role/tester` Add heartbeat/progress tests.
    - Use multi-frame generated video and monkeypatched time/settings.
    - Verify at least one mid-processing heartbeat/progress update before completion.
    - Verify final job progress is `100`.

14. `@role/developer-cv-worker` Persist detections and track summaries.
    - Delete prior `detections` and `tracks` for the job before final inserts.
    - Insert one detection row per detection.
    - Aggregate `tracks` by non-null track ID with first frame, last frame, frames count, average confidence, and max confidence.
    - Do not insert track summaries when no track IDs exist.

15. `@role/tester` Add DB persistence tests.
    - Verify detection rows and track rows are inserted correctly.
    - Verify no-detection videos have zero detections and zero tracks.
    - Verify reprocessing/finalization does not leave stale rows.

16. `@role/developer-cv-worker` Generate CSV and JSON exports.
    - CSV must use documented columns and one row per detection; no-detection CSV has headers only.
    - JSON must include `job`, `media`, `model`, `parameters`, `summary`, `detections`, and `tracks`.
    - Include only CV/image-space fields and no forbidden boundary fields.

17. `@role/tester` Add export contract tests.
    - Verify CSV columns match `docs/API.md`.
    - Verify JSON top-level keys match `docs/API.md`.
    - Verify exported `tracks` content matches persisted track summary rows.
    - Verify no-detection JSON has empty `detections`.
    - Verify exports contain no absolute paths and no forbidden safety-boundary terms.

18. `@role/developer-cv-worker` Complete successful and failed jobs safely.
    - On success, update `processing_jobs` to `completed`, set summary, result paths, `completed_at`, heartbeat, progress `100`, and clear lock fields.
    - On failure, use existing failure helper and safe messages.
    - Ensure no-detection is success, not failure.

19. `@role/tester` Add end-to-end worker video tests.
    - Verify successful detection video job completes.
    - Verify no-detection video job completes.
    - Verify missing/corrupt/output-failure cases fail with clear safe errors.

20. `@role/code-reviewer` Review Phase 18 scope and safety.
    - Check no frontend/backend/API/migration/training work was added unless required by direct test failure.
    - Check no Celery/Redis, REST worker loop, live camera/RTSP, geospatial/targeting/navigation/control output, absolute paths, raw secrets, or committed media artifacts.
    - Check file sizes; keep video code out of oversized image module.

21. `@role/tester` Run relevant quality gates.
    - Run `cd cv; python -m ruff check .`.
    - Run `cd cv; python -m pytest`.
    - Run `cd cv; python -m pytest -m postgres` when PostgreSQL is reachable.
    - If backend files are changed unexpectedly, run targeted backend tests for jobs/results contracts.

22. `@role/docs-maintainer` Update implementation index only if implementation files or current CV worker capabilities changed.
    - Update `cv/index.md` to say video processing/tracking is now implemented if Phase 18 implementation succeeds.
    - Do not modify product docs such as `docs/API.md`, `docs/CV_PIPELINE.md`, `docs/ROADMAP.md`, or `docs/phase.md` during implementation unless user explicitly requests a docs update.

## Verification checklist

- Video jobs are claimable and dispatched.
- Image job behavior remains passing.
- Video job completes with annotated MP4, CSV, JSON, detection rows, summaries, and track rows when tracks exist.
- Tracker state persists across sequential video frames so stable runtime track IDs produce meaningful summaries.
- Progress and heartbeat update during video processing.
- No-detection video completes successfully with empty detection exports.
- Missing/corrupt video and writer failures mark job failed safely.
- DB stores only relative paths.
- Exports and logs stay inside CV-only boundary.
- Relevant CV worker gates pass or blockers are documented with exact command output.
