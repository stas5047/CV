# Plan - Phase 21 Training Pipeline Artifacts

## Scope

Phase only: offline training scripts, notebook templates, dataset preparation, deterministic split manifest, one-class YOLO config generation, model card/metrics schemas, tiny local smoke option, and training instructions. No source runtime implementation, no API, no database migration, no frontend work.

## Ordered atomic plan

1. `@role/developer-training` Inspect existing `training/` contents and choose minimal new file layout inside `training/` for scripts, templates, schemas, tests, and instructions.
   - Verifiable: chosen layout stays under `training/`; no new top-level product folder.

2. `@role/developer-training` Define training-local dependency and command strategy before adding scripts.
   - Verifiable: if non-stdlib dependencies are introduced, a training-local manifest or documented install command exists; if no install command exists yet, `training/index.md` says `not available yet`.

3. `@role/developer-training` Define dataset preparation contract for Seraphim YOLO-compatible output.
   - Verifiable: contract writes/creates `storage/datasets/seraphim_subset/images/{train,val,test}`, `storage/datasets/seraphim_subset/labels/{train,val,test}`, `data.yaml`, and `split_manifest.csv`.

4. `@role/developer-training` Implement deterministic split utility with seed `42`.
   - Verifiable: same input fixture produces identical `split_manifest.csv` on repeated runs.

5. `@role/developer-training` Add group-aware split behavior.
   - Verifiable: when source/sequence/video/group metadata exists, same `source_group_id` never appears in more than one split.

6. `@role/developer-training` Add deterministic per-image fallback split when group metadata is absent.
   - Verifiable: manifest still has `source_group_id` column, empty where unavailable, and split values only `train`, `val`, `test`.

7. `@role/developer-training` Generate YOLO `data.yaml` for exactly one class.
   - Verifiable: `data.yaml` has `nc: 1` and names contain only `drone`.

8. `@role/developer-training` Add model card schema/template for trained and placeholder model records.
   - Verifiable: required fields exist: `name`, `model_family`, `variant`, `task`, `classes`, `dataset`, `split_manifest`, `train_images`, `val_images`, `test_images`, `image_size`, `epochs`, `metrics`.

9. `@role/developer-training` Add metrics schema/template for detection, performance, and all four documented experiment families.
   - Verifiable: precision, recall, mAP@0.5, mAP@0.5:0.95, confusion matrix reference, model size, latency, FPS, total processing time, and average video FPS are represented; model comparison, confidence threshold analysis, tracker behavior comparison, and false-positive analysis artifacts validate with incomplete or `null` metrics where docs allow.

10. `@role/developer-training` Add explicit model comparison artifact guidance.
    - Verifiable: guidance compares YOLO26n and YOLO26s, or documented YOLO11n/YOLO11s fallback, with precision, recall, mAP@0.5, mAP@0.5:0.95, latency, FPS, and model size.

11. `@role/developer-training` Add explicit confidence threshold analysis artifact guidance.
    - Verifiable: guidance covers thresholds `0.25`, `0.50`, and `0.70` for the final main model and describes recall versus false-positive trade-off without changing runtime defaults.

12. `@role/developer-training` Add tracker behavior comparison artifact guidance.
    - Verifiable: wording says tracker behavior comparison, not absolute tracking accuracy; covers ByteTrack and BoT-SORT; does not require MOTA, IDF1, HOTA, or manual track identity labels.

13. `@role/developer-training` Add false-positive analysis artifact guidance.
    - Verifiable: Bird vs Drone data is described only as false-positive analysis, not training class or primary dataset replacement.

14. `@role/developer-training` Add minimal offline artifact validation/import-readiness utility for model cards and metrics.
    - Verifiable: utility validates local model card/metrics artifacts and relative paths only; it does not add backend routes, database writes, frontend flows, or runtime training launch.

15. `@role/developer-training` Add YOLO26n and YOLO26s Kaggle/Colab notebook templates.
    - Verifiable: templates use pretrained YOLO weights, task `detect`, image size `640`, seed `42`, one class `drone`, and do not launch from web UI/API.

