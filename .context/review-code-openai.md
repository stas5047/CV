# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 28 implementation adds the protected `/models` frontend page, model registry API helpers, admin registration/activation UI, focused tests, and `frontend/index.md` update. Core route protection, admin-only controls, relative-path client guard, active-state refresh, model display fields, and current frontend gates are in place.

Two important frontend UX defects remain: some visible model-page text is English, and activation failures are silent. No critical blocker found.

## Critical issues

None.

## Important issues

1. Visible English text remains on the production `/models` page.
   - Evidence: `frontend/src/pages/models/ModelPageParts.tsx:80` renders `backend API` in a user-facing error message; `frontend/src/pages/models/ModelPageParts.tsx:228` renders `YOLO registry`; `frontend/src/pages/models/ModelPageParts.tsx:149-150` renders `Precision` and `Recall`.
   - Why it matters: `docs/FRONTEND_UX.md` requires visible UI text, errors, labels, and helper text to be Ukrainian, with only accepted technical labels such as `FPS`, `mAP`, `YOLO`, `CSV`, and `JSON` explicitly allowed. `docs/phase.md` also scopes Phase 28 as Ukrainian frontend work. This repeats a prior status-resolved class of issue: `.context/status.md` says Phase 27 replaced visible `backend API` wording.
   - Expected fix: localize these labels/messages, keeping accepted technical tokens where needed, for example `Реєстр YOLO`, Ukrainian wording for backend connection, and Ukrainian metric labels where practical.

2. Admin model activation failure has no user-visible error state and no regression test.
   - Evidence: `frontend/src/pages/ModelsPage.tsx:51-58` defines `activateMutation` with `onMutate`, `onSuccess`, and `onSettled`, but no `onError` handling or displayed error state. `frontend/src/test/models-page.test.tsx` covers successful activation but not failed activation.
   - Why it matters: `docs/FRONTEND_UX.md` requires failed API requests and admin/user-facing errors to be clear and Ukrainian. Phase 28 includes admin activation as core behavior, so a backend `403`, `404`, or `500` currently leaves the user with no explanation after the button resets.
   - Expected fix: add safe Ukrainian activation error feedback and a focused failed-activation test.

## Optional issues

None.

## Quality gate assessment

- `rtk git status --short`: PASS for inspection; shows expected Phase 28 frontend/context changes plus existing forbidden review-resolution file modification not read.
- `rtk git diff --stat`: PASS for inspection.
- `rtk git diff -- ...allowed paths...`: PASS for inspection; skipped `.context/review-code-resolution.md` per user rule.
- `npm test -- models-page.test.tsx` from `frontend/`: PASS, 6 tests passed.
- `npm run lint` from `frontend/`: PASS.
- `npm test` from `frontend/`: PASS, 39 tests passed.
- `npm run build` from `frontend/`: PASS.

Coverage gap: no test asserts activation failure feedback, and tests permit visible English strings noted above.

## Security/privacy assessment

Applicable because Phase 28 touches admin model registration/activation UI.

- Regular users do not see registration or activation controls in tests.
- Backend remains authority for `POST /api/models` and `PATCH /api/models/{model_id}/activate`.
- Model cards do not display `weights_path`; tests assert absence of raw `weights_path`, relative weight path, `/app/storage`, Windows drive prefix, `null`, `undefined`, and `frame_stride`.
- Client rejects empty, absolute, Windows-drive, and `..` weights paths before submit, while backend validation remains final.
- No training launch control, secret display, token logging, or storage path construction found in the new frontend code.

## Positive findings

- `/models` remains protected and wired inside existing authenticated shell.
- Admin-only form/action visibility matches docs and tests.
- New API helper uses documented endpoints only: `GET /models?limit=100`, `POST /models`, and `PATCH /models/{model_id}/activate`.
- Model cards cover name, family, variant, active state, dataset fields, metrics, size, FPS, and documented YOLO11 fallback display.
- Missing metric values render Ukrainian placeholder text instead of raw `null`.
- Active model state is refetched after activation and covered by regression test.
- Implementation follows prototype structure without copying mock-only behavior into product contracts.

## Files consulted

- `AGENTS.md`
- `CLAUDE.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `docs/FRONTEND_UX.md`
- `docs/API.md`
- `docs/TRAINING_EXPERIMENTS.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `.context/review-plan-resolution.md`
- `.context/status.md`
- `prototype/index.md`
- `prototype/models.jsx`
- `frontend/package.json`
- `frontend/index.md`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/models.ts`
- `frontend/src/api/types.ts`
- `frontend/src/auth/useAuth.ts`
- `frontend/src/layout/AppShell.tsx`
- `frontend/src/pages/ModelsPage.tsx`
- `frontend/src/pages/models/ModelPageParts.tsx`
- `frontend/src/pages/models/modelPageUtils.ts`
- `frontend/src/pages/placeholders.tsx`
- `frontend/src/test/models-page.test.tsx`
- `frontend/src/test/setup.ts`
- `backend/app/api/models.py`
- `backend/app/schemas/models.py`
