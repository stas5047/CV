# Verdict: APPROVED_WITH_CHANGES

## Summary

Phase 15 plan matches main product boundary: worker-only PostgreSQL queue work, no backend API, no frontend, no model loading, no inference, no tracking/export implementation. Architecture direction is correct: `FOR UPDATE SKIP LOCKED`, short claim transaction, PostgreSQL/shared-storage boundary preserved, no Celery/Redis, no backend-worker HTTP job loop.

Plan needs tightening before implementation on three real risks: stale recovery must ignore soft-deleted jobs, heartbeat/progress writes must be scoped to the claiming worker, and PostgreSQL concurrency validation must not be treated as optional if phase claims queue reliability.

## Blocking issues

None.

## Important issues

1. Stale recovery plan does not explicitly exclude soft-deleted jobs.
   - Evidence: `.context/plan.md` step 3 filters queued claims to non-deleted jobs, but step 6 only says "Find stale `processing` jobs older than configured threshold." `docs/DATA_MODEL.md` requires `processing_jobs.deleted_at` soft deletion and says soft-deleted records are hidden from normal user lists and should not be physically removed. A stale-recovery update that resets or fails soft-deleted processing rows could mutate deleted/audit records and potentially resurrect queue work. Add `deleted_at IS NULL` to stale recovery selection/update criteria.

2. Heartbeat/progress helper lacks explicit lock-owner guard.
   - Evidence: `.context/plan.md` step 5 updates progress and heartbeat for a "currently claimed processing job" but does not require matching `locked_by`. `docs/ARCHITECTURE.md` requires claimed jobs to set `locked_by`, `locked_at`, and heartbeat fields. Without `job_id + locked_by + status = processing` conditions, an old worker instance can update a job after stale recovery requeues it or another worker claims it, weakening queue ownership and stale detection.

3. PostgreSQL concurrency test is too easy to skip.
   - Evidence: `.context/plan.md` step 10 says add PostgreSQL-specific concurrency coverage "when available" and otherwise report `not available yet`. `docs/phase.md` validation requires "Two workers do not claim the same job" and `docs/TESTING_QA.md` requires proving PostgreSQL row-level locking and short claim transactions. Because `FOR UPDATE SKIP LOCKED` behavior cannot be proven with SQLite/unit tests, implementation plan should define a concrete PostgreSQL integration command or explicitly mark lack of PostgreSQL as a phase blocker, not a routine `not available yet`.

## Optional improvements

- Add explicit status transition guards for stale recovery updates, for example update only rows still `status = 'processing'` at update time. This reduces race risk between recovery and worker heartbeats.
- Make timeout `error_message` stable and safe, e.g. short worker-timeout text without paths, DB URLs, secrets, tokens, or stack traces. Plan already says safe error, but exact invariant helps review.
- Clarify placeholder processing behavior in Phase 15 main loop. If loop claims real jobs before Phase 16 processing exists, define whether placeholder handler fails safely, leaves job for stale recovery, or is test-only. Avoid accidental permanent `processing` rows in local/demo runs.

## Questions for resolution

- Risk level was left as literal `<MEDIUM | HIGH>` in the prompt. Planning artifacts assume `MEDIUM`. Confirm if this phase should be treated as `HIGH` because it touches DB concurrency.
- What PostgreSQL integration path should implementation use for the two-worker claim test: existing Docker Compose database, a testcontainer-style harness, or a documented manual command?

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`
- `git status --short` output