16. `@role/developer-training` Add documented YOLO11 fallback path inside training artifacts.
    - Verifiable: fallback is labeled fallback-only, maps YOLO26n to YOLO11n and YOLO26s to YOLO11s, and requires model card/experiment metadata to record actual family.

17. `@role/developer-training` Add tiny local smoke training option.
    - Verifiable: command is limited to tiny subset/low epoch verification and documentation says smoke output is not final model/evaluation evidence.

18. `@role/developer-training` Add artifact layout guidance for humans.
    - Verifiable: instructions point to `storage/models/<model-version>/weights.pt`, `model_card.json`, and `metrics.json`, with relative references in artifacts.

19. `@role/developer-training` Add tests for split utility using tiny synthetic fixture.
    - Verifiable: test covers deterministic output, manifest columns, valid split names, and group no-leak behavior.

20. `@role/developer-training` Add tests for `data.yaml` generation.
    - Verifiable: test asserts exactly one class, `drone`.

21. `@role/developer-training` Add tests for model card and metrics schema validation.
    - Verifiable: placeholder/null metrics validate; missing required keys fail.

22. `@role/developer-training` Add schema fixtures for all four documented experiment types.
    - Verifiable: model comparison, confidence threshold analysis, tracker behavior comparison, and false-positive analysis fixtures validate.

23. `@role/developer-training` Add notebook-template checks.
    - Verifiable: checks assert notebook templates start from pretrained YOLO weights and do not train from scratch.

24. `@role/developer-training` Add safety checks for generated artifact paths.
    - Verifiable: generated model card/metrics references intended for app import are relative, not absolute host/container paths.

25. `@role/docs-maintainer` Update `training/index.md` after training files/commands exist.
    - Verifiable: index lists new training artifacts and exact local training commands; unavailable commands remain marked `not available yet`.

26. `@role/docs-maintainer` Check `.gitignore` for training large-file coverage.
    - Verifiable: generated storage datasets, model weights, reports, and notebook outputs remain ignored; update `.gitignore` only if a concrete gap exists.

27. `@role/tester` Run training-specific checks.
    - Verifiable commands, when implemented:
      - training dependency install or documented `not available yet`
      - dataset split fixture command
      - model card/metrics schema validation command
      - all four experiment schema fixture validation command
      - notebook pretrained-weight check
      - training tests command
      - Git status check showing no generated datasets/weights/results tracked

28. `@role/code-reviewer` Review Phase 21 changes against consulted docs.
    - Verifiable: review confirms no runtime training launch, no backend/frontend/API/DB scope creep, YOLO26 primary preserved, single-class `drone` preserved, all four experiment artifact families covered, generated paths relative, large artifacts ignored.

## Relevant checks only

- Dataset split script on small fixture: expected `PASS` after implementation.
- Split manifest required columns: expected `PASS`.
- `data.yaml` one-class `drone`: expected `PASS`.
- Model card schema with placeholder/null metrics: expected `PASS`.
- Metrics schema validation: expected `PASS`.
- Four experiment artifact schema fixtures: expected `PASS`.
- Notebook pretrained-weight check: expected `PASS`.
- Training dependency install/documented command: expected `PASS` when manifest exists; otherwise `not available yet`.
- Training tests: expected `PASS` when test scaffold exists; otherwise `not available yet`.
- Local smoke training: expected `PASS` only if tiny fixture/dependencies are implemented; otherwise `not available yet`.
- Git status large artifact check: expected no generated datasets, weights, or reports tracked.

## Explicit non-scope

- No backend API endpoints.
- No database migrations.
- No frontend pages.
- No CV worker queue/inference changes.
- No model training from web UI or backend API.
- No multi-hour Kaggle/Colab execution by agent.
- No real datasets or model weights committed.
- No second detection class for birds.
- No out-of-scope targeting, navigation, geospatial, hardware, or interception behavior.
