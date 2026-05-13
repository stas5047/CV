# Phase 3 Plan - Database schema and initial Alembic migration

1. `@role/developer-db` Confirm current backend DB foundation.
   - Verify `backend/app/db/session.py`, existing dependencies, and absence of Alembic/model files.
   - Output evidence in implementation notes or final report.

2. `@role/developer-db` Create SQLAlchemy declarative metadata.
   - Add shared base/metadata for all Phase 3 models.
   - Verification: model metadata lists all required table names.

3. `@role/developer-db` Add enum/check representation for documented fixed values.
   - Cover user roles, media types, job statuses, and experiment types.
   - Verification: invalid values fail in database/model tests.

4. `@role/developer-db` Add `users` model.
   - Include required fields, unique email, role constraint, active flag, created/updated timestamps.
   - Verification: duplicate email rejected; invalid role rejected.

5. `@role/developer-db` Add `media_files` model.
   - Include owner FK, metadata fields, relative stored path, soft deletion, timestamps, and user/date index.
   - Verification: FK works; media type constraint works; index exists; image media rejects `frame_count != 1`, non-null `fps`, and non-null `duration_seconds`.

6. `@role/developer-db` Add `model_versions` model.
   - Include documented metadata, relative weights path, metrics JSON, active flag, creator FK, timestamps.
   - Verification: only one active model row allowed; multiple inactive model rows allowed; weights path rejects unsafe paths where database check exists.

7. `@role/developer-db` Add `processing_jobs` model.
   - Include owner FK, media FK, model FK, status, params JSON, summary JSON, result/export paths, error/progress/lock/retry/time fields, soft deletion, timestamps.
   - Verification: status constraint works; progress range works; queue/history/media indexes exist.

8. `@role/developer-db` Add `detections` model.
   - Include job/media FKs, frame/timestamp/class/confidence/bbox/frame size/track ID fields and timestamp.
   - Verification: FKs work; job/frame and media/frame indexes exist.

9. `@role/developer-db` Add `tracks` model.
   - Include job FK, track ID, class, frame range, count, confidence summary, timestamp.
   - Verification: unique `(job_id, track_id)` rejected; lookup index exists.

10. `@role/developer-db` Add `experiment_runs` and `experiment_metrics` models.
    - Include experiment type, publication state, model/admin FKs, config/artifact fields, metric values, metadata JSON, timestamps.
    - Verification: experiment type constraint works; experiment indexes exist; nullable metric value accepted.

11. `@role/developer-db` Add practical relative-path database checks.
   - Apply to documented path fields where feasible without replacing later service path utilities.
   - Verification: Unix absolute paths, Windows drive-letter paths, UNC-style paths, and `..` traversal segments fail in smoke tests where database checks are implemented.

12. `@role/developer-db` Add Alembic configuration and initial migration.
    - Wire Alembic env to backend settings and SQLAlchemy metadata.
    - Generate or write initial migration from current models.
    - Verification: `alembic upgrade head` applies on fresh PostgreSQL database.

13. `@role/tester` Add focused database smoke tests.
    - Cover Alembic metadata table registration, table existence, indexes, key constraints, FKs, image metadata invariants, active model uniqueness, multiple inactive models, nullable metric values, and path checks.
    - Keep tests Phase 3 only; no auth/API/worker behavior tests.
    - Verification: `python -m pytest` passes from `backend/`.

14. `@role/tester` Run relevant gates.
    - `python -m ruff check .`
    - `python -m pytest`
    - Alembic migration apply against fresh PostgreSQL.
    - Alembic migration inside backend container when Compose database is available.

15. `@role/code-reviewer` Review Phase 3 scope and doc fit.
    - Check no source work from later phases slipped in: auth endpoints, seed, uploads, jobs APIs, worker logic, frontend UI, training, Celery/Redis.
    - Check no binary files, generated storage contents, secrets, or absolute stored paths.
    - Verification: final review notes cite docs and touched files.

16. `@role/docs-maintainer` Update only implementation indexes if commands or backend contents changed.
    - Product docs stay unchanged.
    - Verification: `backend/index.md` updated only if implementation changes available commands/current files; `docs/index.md` unchanged unless source-of-truth docs change.
