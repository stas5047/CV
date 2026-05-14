## Phase 15 - PostgreSQL queue claiming, heartbeat, and stale job recovery

**Direction:** CV Worker / Queue  
**Goal:** Implement reliable PostgreSQL job queue behavior before media processing.

### Scope

- Implement polling loop for queued jobs.
- Implement job claiming with `FOR UPDATE SKIP LOCKED`.
- Keep claim transaction short.
- Set `status = processing`, `locked_by`, `locked_at`, `started_at`, and `last_heartbeat_at` during claim.
- Ensure processing happens outside the claim transaction.
- Implement heartbeat/progress update helpers.
- Implement stale job recovery:
  - detect stale `processing` jobs;
  - reset to `queued` and increment `retry_count` when retry count is below max;
  - mark as `failed` when retry count reaches max.
- Add tests or integration tests showing two workers cannot claim the same job.
- Add worker shutdown behavior as practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`

### Validation

- Worker claims oldest queued job.
- Two workers do not claim the same job.
- Claim transaction is not held during simulated processing.
- Heartbeat/progress updates work.
- Stale jobs reset or fail according to retry count.
- Worker restart does not leave jobs permanently stuck in `processing`.

### Commit

`feat(worker-queue): add Postgres job claiming heartbeat and stale recovery`