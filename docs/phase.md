## Phase 31 - Frontend Ukrainian UX, responsive polish, and scope audit

**Direction:** Frontend / QA  
**Goal:** Make the frontend coherent, Ukrainian, polished, responsive, and within documented scope.

### Scope

- Audit all user-facing text for Ukrainian language.
- Ensure accepted technical labels such as `FPS`, `mAP`, `YOLO`, `CSV`, and `JSON` remain readable.
- Standardize status badges, buttons, forms, tables, cards, charts, skeletons, toasts, and empty states.
- Standardize date, duration, confidence, percentage, and bounding-box formatting.
- Ensure raw `null` is never displayed.
- Ensure absolute filesystem paths are never displayed.
- Ensure `frame_stride` is not visible in standard UI.
- Ensure admin buttons and navigation are hidden from regular users.
- Ensure no frontend text presents CV outputs as targeting, navigation, or interception instructions.
- Verify responsiveness for desktop and laptop screens, and reasonable behavior on narrower screens.
- Add or update frontend tests where practical.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Frontend lint/typecheck/build pass.
- Manual route smoke passes for login, registration, dashboard, upload, jobs, job details, models, experiments, and admin.
- Ukrainian UX audit passes.
- No out-of-scope UI actions are visible.
- Empty, loading, error, forbidden, and no-detection states are clear.

### Commit

`style(frontend): polish Ukrainian dashboard UX and scope boundaries`