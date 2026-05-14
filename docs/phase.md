## Phase 18 - Video processing and tracking pipeline

**Direction:** CV Worker / Video Processing  
**Goal:** Implement end-to-end video job processing with progress updates and tracking.

### Scope

- Read uploaded video from shared storage.
- Validate readable video/decode result at worker level.
- Read or verify video metadata: frame count, FPS, width, height, duration when available.
- Process frames in order.
- Run YOLO detection frame by frame.
- Apply ByteTrack by default for video tracking.
- Support BoT-SORT as an alternative when runtime support is available.
- Write annotated frames to output video, preferably MP4.
- Update progress and heartbeat every configured frame/time interval.
- Store detection rows with frame indices and timestamps in milliseconds.
- Store track IDs when the tracker provides them.
- Create track summary rows per job/track ID.
- Calculate average FPS, processing duration, confidence summaries, and video metrics.
- Handle missing/corrupted videos and failed output media creation safely.
- Complete no-detection video jobs successfully.
- Add video processing tests using small fixtures, mocks, or smoke assets.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Video job completes successfully.
- Progress and heartbeat update during processing.
- Annotated video is created or a safe downloadable result is available.
- Detections include frame indices and timestamps.
- Track IDs are stored when available and may be null when not associated.
- Track summaries are created for video jobs with tracks.
- Average FPS and processing duration are calculated.
- No-detection video job completes successfully.

### Commit

`feat(worker-video): add video detection tracking and progress pipeline`