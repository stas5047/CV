# Phase 28 Plan - Frontend Model Registry Page

1. [@role/developer-frontend] Create focused model API helpers in `frontend/src/api/models.ts`.
   - Add `listModels`, `registerModel`, and `activateModel` wrappers around existing `apiRequest`.
   - Use only `/models`, `/models?limit=100`, and `/models/{model_id}/activate`.
   - Verification: helpers compile and no endpoint outside `docs/API.md` is introduced.

2. [@role/developer-frontend] Add frontend request typing in `frontend/src/api/types.ts` only if needed.
   - Define `ModelCreateRequest` from existing backend schema fields.
   - Do not add response fields absent from `ModelVersion`.
   - Verification: TypeScript accepts create payload without `any` for form submission.

3. [@role/developer-frontend] Add `frontend/src/pages/models/ModelPageParts.tsx`.
   - Include model metric extraction/formatting helpers.
   - Include Ukrainian empty, loading, error, active badge, fallback badge, metric bar, model list, and admin form components.
   - Hide raw `weights_path` in display cards/list.
   - Show dataset description, family, variant, active status, key metrics, and model size when known.
   - Add admin weights-path helper text and client-side rejection for absolute-looking or traversal-looking paths while preserving backend authority.
   - Verification: file contains no API calls and no later-phase experiment/admin UI.

4. [@role/developer-frontend] Add `frontend/src/pages/ModelsPage.tsx`.
   - Fetch models with TanStack Query.
   - Detect admin role from existing auth state.
   - Show prototype-based model registry layout.
   - Show admin-only register action/form and activate buttons.
   - Invalidate/refetch models after successful registration or activation.
   - Verification: `/models` renders data from `/api/models` and non-admin users see view-only UI.

5. [@role/developer-frontend] Wire `/models` route in `frontend/src/App.tsx`.
   - Import `ModelsPage` from new page file.
   - Keep `ExperimentsPage` and `AdminPage` placeholders unchanged.
   - Verification: route remains inside `ProtectedRoute` and no admin guard is added to `/models`.

6. [@role/developer-frontend] Add `frontend/src/test/models-page.test.tsx`.
   - Test guest redirect from `/models`.
   - Test regular user list rendering and absence of admin controls.
   - Test dataset description, model size when known, and YOLO11 fallback metadata rendering.
   - Test known metrics fixture and missing metrics fixture separately.
   - Test admin registration POST body.
   - Test admin registration rejects absolute-looking or traversal-looking weights paths before submit and displays safe Ukrainian errors.
   - Test admin activation PATCH call.
   - Test activation refetch/update makes the newly activated model visually active and avoids stale active-state display.
   - Test loading/error/empty/missing-metric states.
   - Test absence of raw `null`, `undefined`, `frame_stride`, `/app/storage`, and displayed `weights_path`.
   - Verification: `npm test -- models-page.test.tsx` passes if Vitest supports file filter; otherwise full `npm test`.

7. [@role/code-reviewer] Review frontend scope against Phase 28 docs and prototype.
   - Check Ukrainian visible text.
   - Check no new routes or product behavior.
   - Check no training launch, file upload for weights, experiments page, or admin page work.
   - Check admin UI visibility is frontend-only convenience and backend remains authority.
   - Verification: review notes identify no Phase 29/30 work.

8. [@role/tester] Run relevant frontend gates.
   - `npm run lint`
   - `npm test`
   - `npm run build`
   - Verification: all pass, or failures are recorded with exact command and reason.

9. [@role/developer-frontend] Fix only Phase 28 failures found by tests/review.
   - Keep edits limited to model registry page, model API helpers, types, and tests.
   - Verification: rerun failed relevant gate(s).

10. [@role/docs-maintainer] Decide docs/index updates.
   - Do not update product docs in this phase unless implementation changes documented commands or file indexes.
   - If source files are created, update `frontend/index.md` only in implementation phase if required by repository index policy, not during this planning-only phase.
   - Verification: no product docs changed during this contract phase.
