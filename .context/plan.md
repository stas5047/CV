# Phase 11 Implementation Plan

## Scope

Phase only: admin backend APIs and safe storage cleanup.

Do not implement frontend, experiments API, worker queue, CV processing, training utilities, schema migrations, or docs/product changes.

## Ordered atomic steps

1. `@role/developer-backend` Inspect current backend route/schema/service patterns.
   - Verify files: `backend/app/api/router.py`, `backend/app/api/jobs.py`, `backend/app/api/models.py`, `backend/app/schemas/jobs.py`, `backend/app/schemas/auth.py`, `backend/app/services/results.py`.
   - Verifiable: exact existing response/list patterns identified before adding admin code.

2. `@role/developer-auth-security` Confirm admin dependency behavior.
   - Verify `get_current_admin_user` depends on active authenticated user and returns 403 for non-admin.
   - Verifiable: existing `backend/tests/test_security_utils.py` covers admin dependency.

3. `@role/developer-backend` Define admin API response/request schemas only from documented safe fields.
   - Create `backend/app/schemas/admin.py`.
   - Include no password hashes, tokens, absolute paths, or storage-root values.
   - Prefer cleanup response counts and categories over path lists.
   - If path-like cleanup details are returned, expose only relative/logical paths.
   - If exact stats/cleanup JSON fields cannot be derived without inventing safe behavior, stop for user decision.
   - Verifiable: schema fields map to existing documented DB/API concepts.

4. `@role/developer-backend` Add admin service module.
   - Create `backend/app/services/admin.py`.
   - Add service functions for global stats, global jobs, basic users, and cleanup.
   - Keep route handlers thin.
   - Verifiable: routes will call service functions; no DB logic embedded in router.

5. `@role/developer-backend` Implement global stats query.
   - Aggregate only from existing documented tables.
   - Include no user secrets and no filesystem paths.
   - Verifiable: admin stats endpoint returns deterministic aggregate values in tests.

6. `@role/developer-backend` Implement global admin job history.
   - Prefer reuse of existing safe job detail/list response logic.
   - Enforce admin-only route even if underlying service can list all for admins.
   - Preserve pagination and relevant filters only if already supported safely.
   - Verifiable: admin sees all non-deleted jobs; regular user cannot call route.

7. `@role/developer-backend` Implement basic admin users list.
   - Use safe user fields only.
   - Support pagination because users can grow.
   - Exclude `password_hash`.
   - Verifiable: response text never contains password hash values.

8. `@role/developer-auth-security` Design cleanup protection set.
   - Collect relative paths that must not be deleted from documented DB fields.
   - Include non-deleted media/job references and active model artifacts.
   - Protect active model `weights_path` and the derived active model directory, including `models/{model_version_id}/model_card.json` when derivable from documented layout.
   - Treat referenced directories as protected prefixes, including `experiment_runs.artifacts_path` and derived active model directories.
   - Treat invalid/absolute DB paths as protected skip/error, not delete targets.
   - Verifiable: tests prove referenced files and descendants under referenced directories remain.

9. `@role/developer-auth-security` Implement conservative cleanup behavior.
   - Operate only under `STORAGE_ROOT` through `safe_join_storage_path`.
   - Do not delete active model weights/cards, referenced files, visible completed job files, or ambiguous recent result files.
   - Do not physically delete files from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/` in Phase 11 because no retention window is documented.
   - If physical deletion is implemented, limit it to clearly safe unreferenced files under `temp/`.
   - Return only safe relative/logical cleanup information.
   - Log safe counts/actions only.
   - Verifiable: cleanup cannot remove protected fixtures or a fresh unreferenced `results/` file, deletes only eligible `temp/` files if deletion is implemented, and cannot report absolute paths.

10. `@role/developer-backend` Add admin router.
    - Create `backend/app/api/admin.py`.
    - Routes:
      - `GET /admin/stats`
      - `GET /admin/jobs`
      - `GET /admin/users`
      - `POST /admin/storage/cleanup`
    - Use `get_current_admin_user` on every route.
    - Verifiable: generated routes appear under `/api/admin/*`.

11. `@role/developer-backend` Include admin router.
    - Modify `backend/app/api/router.py`.
    - Verifiable: `GET /api/admin/stats` resolves in TestClient.

12. `@role/tester` Add admin API tests.
   - Create `backend/tests/test_admin_api.py`.
   - Cover guest, regular user, inactive admin, and active admin access.
   - Cover global jobs/users/stats behavior.
   - Cover cleanup safety and no absolute path exposure.
   - Cover active model card/directory protection when only `weights_path` is stored.
   - Cover referenced directory prefix protection for experiment artifacts.
   - Cover fresh unreferenced `results/` file preservation.
   - Cover temp-only physical deletion if cleanup deletes any files in Phase 11.
   - Verifiable: targeted test file fails before implementation and passes after implementation.

13. `@role/tester` Run targeted admin tests.
    - Command: `python -m pytest tests/test_admin_api.py`
    - Workdir: `backend/`
    - Expected: PASS.

14. `@role/tester` Run backend lint.
    - Command: `python -m ruff check .`
    - Workdir: `backend/`
    - Expected: PASS.

15. `@role/tester` Run backend suite if targeted checks pass.
    - Command: `python -m pytest`
    - Workdir: `backend/`
    - Expected: PASS.

16. `@role/code-reviewer` Review phase scope and safety.
    - Check no frontend/worker/training/schema/product-doc changes.
    - Check all admin routes require admin role.
    - Check cleanup cannot delete protected files.
    - Check responses/logs omit secrets and absolute paths.
    - Verifiable: review notes no scope creep or lists exact blockers.

17. `@role/docs-maintainer` Update `backend/index.md` because Phase 11 creates backend admin files and the component index must stay current.
    - Do not update product docs.
    - Verifiable: index mentions admin API files honestly and keeps commands accurate.

## Quality gates for phase

- `python -m pytest tests/test_admin_api.py` from `backend/`
- `python -m ruff check .` from `backend/`
- `python -m pytest` from `backend/`

## Explicit non-goals

- No frontend admin page.
- No experiments endpoints.
- No model training/import changes.
- No worker cleanup task.
- No hard deletion of DB rows.
- No deletion outside `STORAGE_ROOT`.
- No physical deletion from `uploads/`, `results/`, `reports/`, `models/`, or `datasets/` without a future documented retention policy.
- No new roles beyond `user` and `admin`.
- No exposure of absolute paths or password hashes.
