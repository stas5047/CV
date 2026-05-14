## Phase 17 - Image processing pipeline

**Direction:** CV Worker / Image Processing  
**Goal:** Implement end-to-end image job processing.

### Scope

- Read uploaded image from shared storage.
- Validate readable image/decode result at worker level.
- Run YOLO inference on the image.
- Convert detections to original-resolution pixel coordinates.
- Store detection rows with:
  - `frame_index = 0`;
  - `timestamp_ms = 0`;
  - `track_id = null`.
- Write annotated image output under `results/{job_id}/`.
- Calculate image processing summary metrics.
- Update job result path, summary, progress, and status.
- Handle corrupted images, missing files, and failed output creation.
- Complete no-detection image jobs successfully.
- Add image processing tests using mocks or small fixtures.

### Relevant docs

- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/API.md`
- `docs/TESTING_QA.md`

### Validation

- Image job completes successfully.
- Annotated image is created when possible.
- Detection rows use original-resolution pixel coordinates.
- Image detections use `frame_index = 0`, `timestamp_ms = 0`, and `track_id = null`.
- No-detection image job completes with zero detections.
- Result paths are relative.
- Worker tests pass.

### Commit

`feat(worker-image): add image detection processing pipeline`