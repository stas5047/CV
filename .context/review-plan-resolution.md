# Phase 15 Planning Review Resolution

## Verdict: READY_FOR_IMPLEMENTATION

Claude review verdict was `APPROVED_WITH_CHANGES`. No blocking source-of-truth conflict found. Accepted changes were applied only to `.context/design.md` and `.context/plan.md`. `.context/research.md` did not require contract changes.

## Resolution table

| ID | Claude item | Resolution | Reason | Applied to |
|---|---|---|---|---|
| I1 | Stale recovery must explicitly exclude soft-deleted jobs. | accepted | `docs/DATA_MODEL.md` requires `processing_jobs.deleted_at` soft deletion; queue recovery should not mutate deleted/audit rows. | `.context/design.md`, `.context/plan.md` |
| I2 | Heartbeat/progress helper needs explicit lock-owner guard. | accepted | `locked_by` is part of queue ownership; updates must be scoped to `job_id + locked_by + status = processing` to avoid stale worker writes. | `.context/design.md`, `.context/plan.md` |
| I3 | PostgreSQL concurrency test is too easy to skip. | accepted | `docs/phase.md` and `docs/TESTING_QA.md` require proving two workers cannot claim the same job; SQLite/unit tests cannot prove `FOR UPDATE SKIP LOCKED`. | `.context/design.md`, `.context/plan.md` |
| O1 | Add explicit status transition guards for stale recovery updates. | accepted | Race guard aligns with queue reliability and does not conflict with docs. | `.context/design.md`, `.context/plan.md` |
| O2 | Make timeout `error_message` stable and safe. | accepted | Matches security/logging and safe API error requirements. | `.context/design.md`, `.context/plan.md` |
| O3 | Clarify placeholder processing behavior in Phase 15 main loop. | accepted | Prevents real claimed jobs from remaining permanently `processing` before Phase 16 processing exists. Scope remains queue-only. | `.context/design.md`, `.context/plan.md` |
| Q1 | Confirm whether phase risk should be `HIGH` instead of assumed `MEDIUM`. | rejected | Risk label is not a product-doc contract and does not change required implementation or gates. Phase remains governed by `docs/phase.md` and accepted queue-reliability gates. | none |
| Q2 | Choose PostgreSQL integration path. | accepted | Use existing Docker Compose Postgres as concrete path unless implementation discovers an existing better harness. Lack of runnable PostgreSQL gate is blocker for queue-reliability completion. | `.context/design.md`, `.context/plan.md` |

## Accepted changes applied

- Stale recovery selection/update must include `deleted_at IS NULL`.
- Stale recovery updates must guard on rows still being `status = 'processing'`.
- Heartbeat/progress updates must match `job_id`, current worker `locked_by`, and `status = 'processing'`.
- Timeout and placeholder failure messages must be short, stable, and free of paths, DB URLs, secrets, tokens, and stack traces.
- Phase 15 runtime placeholder for real claimed jobs must fail safely instead of leaving jobs permanently `processing`.
- PostgreSQL queue validation uses:
  - root: `docker compose --env-file .env.example up -d postgres`
  - `cv/`: `python -m pytest -m postgres`
- If PostgreSQL queue validation cannot run, Phase 15 queue-reliability completion is blocked; SQLite/unit tests alone are insufficient.

## Rejected items

- Q1 risk-level confirmation rejected as implementation-contract change. Source docs define phase scope and gates; no user decision needed.

## Duplicate items

- None.

## Items needing user decision

- None.

## Final contract status

- Final Phase 15 contract is ready for implementation.
- Scope remains worker queue claiming, heartbeat/progress helpers, stale recovery, polling/shutdown behavior, and tests only.
- No backend API, frontend, DB migration, inference, tracking, exports, detections, result media, or training work added.
