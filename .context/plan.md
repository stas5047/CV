# Phase 31 Implementation Plan

## Scope

Phase only: `Phase 31 - Frontend Ukrainian UX, responsive polish, and scope audit`.

Do not modify backend, database, API contracts, worker, training, Docker runtime, product docs, or routes. Use `prototype/` only as visual reference.

## Ordered Atomic Plan

1. `@role/developer-frontend` - Inventory production routes and prototype screens.
   - Verify `frontend/src/App.tsx` routes match required docs routes.
   - Map each production page to its prototype file.
   - Verifiable by route-to-file checklist in implementation notes or final report.

2. `@role/developer-frontend` - Audit visible text.
   - Search route/page/component files for user-facing strings.
   - Keep Ukrainian text for labels, buttons, headings, errors, empty states, toasts, and table headings where practical.
   - Keep only documented technical labels such as `FPS`, `mAP`, `YOLO`, `CSV`, `JSON`, plus field labels required by docs when clearer.
   - Verifiable by targeted `rg` review and frontend tests.

3. `@role/developer-frontend` - Audit CV-only wording.
   - Search frontend visible text for targeting, interception, navigation, geolocation, payload, aiming, flight-control, or hardware-control language.
   - Replace any found user-facing text with CV-only image-space wording from docs.
   - Verifiable by targeted `rg` scan and route smoke.

4. `@role/developer-frontend` - Audit unsafe display.
   - Ensure pages use existing safe text/format helpers before rendering filenames, model names, error messages, paths, artifact values, and backend details.
   - Ensure raw `null`, `undefined`, `frame_stride`, `C:\`, `/app/storage`, and `/storage/` do not appear in UI.
   - Verifiable by existing and updated tests.

5. `@role/developer-frontend` - Standardize formatting helpers where pages drift.
   - Align date, duration, confidence, percentage, FPS, count, and bounding-box display across dashboard, jobs, details, models, experiments, and admin.
   - Do not change API payloads.
   - Verifiable by unit/route tests and manual screenshots.

6. `@role/developer-frontend` - Standardize status badge behavior.
   - Align job status badge labels, dot behavior, colors, and sizes with docs and prototype.
   - Keep visible status text Ukrainian.
   - Verifiable by status badge tests or page route assertions.

7. `@role/developer-frontend` - Standardize buttons/forms/tables/cards/skeletons/toasts/empty states.
   - Use existing shadcn-style `Button`, `Input`, `.av-*` classes, and page part components.
   - Match prototype density, borders, green accent, mono numeric data, compact tables, and small radius.
   - Audit and fix success/error toast notifications or equivalent documented feedback for implemented actions, especially login/register errors, upload/job creation, downloads, model/admin mutations, and cleanup.
   - Keep feedback text Ukrainian and avoid adding new product flows.
   - Avoid new dependencies.
   - Verifiable by browser smoke and frontend snapshot-free route tests.

8. `@role/developer-frontend` - Audit auth and admin visibility.
   - Verify guests see only auth/public routes.
   - Verify regular users do not see admin navigation or admin mutation actions.
   - Verify `/admin` still goes through `AdminRoute`.
   - Verifiable by existing auth/admin tests plus any needed assertions.

9. `@role/developer-frontend` - Audit loading/error/empty/forbidden/no-detection states.
   - Confirm each required route has clear Ukrainian loading, error, and empty state.
   - Confirm no-detection completed job is successful and keeps downloads when available.
   - Confirm experiments use required empty-state text for missing sections.
   - Verifiable by existing tests and focused additions where gaps appear.

10. `@role/developer-frontend` - Audit responsive behavior.
    - Check shell, mobile drawer, auth forms, metric grids, upload layout, tables, details page, charts, and admin panels at narrow and desktop widths.
    - Prefer single-column mobile layouts and table horizontal scroll.
    - Keep `min-h-[100dvh]` where full-height behavior exists.
    - Verifiable by manual browser route smoke and CSS review.

11. `@role/developer-frontend` - Apply minimal frontend fixes found by the audits.
    - Modify only relevant existing frontend files and existing tests.
    - Do not add routes, API calls, schema fields, product flows, or product docs.
    - Verifiable by `git diff -- frontend`.

12. `@role/tester` - Run frontend quality gates.
    - `cd frontend; npm run lint`
    - `cd frontend; npm test`
    - `cd frontend; npm run build`
    - Expected: PASS, except known Vite chunk-size warning may remain if build succeeds.

13. `@role/tester` - Run manual route smoke.
    - Check `/login`, `/register`, `/dashboard`, `/upload`, `/jobs`, `/jobs/:jobId`, `/models`, `/experiments`, and `/admin`.
    - Include regular-user and admin visibility where practical.
    - Include narrow viewport smoke.
    - Record whether smoke used live backend data, seeded/mock test data, or route-level test harness data.
    - Verifiable by manual notes in final implementation report.

14. `@role/code-reviewer` - Scope and safety review.
    - Compare diff against Phase 31 docs only.
    - Confirm no backend/db/API/runtime/product-doc changes.
    - Confirm no out-of-scope CV wording.
    - Confirm no unsafe path/secret display.
    - Confirm frontend remains based on prototype visual language.
    - Verifiable by review notes and final verdict.

15. `@role/docs-maintainer` - Documentation update decision.
    - Product docs must not be changed for this phase unless implementation changes commands, env vars, documented file paths, or component indexes.
    - Expected for Phase 31: docs updates skipped.
    - Verifiable by `git diff -- docs frontend/index.md`.

## Quality Gates

- `cd frontend; npm run lint`
- `cd frontend; npm test`
- `cd frontend; npm run build`
- Manual frontend route smoke for required routes.
- Toast/success-error feedback audit.
- Ukrainian UX audit.
- Scope boundary audit.
- Admin visibility audit.
- Unsafe display audit for raw `null`, `undefined`, `frame_stride`, absolute paths, and storage internals.

## Out Of Scope

- Backend, database, API, worker, training, Docker runtime, deployment, or product docs changes.
- New routes or product flows.
- New API calls or schema fields.
- Live camera, RTSP, targeting, navigation, interception, hardware control, or training-from-UI behavior.
- Adding Framer Motion, GSAP, Three.js, or icon libraries not already installed.
