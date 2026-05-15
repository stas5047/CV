# Codex Mistake Log

## 2026-05-15 - Phase 32 worker Dockerfile fix initially invalidated heavy dependency cache

- Mistake: First added OpenCV native OS packages before the worker Python dependency install layer.
- Impact: `docker compose --env-file .env.example build cv-worker` spent 10 minutes rebuilding heavy Python dependencies and timed out before verification.
- Fix: Moved the OS package install after the existing Python dependency layer, preserving Docker cache for `torch`/Ultralytics dependencies while still adding runtime libraries.
- Prevention: For Dockerfiles with heavy dependency layers, place small runtime-library fixes after cached dependency layers when build correctness allows it.

## 2026-05-15 - Playwright module smoke attempt used unavailable `npx --package` path

- Mistake: Tried to run a browser-smoke helper through `npx --package playwright node`, but this environment did not expose the Playwright package to `require("playwright")`.
- Impact: Browser smoke did not run from that attempt and cost a verification step.
- Fix: Stopped the browser-smoke attempt after the user explicitly said browser checks are user-owned for this pass.
- Prevention: In this environment, do not assume `npx --package` exposes Playwright to arbitrary Node scripts. Use the project test runner or skip browser checks when the user owns them.

## 2026-05-15 - Phase 29 frontend Ukrainian text was committed as mojibake

- Mistake: Phase 29 `/experiments` visible Ukrainian strings and test expectations were corrupted into mojibake, and tests imported the implementation empty-state constant instead of asserting the docs literal.
- Impact: Frontend gates passed while the page failed the Ukrainian UI and exact experiment empty-state requirements.
- Fix: Replaced corrupted strings with real Ukrainian, set the exact docs-required empty-state literal, and changed tests to assert that literal directly.
- Prevention: For Ukrainian UI work, scan touched frontend files for mojibake fragments and keep tests anchored to docs-required literals rather than implementation constants.

## 2026-05-14 - Phase 25 Playwright storage state written with BOM

- Mistake: Wrote temporary Playwright storage-state JSON with PowerShell `Set-Content -Encoding UTF8`, which produced a BOM.
- Impact: First dashboard browser-smoke attempt failed with `Unexpected token` while reading storage state and produced no screenshots.
- Fix: Rewrote the temp storage-state file with BOM-free `System.Text.UTF8Encoding(false)` and reran the smoke successfully.
- Prevention: For Playwright JSON artifacts on Windows, write temp JSON with BOM-free UTF-8.

## 2026-05-14 - Phase 25 frontend test command used unsupported Vitest option

- Mistake: Ran `npm test -- --runInBand`, which is a Jest option and is not supported by this project's Vitest version.
- Impact: First test attempt failed before running tests with `Unknown option --runInBand`.
- Fix: Reran the documented command `npm test`.
- Prevention: Use project-documented frontend test command unless `package.json` confirms additional runner options.

## 2026-05-14 - Phase 24 dev server start used `npm` instead of `npm.cmd` on Windows

- Mistake: Started the Vite dev server with `Start-Process -FilePath npm`, which followed Windows file association behavior and launched `notepad` instead of the npm CLI.
- Impact: Initial browser smoke saw `ERR_CONNECTION_REFUSED` because the dev server was not running.
- Fix: Closed the accidental `notepad` process and restarted with `Start-Process -FilePath npm.cmd`.
- Prevention: On Windows, use `npm.cmd` explicitly when launching npm through `Start-Process`.

## 2026-05-14 - Phase 21 training package discovery included non-package folders

- Mistake: Initial `training/pyproject.toml` relied on setuptools automatic package discovery while `training/` also contained `notebooks/` and `templates/`.
- Impact: `python -m pip install -e "training[dev]"` failed before package install with `Multiple top-level packages discovered`.
- Fix: Added explicit setuptools package discovery for `aerovision_training*` and excluded tests/templates/notebooks.
- Prevention: When a Python package folder contains non-package artifact directories, configure package discovery before running install gates.

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
