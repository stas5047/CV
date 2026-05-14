# Phase 28 Design - Frontend Model Registry Page

## Phase goal

Build the production `/models` frontend page for viewing registered model versions and, for admins only, registering and activating models through existing backend REST endpoints.

## Intended behavior from docs

Confirmed facts:

- `/models` is a protected frontend route.
- Authenticated users can view registered model versions.
- Regular users must not see admin-only mutation actions.
- Admin users can register model versions and activate one model.
- Models list must show:
  - model name;
  - family, including YOLO26 or documented YOLO11 fallback;
  - variant;
  - active status;
  - dataset description;
  - key metrics;
  - model size when known.
- Missing metric values must render Ukrainian placeholders or empty states, not raw `null`.
- Visible UI text must be Ukrainian. Technical labels such as `YOLO`, `mAP`, `FPS`, `JSON` may remain English.
- Frontend calls only backend REST API.
- Backend remains authorization source of truth.
- UI must not expose unsafe absolute filesystem paths.
- Training is not launched from UI or API.
- Model registration uses existing relative storage paths. Large `.pt` upload through UI is optional and not required.
- YOLO26 is primary. YOLO11 appears only as documented fallback metadata.

## Architecture decisions

- Replace only the Phase 28 placeholder route with a real page. Do not touch experiments/admin later-phase placeholders.
- Add a focused `frontend/src/api/models.ts` module for model list, detail if needed, create, and activate calls using existing `apiRequest`.
- Keep API types aligned with existing backend schema. Extend `frontend/src/api/types.ts` only for `ModelCreateRequest` if needed.
- Implement `frontend/src/pages/ModelsPage.tsx` as page orchestrator with TanStack Query.
- Put formatting, metric extraction, status badge, list, empty/error/loading states, and admin form helpers in `frontend/src/pages/models/ModelPageParts.tsx` if needed for file size and review clarity.
- Keep prototype as visual guide:
  - page header with admin action;
  - collapsible/conditional admin registration form;
  - active model accent marker;
  - compact model rows/cards;
  - metric bars;
  - clear empty state.
- Do not copy prototype mock behavior that conflicts with docs, especially fake datasets or local-only activation simulation.
- Use existing design system and dependencies:
  - Tailwind CSS v3 syntax;
  - shadcn-style `Button` and `Input`;
  - `@radix-ui/react-icons`;
  - no new third-party package.
- Use `DESIGN_VARIANCE=8`, `MOTION_INTENSITY=6`, `VISUAL_DENSITY=4` only within existing project constraints: asymmetric but readable model list, CSS transitions only, no added animation dependency.
- Model fixtures and assertions must explicitly cover dataset description, model size when known, full metric display, and YOLO11 fallback metadata so the page cannot pass with partial model cards.

## Frontend impact

- `/models` changes from placeholder to production page.
- New frontend API helper likely needed for:
  - `GET /models?limit=100`
  - `POST /models`
  - `PATCH /models/{model_id}/activate`
- Existing upload/dashboard model API calls can remain unchanged unless deduplication is minimal and low-risk.
- Existing `App.tsx` import should point to the new `ModelsPage`; later placeholders remain in `placeholders.tsx`.
- Tests should cover user view, admin actions, loading/error/empty states, no raw `null`, no `weights_path` display, and activation/register API calls.

## Backend impact

- No backend source changes planned.
- Use existing backend model endpoints only.
- Backend remains responsible for auth, admin checks, path safety, and relative path validation.

## DB impact

- No database changes planned.
- Existing `model_versions` storage and constraints remain source of truth.

## API impact

- No new routes, payload fields, or response fields.
- Use documented/current endpoints:
  - `GET /api/models`
  - `POST /api/models`
  - `PATCH /api/models/{model_id}/activate`
- Request body must match existing `ModelCreateRequest`.

## Security/privacy impact

- Hide register/activate controls from non-admin users.
- Still handle backend `403` as final authority.
- Do not display `weights_path` in model cards/list because it is an internal relative storage reference.
- Admin form may accept a relative weights path because backend API requires it for registration; label it clearly as storage-relative path and do not accept absolute examples.
- Add lightweight client validation for the admin weights path before submit:
  - reject absolute-looking Unix paths such as `/app/storage/...`;
  - reject Windows drive paths such as `C:\...`;
  - reject traversal-looking paths containing `..`;
  - submit only the storage-relative value to the backend.
- Backend remains the authority for final relative-path validation, and backend validation errors must render as safe Ukrainian form errors without exposing unsafe paths.
- Do not log tokens, passwords, secrets, or model storage internals.
- Do not show absolute filesystem paths from any error or response.
- Do not expose training launch controls.

## Test strategy

- Add focused frontend route tests for `/models`.
- Verify guest redirect remains protected route behavior.
- Verify regular user:
  - sees model list;
  - sees dataset description, model family, variant, active status, key metrics, model size when known, and YOLO11 fallback metadata when present;
  - sees active status and metrics;
  - does not see register or activate controls;
  - does not trigger admin endpoints.
- Verify admin:
  - sees register control;
  - submits model registration body matching backend schema;
  - cannot submit absolute-looking or traversal-looking weights paths from the client form;
  - activates inactive model through documented PATCH endpoint;
  - sees refresh/update after mutation, with the newly activated model visually active and the previously active model no longer shown as active.
- Verify loading skeleton, API error state with retry, empty state, and missing metrics placeholder.
- Verify UI never renders raw `null`, `undefined`, `frame_stride`, `/app/storage`, Windows absolute paths, or raw `weights_path`.
- Run:
  - `npm run lint`
  - `npm test`
  - `npm run build`

## Ambiguities or conflicts

- WARNING: CONFLICT: `docs/index.md` describes frontend state as Phase 24, but `frontend/index.md`, `docs/phase.md`, and actual code indicate Phase 28 is next after Phase 27. Plan follows `docs/phase.md`.
- User prompt left phase title and risk placeholders unresolved. Current phase inferred from `docs/phase.md`; risk marked MEDIUM assumption.
- Prototype contains mock model names/dataset strings. Prototype index says those are not contracts, so only visual structure should carry into implementation.
