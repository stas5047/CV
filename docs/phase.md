## Phase 19 - Worker CSV/JSON exports and no-detection contracts

**Direction:** CV Worker / Exports  
**Goal:** Generate CSV and JSON exports exactly according to API/export contracts.

### Scope

- Generate CSV export with one row per detection.
- Include required CSV columns:
  - job/media/frame/timestamp fields;
  - class/confidence fields;
  - bounding box corner fields;
  - derived center-size fields;
  - frame dimensions;
  - track ID;
  - model version;
  - tracker type.
- Generate JSON export with top-level:
  - `job`;
  - `media`;
  - `model`;
  - `parameters`;
  - `summary`;
  - `detections`;
  - `tracks`.
- Generate headers-only CSV for no-detection jobs.
- Generate JSON with empty `detections` array for no-detection jobs.
- Store `csv_path` and `json_path` as relative paths.
- Keep exports inside allowed CV output boundary only.
- Add export contract tests.

### Relevant docs

- `docs/API.md`
- `docs/CV_PIPELINE.md`
- `docs/DATA_MODEL.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/TESTING_QA.md`

### Validation

- CSV export contains all required columns.
- JSON export contains all required top-level objects/arrays.
- Derived values are computed correctly from corner coordinates.
- No-detection CSV has headers only.
- No-detection JSON has empty `detections` array.
- Exports do not include forbidden physical-control, targeting, geolocation, or engagement fields.
- Export tests pass.

### Commit

`feat(worker-exports): add CSV JSON exports and no-detection contracts`