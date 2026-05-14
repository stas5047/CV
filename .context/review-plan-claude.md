# Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 25 scope: frontend-only dashboard and authenticated shell, existing REST API only, Ukrainian UI, role-safe admin nav, loading/error/empty states, and prototype-based visual direction.

No blocking product-doc conflict found. Two changes should be made before implementation to reduce real risk: define dashboard metric derivation precisely, and make prototype browser verification non-optional unless blocked.

## Blocking issues

None.

## Important issues

1. Dashboard metric derivation is under-specified and can misrepresent required stats.
   - Evidence: `docs/phase.md:20-23` and `docs/FRONTEND_UX.md:146-149` require total processed files, total detections, average confidence, and average FPS. Plan uses `GET /api/admin/stats` and `GET /api/admin/jobs?limit=5` for admins (`.context/plan.md:25-27`) and says to render four metric cards (`.context/plan.md:51-54`), but current admin stats only exposes job counts/status counts, detection total, model counts, etc. (`backend/app/schemas/admin.py:21-47`; `backend/app/services/admin.py:36-58`). It does not expose average confidence or average FPS.
   - Risk: implementation may show `jobs.total` as "processed files" or calculate admin averages from only 5 recent jobs, producing misleading dashboard values.
   - Required change: add plan note that `total processed files` must come from completed jobs only when available, total detections from documented summary/admin data, and average confidence/FPS must be derived only from available completed job `summary_json` values or shown as Ukrainian unavailable placeholders. Do not invent global averages from limited recent rows.

2. Prototype visual verification is conditional even though phase is prototype-driven.
   - Evidence: current user instruction says frontend must be built entirely from `@prototype`; plan says manual browser check only "if dev server/browser available" (`.context/plan.md:83-87`) and quality gates say browser smoke "when available" (`.context/plan.md:99-102`). `docs/FRONTEND_UX.md:158` and `docs/TESTING_QA.md:371-385` require graceful dashboard states and frontend API error handling; visual/state issues are hard to catch with build/tests only.
   - Risk: implementation can pass unit/build gates while drifting from prototype shell/dashboard layout or breaking narrow viewport state.
   - Required change: make browser smoke against `/dashboard` required for implementation unless tooling is genuinely unavailable, in which case record exact blocker. Check desktop and narrow viewport against prototype dashboard/shell.

## Optional improvements

- Add one explicit test/review assertion that active model UI does not display `weights_path` or any storage-like path. API model responses include `weights_path`, but `docs/FRONTEND_UX.md:475` forbids exposing absolute filesystem paths and dashboard only needs model name/family/variant/active state.
- Add test assertion that regular-user dashboard code does not call `/api/admin/*`; this would make backend-authority boundary easier to verify.

## Questions for resolution

None.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `backend/app/schemas/admin.py`
- `backend/app/services/admin.py`
- `backend/app/schemas/jobs.py`
- `backend/app/schemas/models.py`
- `backend/app/api/admin.py`
- `backend/app/api/jobs.py`
- `backend/app/api/models.py`
- `frontend/package.json`
- `frontend/src/App.tsx`
- `frontend/src/layout/AppShell.tsx`
- `C:/Users/Kotletka/.codex/skills/taste-skill/SKILL.md`
- `C:/Users/Kotletka/.codex/plugins/cache/openai-curated/superpowers/1b89ff49/skills/using-superpowers/SKILL.md`
