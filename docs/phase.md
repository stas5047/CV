## Phase 27 - Frontend jobs history and job details pages

**Direction:** Frontend
**Goal:** Implement job list, filters, status polling, details, detections/tracks, previews, and downloads.

### Scope

- Implement `/jobs` page.
- Add jobs table with:
  - status badge;
  - media type;
  - original filename;
  - model version;
  - created date;
  - processing duration;
  - detections count;
  - average confidence;
  - link to details.
- Add filters for status, media type, date, and model where practical.
- Implement `/jobs/:jobId` page.
- Show job status, media metadata, summary cards, progress, heartbeat/update time, and failed-job error area.
- Poll job status while queued or processing.
- Show processed media preview when possible.
- If processed video preview is unavailable, show Ukrainian notice and keep download button.
- Add detection table with frame index, timestamp, class, confidence, bounding box, and track ID.
- Add track summary table for videos.
- Add download buttons for annotated media, CSV, and JSON.
- Handle completed no-detection jobs with Ukrainian empty state, not error.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`

### Validation

- Jobs page shows only current user's jobs for regular users.
- Status badges use Ukrainian visible text.
- Queued/processing jobs poll and update UI.
- Completed jobs show summaries and tables.
- Failed jobs show safe Ukrainian error messages.
- No-detection jobs show empty state and keep downloads when available.
- Downloads work from UI.
- Frontend build passes.

### Commit

`feat(frontend-jobs): add jobs history details polling and downloads`
