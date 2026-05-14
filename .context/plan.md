# Plan - Phase 27

1. `@role/developer-frontend` Add Phase 27 API types in `frontend/src/api/types.ts` for job result metadata, detections, tracks, and list responses from `backend/app/schemas/jobs.py`.
   - Verify TypeScript types match existing backend field names and do not add undocumented fields.

2. `@role/developer-frontend` Add `frontend/src/api/jobs.ts` with functions for:
   - `GET /jobs`
   - `GET /jobs/{jobId}`
   - `GET /jobs/{jobId}/summary`
   - `GET /jobs/{jobId}/detections`
   - `GET /jobs/{jobId}/tracks`
   - `GET /jobs/{jobId}/result`
   - authenticated download by backend-provided download URL.
   - authenticated processed-media preview blob by backend-provided download/preview URL, with object URL cleanup.
   - Verify all paths stay under `/api` through existing client config and no storage path is constructed.

3. `@role/developer-frontend` Create shared Phase 27 formatting helpers for status labels, media type labels, dates, duration, confidence, timestamps, bounding boxes, counts, and safe missing-value placeholders.
   - Verify helpers never return raw `null`, `undefined`, absolute paths, or `frame_stride`.

4. `@role/developer-frontend` Implement `/jobs` page from prototype structure:
   - header with upload action;
   - search/local filename filter only across the currently loaded page, with Ukrainian wording that does not imply whole-history search;
   - backend-backed status and media type filters;
   - date filters only using `created_from`/`created_to`;
   - optional model filter only if backed by existing `/models`;
   - paginated table;
   - loading skeleton;
   - API error state with retry;
   - no-jobs and no-results Ukrainian empty states.
   - Verify regular user page uses `/api/jobs`, not `/api/admin/jobs`.

5. `@role/developer-frontend` Implement `/jobs/:jobId` page from prototype structure:
   - back link;
   - status badge;
   - queued/processing progress and last update/heartbeat;
   - safe failed-job error area;
   - media metadata and authenticated blob preview with object URL cleanup, or Ukrainian preview-unavailable notice;
   - summary cards;
   - processing parameters without `frame_stride`;
   - downloads block;
   - detections table;
   - video-only tracks table;
   - no-detection and no-track Ukrainian empty states.
   - Verify CV output wording stays detection/tracking/image-space only.

6. `@role/developer-frontend` Add polling behavior for job details.
   - Poll while status is `queued` or `processing`.
   - Stop polling after `completed`, `failed`, or `cancelled`.
   - Refresh result/detection/track queries after completion.
   - Verify polling does not run for terminal jobs.

7. `@role/developer-frontend` Wire real page modules into `frontend/src/App.tsx` and remove only the jobs/detail imports from placeholder usage.
   - Verify `/models`, `/experiments`, and `/admin` placeholders remain unchanged for later phases.

8. `@role/developer-frontend` Add focused tests for jobs list route.
   - Verify protected `/jobs` renders table data.
   - Verify unauthenticated `/jobs` redirects to login, or explicitly verify existing protected-route tests cover the final `/jobs` route entry.
   - Verify filters produce documented query params.
   - Verify empty/no-results states.
   - Verify detail links.
   - Verify no raw `null`, `undefined`, absolute path, or `frame_stride`.

9. `@role/developer-frontend` Add focused tests for job details route.
   - Verify unauthenticated `/jobs/:jobId` redirects to login, or explicitly verify existing protected-route tests cover the final `/jobs/:jobId` route entry.
   - Verify completed image/video rendering.
   - Verify queued/processing progress state.
   - Verify failed state hides raw backend internals.
   - Verify no-detection empty state is not error.
   - Verify downloads use backend endpoints.
   - Verify track table appears only for video jobs with tracks.

10. `@role/tester` Run `cd frontend; npm run lint`.
    - PASS required before completion, or document exact blocker.

11. `@role/tester` Run `cd frontend; npm test`.
    - PASS required before completion, or document exact blocker.

12. `@role/tester` Run `cd frontend; npm run build`.
    - PASS required before completion, or document exact blocker.

13. `@role/tester` Run manual browser smoke when implementation is ready and local frontend can run:
    - Check `/jobs` at desktop and narrow widths.
    - Check `/jobs/:jobId` completed, no-detection, failed, and queued/processing states where fixtures or backend data make practical.
    - Check download buttons trigger through backend endpoints without exposing absolute paths.
    - Check video preview unavailable state keeps download action available.
    - PASS required before completion, or document exact blocker/not available.

14. `@role/code-reviewer` Review Phase 27 frontend diff against `docs/FRONTEND_UX.md`, `docs/API.md`, `docs/CV_PIPELINE.md`, and this contract.
    - Verify no source-of-truth drift, no admin/global route creep, no unsafe paths/errors, no non-Ukrainian visible UI, no download auth issue, no `frame_stride`, no CV-only boundary violation.

15. `@role/docs-maintainer` Update no product docs by default.
    - Only update `frontend/index.md` if implementation changes current frontend state description or commands.
    - Verify no edits to product docs unless command/structure changes require it.
