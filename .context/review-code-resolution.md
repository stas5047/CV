# Code Review Resolution - Phase 14

## Verdict: FIXED

Code review items were checked against `docs/phase.md`, `docs/CV_PIPELINE.md`, `.context/plan.md`, and current worker code. One important issue is accepted. No critical, optional, duplicate, or user-decision items block implementation.

## Resolution table

| ID | Source | Priority | Review item | Resolution | Rationale | Planned fix |
|---|---|---|---|---|---|---|
| OAI-1 | `.context/review-code-openai.md` | important | `CV_DEVICE=cuda` unavailable is retried and reported as database unavailable. | accepted | Docs and accepted plan require forced CUDA to fail clearly when unavailable. Current `run_worker()` wraps device selection inside `wait_for_database()`, and `wait_for_database()` catches all exceptions. | Move DB retry around database connectivity only and add startup regression test that `DeviceUnavailableError` fails immediately. |

## Accepted critical fixes

- None.

## Accepted important fixes

- Fix startup retry boundaries so `DeviceUnavailableError("CUDA requested but unavailable")` is not converted into `RuntimeError("database unavailable after ... attempts")`.
- Add startup-level regression test for unavailable forced CUDA.

## Accepted optional fixes

- None.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Fixes applied

- Changed `cv/aerovision_worker/main.py` so `run_worker()` performs device selection before the database retry wrapper and retries only the database connectivity check.
- Added `cv/tests/test_startup.py` regression coverage proving `CV_DEVICE=cuda` unavailable raises `DeviceUnavailableError` before database checks/retries.
- Updated `docs/index.md` current implementation state so the CV worker scaffold is no longer described as placeholder-only.

## Final verification

- `python -m pytest tests\test_startup.py` from `cv/`: PASS, 3 passed.
- `python -m pytest` from `cv/`: PASS, 32 passed.
- `python -m ruff check .` from `cv/`: PASS, `All checks passed!`.
- `docker compose --env-file .env.example config`: PASS.
- `python -m aerovision_worker.main --check-once` from `cv/` with `DATABASE_URL=sqlite+pysqlite:///:memory:` and `CV_DEVICE=cpu`: PASS.
- `python -m pip install -e ".[dev]"` from `cv/`: FAIL, timed out after 124 seconds while installing/checking dependencies.
- `docker compose --env-file .env.example build cv-worker`: FAIL, command timed out after 124 seconds.
