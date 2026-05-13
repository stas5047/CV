# Codex Mistake Log

## 2026-05-13 - Phase 3 database constraints missed SQL NULL and terminal traversal cases

- Mistake: Initial image-media check used `frame_count = 1` without `frame_count IS NOT NULL`, so SQL `CHECK` accepted `UNKNOWN` and allowed image rows with `frame_count = NULL`.
- Mistake: Initial relative-path check rejected leading and middle `..` segments but allowed terminal `models/..` and `models\..`.
- Fix: Added explicit image `frame_count IS NOT NULL`, terminal traversal rejects, and regression tests for both cases.
- Prevention: For SQL checks, test NULL behavior explicitly; for path segment checks, test leading, middle, and terminal traversal segments.
