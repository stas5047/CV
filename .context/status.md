Phase 28 - Frontend model registry page

Status: code review resolved and final-fix verified.

Scope completed:
- Added typed frontend model registry API helpers for list, register, and activate actions.
- Replaced `/models` placeholder with protected Ukrainian model registry page.
- Added admin-only model registration form using storage-relative weights paths.
- Added client-side guard against absolute/traversal weights paths while keeping backend authorization as authority.
- Added admin activation flow with model-list refetch so active state updates visibly.
- Added model metrics display, active/fallback badges, loading/error/empty states, and missing-metric placeholders.
- Added focused route tests for regular users, admins, unsafe paths, activation update, loading/error/empty states, and unsafe value absence.
- Updated `frontend/index.md` for current Phase 28 state.

Code review fixes completed:
- Localized remaining avoidable English model-page text (`backend API`, `YOLO registry`, `Precision`, `Recall`, and `runtime` wording).
- Added safe Ukrainian activation failure feedback.
- Added regression coverage for failed activation without exposing raw backend error detail.

Quality gates:
- `npm test -- models-page.test.tsx` PASS, 7 tests passed.
- `npm run lint` PASS.
- `npm test` PASS, 40 tests passed.
- `npm run build` PASS.
- `Invoke-WebRequest http://localhost:5173/models` PASS (200); port 5173 was already in use.
- `git diff --check` FAIL: pre-existing `docs/phase.md:3` trailing whitespace; not part of accepted Phase 28 code-review fixes, so left unchanged.

Security/privacy:
- Regular users do not see register/activate controls.
- Backend remains authority for admin registration/activation.
- Model cards do not display `weights_path` or unsafe absolute paths.
- Admin form rejects `/app/storage/...`, Windows drive paths, and `..` segments before submit.
- No secrets, tokens, passwords, or training-launch controls added.

Deviations:
- None from `.context/design.md`, `.context/plan.md`, planning resolution, or accepted code-review resolution.

Remaining risks:
- Manual in-app browser smoke was not performed because no Browser plugin callable tool was exposed in this tool set; HTTP route smoke passed.
- `docs/phase.md:3` has trailing whitespace from prior worktree state; not resolved because current review resolution accepted only Phase 28 model-page fixes.
