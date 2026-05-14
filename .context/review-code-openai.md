# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 27 implementation is mostly doc-consistent: `/jobs` and `/jobs/:jobId` are protected, use backend REST APIs only, avoid `/api/admin/jobs`, keep `frame_stride` hidden, use authenticated blob downloads/previews, and cover main list/detail/no-detection/failed states with frontend tests. Lint, tests, and build pass.

Approval needs changes because one diff cleanliness gate is red, the documented model filter is missing despite existing API support, one visible error message contains English product-facing copy, and the new blob helper can send bearer tokens to arbitrary absolute URLs.

## Critical issues

None.

## Important issues

1. Diff whitespace gate fails.
   - Evidence: `rtk git diff --check` fails with `docs/phase.md:3: trailing whitespace`.
   - Impact: review gate is red even though frontend lint/test/build pass.

2. Jobs page omits the model filter required by the phase when practical.
   - Evidence: `docs/phase.md` says Phase 27 filters include status, media type, date, and model where practical.
   - Evidence: `docs/API.md` lists `model version` as a jobs filter, and `backend/app/api/jobs.py` accepts `model_version_id`.
   - Evidence: `frontend/src/pages/JobsPage.tsx:24-45` tracks and sends only status, media type, `created_from`, and `created_to`; no model state or `model_version_id` query param is wired.
   - Impact: users cannot filter job history by model even though backend support exists and the page already displays model names.

3. Jobs API error copy includes English visible UI text.
   - Evidence: `frontend/src/pages/JobsPage.tsx:62` renders `backend API` inside a user-facing Ukrainian error message.
   - Evidence: `docs/FRONTEND_UX.md` requires visible frontend errors/messages to be Ukrainian; accepted English exceptions include technical labels like `FPS`, `YOLO`, `CSV`, `JSON`, not `backend API`.
   - Impact: Phase 27 violates the Ukrainian UI invariant on failed jobs-list loading.

4. Blob download helper can leak bearer tokens to absolute external URLs.
   - Evidence: `frontend/src/api/client.ts:65` accepts any `path.startsWith("http")` URL as-is.
   - Evidence: `frontend/src/api/client.ts:67-68` then attaches `Authorization: Bearer ...` to that URL.
   - Impact: if a malformed or compromised API response returns an absolute external `download_url`, the frontend sends the JWT to that host. Result downloads should be restricted to same-origin/API-relative URLs.

## Optional issues

None.

## Quality gate assessment

- `npm run lint`: PASS.
- `npm test`: PASS, 32 tests passed.
- `npm run build`: PASS.
- `rtk git diff --check`: FAIL, `docs/phase.md:3: trailing whitespace`.
- Manual browser smoke: not run in this review; `.context/status.md` says it was not available in the implementation session.

## Security/privacy assessment

Backend remains the authorization authority, and the new pages use protected backend endpoints rather than storage paths. Failed job internals are not rendered. Main remaining risk is the absolute-URL bearer-token leak in `apiBlobRequest`.

## Positive findings

- `/jobs` and `/jobs/:jobId` are routed under `ProtectedRoute`.
- Regular jobs page uses `/api/jobs`, not admin/global job endpoints.
- Result preview and downloads use authenticated blob fetches, with object URL cleanup.
- No-detection completed jobs render as a successful empty state with downloads still available.
- Job details avoid rendering raw `error_message`, `frame_stride`, storage roots, or absolute paths in tested states.
- Frontend tests cover route protection, list rendering, filtering, details rendering, downloads, no-detection, failed-state safety, and video-only tracks.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `frontend/package.json`
- `frontend/index.md`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/jobs.ts`
- `frontend/src/api/types.ts`
- `frontend/src/pages/JobsPage.tsx`
- `frontend/src/pages/JobDetailsPage.tsx`
- `frontend/src/pages/jobs/jobFormatters.ts`
- `frontend/src/pages/jobs/JobPageParts.tsx`
- `frontend/src/test/jobs-page.test.tsx`
- `frontend/src/test/job-details-page.test.tsx`
- `backend/app/api/jobs.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/results.py`
- `prototype/jobs.jsx`
- `prototype/job-detail.jsx`
- `rtk git status --short`
- `rtk git diff --stat`
- `rtk git diff`
