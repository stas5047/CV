# Codex Mistake Log

## 2026-05-14 - Phase 13 boundary scan covered errors but missed success responses

- Mistake: Initial Phase 13 API contract test reused the response safety helper only for error payloads, not representative successful JSON responses.
- Impact: The phase claimed API output boundary coverage without proving successful media, jobs/results, models, experiments, and admin responses avoided internal paths and forbidden CV-boundary terms.
- Fix: Added successful-response contract coverage across representative implemented JSON endpoints.
- Prevention: When a plan says "representative API responses," include both error and success payloads before marking boundary audit complete.

## 2026-05-14 - Phase 12 tracker wording guard matched only exact forbidden terms

- Mistake: Initial tracker-comparison validation rejected exact `tracking_accuracy`, `MOTA`, `IDF1`, and `HOTA` strings but allowed variants such as `mota_score`, `tracking_accuracy_score`, and metadata label `IDF1 metric`.
- Impact: Admin import could expose API-facing tracker metrics that violated the documented behavior-comparison boundary.
- Fix: Added separator-insensitive embedded-term rejection and regression tests for variant metric names and metadata text.
- Prevention: When docs forbid terminology, test exact terms, suffixed/prefixed metric names, spaced labels, and nested metadata.

## 2026-05-13 - Phase 4 Docker smoke ran dependent migration and seed in parallel

- Mistake: Ran `docker compose ... alembic upgrade head` and `docker compose ... python -m app.setup` in parallel even though seed depends on migrated tables.
- Impact: Seed smoke briefly failed with `relation "users" does not exist`.
- Fix: Reran seed only after migration completed; seed then passed.
- Prevention: Do not parallelize dependent quality gates. Run migration before seed/setup.

## 2026-05-13 - Phase 3 database constraints missed SQL NULL and terminal traversal cases

- Mistake: Initial image-media check used `frame_count = 1` without `frame_count IS NOT NULL`, so SQL `CHECK` accepted `UNKNOWN` and allowed image rows with `frame_count = NULL`.
- Mistake: Initial relative-path check rejected leading and middle `..` segments but allowed terminal `models/..` and `models\..`.
- Fix: Added explicit image `frame_count IS NOT NULL`, terminal traversal rejects, and regression tests for both cases.
- Prevention: For SQL checks, test NULL behavior explicitly; for path segment checks, test leading, middle, and terminal traversal segments.
