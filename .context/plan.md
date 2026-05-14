# Phase 19 Implementation Plan - Worker CSV/JSON exports and no-detection contracts

## Scope

Only Phase 19 worker export behavior. Do not modify product docs. Do not modify frontend, training, auth, upload, model registry, admin, Docker, or unrelated backend code.

## Ordered atomic plan

1. `@role/developer-cv-worker` Re-read Phase 19 relevant docs before source edits.
   - Files: `docs/API.md`, `docs/CV_PIPELINE.md`, `docs/DATA_MODEL.md`, `docs/PROJECT_CONTEXT.md`, and `docs/TESTING_QA.md`.
   - Verify: required CSV columns, required JSON top-level keys, no-detection rules, relative path rules, CV-only boundary are listed in notes before editing.

2. `@role/tester` Run current focused export tests to establish baseline.
   - Command: `cd cv; python -m pytest tests/test_image_processing.py tests/test_video_processing.py -q`
   - Verify: PASS means implementation may only need contract hardening; FAIL means preserve failing output for fix.

3. `@role/developer-cv-worker` Audit `cv/aerovision_worker/image_processing.py`.
   - Verify `CSV_COLUMNS` exactly equals documented column list and order.
   - Verify `_export_detection` computes `center_x`, `center_y`, `bbox_width`, `bbox_height` from bbox corners.
   - Verify `_write_csv_export` writes headers before rows.
   - Verify `_write_json_export` includes only top-level `job`, `media`, `model`, `parameters`, `summary`, `detections`, `tracks`.
   - Verify no-detection path writes CSV/JSON before completion update.

4. `@role/developer-cv-worker` Audit `cv/aerovision_worker/video_exports.py`.
   - Verify video CSV uses same `CSV_COLUMNS`.
   - Verify `write_json_export` includes required top-level objects/arrays.
   - Verify `build_track_summaries` excludes null `track_id` and summarizes video tracking only.
   - Verify `result_paths` stores relative `results/{job_id}/...` paths.

5. `@role/developer-cv-worker` Audit `cv/aerovision_worker/video_processing.py` and `cv/aerovision_worker/video_persistence.py`.
   - Verify CSV/JSON exports are generated for completed video jobs before DB completion update.
   - Verify no-detection videos still produce annotated MP4 when possible.
   - Verify completed DB update stores `csv_path` and `json_path` as relative values.
   - Verify export write failures call `fail_processing_job` with safe generic errors.

6. `@role/developer-cv-worker` If audit finds missing export contract behavior, patch only affected worker modules.
   - Allowed files:
     - `cv/aerovision_worker/image_processing.py`
     - `cv/aerovision_worker/video_exports.py`
     - `cv/aerovision_worker/video_processing.py`
     - `cv/aerovision_worker/video_persistence.py`
     - `cv/aerovision_worker/video_types.py`
   - Verify: no backend/frontend/docs files changed for worker-only fixes.

7. `@role/developer-cv-worker` Add or tighten image export tests only if needed.
   - File: `cv/tests/test_image_processing.py`
   - Required assertions:
     - CSV fieldnames exactly match docs.
     - CSV row count equals detection count.
     - Derived center-size values match bbox corners.
     - JSON top-level keys match docs.
     - No-detection CSV rows list is empty after header.
     - No-detection JSON `detections` equals `[]`.
     - No-detection JSON `summary` has `total_detections = 0`, `frames_with_detections = 0`, `average_confidence = null`, and `maximum_confidence = null`.
     - Persisted no-detection job `summary_json` has the same zero/null summary values where available in the test fixture.
     - JSON/export text omits absolute `storage_root` and forbidden boundary terms.
   - Verify: tests fail before missing fix when behavior is absent, then pass after fix.

8. `@role/developer-cv-worker` Add or tighten video export tests only if needed.
   - File: `cv/tests/test_video_processing.py`
   - Required assertions:
     - CSV fieldnames exactly match docs.
     - CSV row count equals detection count.
     - JSON top-level keys match docs.
     - JSON `tracks` includes only summarized non-null track IDs.
     - No-detection CSV rows list is empty after header.
     - No-detection JSON has `detections: []` and `tracks: []`.
     - No-detection JSON `summary` has `total_detections = 0`, `frames_with_detections = 0`, `average_confidence = null`, and `maximum_confidence = null`.
     - Persisted no-detection job `summary_json` has the same zero/null summary values where available in the test fixture.
     - Export paths are relative and files exist.
     - JSON/export text omits absolute `storage_root` and forbidden boundary terms.
   - Verify: tests fail before missing fix when behavior is absent, then pass after fix.

9. `@role/tester` Run focused worker export tests.
   - Command: `cd cv; python -m pytest tests/test_image_processing.py tests/test_video_processing.py -q`
   - Expected: PASS.

10. `@role/tester` Run worker lint for touched worker/test surface.
    - Command: `cd cv; python -m ruff check aerovision_worker tests`
    - Expected: PASS.

11. `@role/code-reviewer` Review changed files against `docs/API.md`, `docs/CV_PIPELINE.md`, `docs/DATA_MODEL.md`, `docs/PROJECT_CONTEXT.md`, and `docs/TESTING_QA.md`.
    - Verify no API/schema/UI/docs/runtime-service scope creep.
    - Verify CSV/JSON export contracts.
    - Verify no-detection success behavior.
    - Verify relative path storage.
    - Verify CV-only output boundary.
    - Verify no secrets or absolute paths in export/error output.

12. `@role/docs-maintainer` Decide docs/index updates.
    - Expected: skipped unless implementation changes commands, structure, env variables, artifact layout, or documented file paths.
    - Verify: if skipped, final report says docs/index updates skipped because no documented paths/commands changed.

## Relevant quality gates

- `cd cv; python -m pytest tests/test_image_processing.py tests/test_video_processing.py -q`
- `cd cv; python -m ruff check aerovision_worker tests`

Not in scope:

- Backend full suite unless backend files change.
- PostgreSQL queue integration unless queue/persistence semantics change.
- Frontend checks.
- Docker Compose smoke.

## Stop conditions

- Stop and report `WARNING: CONFLICT` if implementation, `.context`, or docs disagree on export fields, no-detection success, relative paths, or CV-only boundary.
- Stop before source edits if a required JSON nested field is unclear and cannot be inferred from docs without inventing behavior.
- Do not mark complete with failing focused gates unless exact failing command/output is documented as blocker.
