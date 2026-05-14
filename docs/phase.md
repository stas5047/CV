## Phase 30 - Frontend admin page

**Direction:** Frontend / Admin  
**Goal:** Implement admin-only UI for global stats, global jobs, users, shortcuts, and cleanup.

### Scope

- Implement `/admin` page.
- Restrict route to admin users in frontend routing.
- Display global processing statistics.
- Display recent jobs from all users.
- Display model management shortcuts.
- Display safe storage cleanup action.
- Display basic users table.
- Do not implement complex user management unless explicitly approved later.
- Add Ukrainian loading, error, empty, and success states.
- Ensure backend remains the source of truth for authorization.

### Relevant docs

- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Admin navigation appears only for admins.
- Regular users cannot access `/admin`.
- Admin page loads global stats/jobs/users.
- Cleanup action is clear and conservative in UI wording.
- Empty lists show Ukrainian empty states.
- Frontend build passes.

### Commit

`feat(frontend-admin): add admin dashboard and cleanup UI`