# AeroVision Offline Training Workflow

This folder contains offline-only training artifacts and artifact registration helpers. Web UI, backend API, database migrations, and CV worker runtime do not launch training.

## Dataset Preparation

Install training utilities for local commands:

```powershell
python -m pip install -e "training[dev]"
```

Prepare a deterministic one-class YOLO dataset:

```powershell
python -m aerovision_training.dataset_split --images-dir <source-images> --labels-dir <source-labels> --output-dir storage/datasets/seraphim_subset
```

With grouping metadata:

```powershell
python -m aerovision_training.dataset_split --images-dir <source-images> --labels-dir <source-labels> --metadata-csv <metadata.csv> --group-column source_group_id --output-dir storage/datasets/seraphim_subset
```

The output directory must be empty before preparation. Source files with duplicate flattened image or label filenames are rejected because the YOLO output layout does not preserve source subdirectories.

Output layout:

```text
storage/datasets/seraphim_subset/
  images/train/
  images/val/
  images/test/
  labels/train/
  labels/val/
  labels/test/
  data.yaml
  split_manifest.csv
```

`data.yaml` defines one class: `drone`. `split_manifest.csv` contains `image_path`, `label_path`, `source_group_id`, and `split`.

## Cloud Notebooks

Use `training/notebooks/yolo26n_finetune_template.ipynb` for baseline and `training/notebooks/yolo26s_finetune_template.ipynb` for main model. Humans run these in Kaggle or Colab, download trained artifacts, and place them under storage.

YOLO26 is primary. YOLO11 fallback is allowed only after YOLO26 unavailability is reported and documented. If fallback is used, record actual family in model card and metrics.

## Local Smoke

Tiny local smoke training verifies pipeline shape only. It is not final model or evaluation evidence.

```powershell
python -m aerovision_training.smoke_train --data-yaml storage/datasets/seraphim_subset/data.yaml --model yolo26n.pt --epochs 1
```

Requires `ultralytics` in the training environment.

## Model Artifacts

Expected model layout:

```text
storage/models/yolo26s-seraphim-subset-v1/
  weights.pt
  model_card.json
  metrics.json
```

Use templates:

- `training/templates/model_card.placeholder.json`
- `training/templates/metrics.placeholder.json`

Validate import-readiness:

```powershell
python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json
```

## Register Artifacts In App

After cloud training, place downloaded files under storage before registration:

```text
storage/models/yolo26s-seraphim-subset-v1/weights.pt
storage/models/yolo26s-seraphim-subset-v1/model_card.json
storage/models/yolo26s-seraphim-subset-v1/metrics.json
storage/reports/yolo26s-seraphim-subset-v1/
```

Use an admin JWT issued by the backend API. Prefer an environment variable so tokens are not written into command history:

```powershell
$env:AEROVISION_API_TOKEN = "<admin-jwt>"
```

Register an existing model weights path through the backend API:

```powershell
python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 register-model --model-card storage/models/yolo26s-seraphim-subset-v1/model_card.json --weights-path models/yolo26s-seraphim-subset-v1/weights.pt
```

Register and activate in one explicit admin action:

```powershell
python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 register-model --model-card storage/models/yolo26s-seraphim-subset-v1/model_card.json --weights-path models/yolo26s-seraphim-subset-v1/weights.pt --activate
```

Import experiment records through the backend API:

```powershell
python -m aerovision_training.register_artifacts --backend-url http://localhost:8000 import-experiments --metrics storage/models/yolo26s-seraphim-subset-v1/metrics.json --artifacts-path reports/yolo26s-seraphim-subset-v1 --dataset-name "Seraphim Drone Detection Dataset subset" --published
```

The helper registers existing relative paths under storage. It does not upload `.pt` weights, does not read model weights, does not start training, and does not bypass backend admin authorization.

Artifact paths intended for application import must be relative to storage root. Do not place datasets, weights, generated reports, or training outputs in Git.
