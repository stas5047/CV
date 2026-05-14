# AeroVision - Training Index

## General Description

The `training/` folder contains AeroVision offline training, dataset preparation, notebook, artifact, and experiment-import-readiness utilities.

According to `../docs/`, training is performed outside the running web application in free cloud notebook environments such as Kaggle Notebook or Google Colab. This folder contains scripts, notebook templates, model-card/metrics templates, validators, and tests. The web UI and backend must not launch model training.

## Current Files

| Path | Purpose |
|---|---|
| `index.md` | Training folder summary, current contents, and training-local commands. |
| `README.md` | Human workflow for offline dataset preparation, cloud notebooks, smoke training, model artifacts, and validation. |
| `pyproject.toml` | Training-local package metadata and optional dev/smoke dependencies. |
| `aerovision_training/dataset_split.py` | Deterministic YOLO dataset preparation with group-aware split support, stale-output safeguards, duplicate-target checks, and `data.yaml` generation. |
| `aerovision_training/schemas.py` | Model card and metrics artifact validation rules. |
| `aerovision_training/validate_artifacts.py` | Offline import-readiness CLI for model card and metrics artifacts. |
| `aerovision_training/notebook_checks.py` | Notebook-template validation helper. |
| `aerovision_training/smoke_train.py` | Tiny local YOLO smoke training entry point; not final training evidence. |
| `templates/model_card.placeholder.json` | Placeholder model card template with nullable metrics. |
| `templates/metrics.placeholder.json` | Placeholder metrics template covering all four documented experiment families. |
| `notebooks/yolo26n_finetune_template.ipynb` | Human-run YOLO26n Kaggle/Colab fine-tuning template. |
| `notebooks/yolo26s_finetune_template.ipynb` | Human-run YOLO26s Kaggle/Colab fine-tuning template. |
| `tests/` | Training utility and artifact contract tests. |

## Commands

| Command | Status |
|---|---|
| `python -m pip install -e "training[dev]"` | Installs training utilities and test dependencies. |
| `python -m aerovision_training.dataset_split --images-dir <source-images> --labels-dir <source-labels> --output-dir storage/datasets/seraphim_subset` | Prepares deterministic one-class YOLO dataset split. |
| `python -m aerovision_training.dataset_split --images-dir <source-images> --labels-dir <source-labels> --metadata-csv <metadata.csv> --group-column source_group_id --output-dir storage/datasets/seraphim_subset` | Prepares group-aware YOLO split when grouping metadata exists. |
| `python -m aerovision_training.validate_artifacts --model-card training/templates/model_card.placeholder.json --metrics training/templates/metrics.placeholder.json` | Validates model card and metrics artifacts for offline import readiness. |
| `python -m aerovision_training.smoke_train --data-yaml storage/datasets/seraphim_subset/data.yaml --model yolo26n.pt --epochs 1` | Runs tiny local smoke training only when `ultralytics` and tiny data are available; not final evidence. |
| `python -m pytest training/tests` | Runs training utility and artifact contract tests from repository root. |
