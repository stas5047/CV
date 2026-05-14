## Phase 14 - CV worker scaffold, settings, logging, and database access

**Direction:** CV Worker  
**Goal:** Create the separate worker service foundation without implementing full inference yet.

### Scope

- Scaffold `cv/` Python project.
- Add dependencies for SQLAlchemy, PostgreSQL driver, Pydantic settings, PyTorch/Ultralytics placeholder, OpenCV headless, NumPy, pandas, and tests.
- Implement worker settings for database, storage, device, polling, heartbeat, stale-job threshold, and max retries.
- Implement safe logging that does not expose secrets or absolute paths in user-facing messages.
- Implement database session layer for worker.
- Implement startup logs including selected/desired `CV_DEVICE` configuration.
- Implement storage path resolution under `/app/storage` using relative paths from the database.
- Add worker Dockerfile and Compose integration.
- Add basic worker health/startup smoke tests where practical.

### Relevant docs

- `docs/ARCHITECTURE.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/AUTH_SECURITY.md`
- `docs/TESTING_QA.md`

### Validation

- Worker container starts in Docker Compose.
- Worker logs selected device configuration on startup.
- Worker can connect to PostgreSQL.
- Worker can resolve safe relative storage paths.
- Worker does not call backend over HTTP for job polling.
- Worker smoke tests pass.

### Commit

`feat(worker): scaffold CV worker settings logging and database access`