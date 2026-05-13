# TRAINING_EXPERIMENTS.md

## Purpose

This document defines cloud-notebook training, dataset preparation, experiment recording, and experiment artifact import for the Drone Computer Vision Subsystem.

This document is canonical for:

- human vs code-agent responsibility during training;
- cloud notebook training policy;
- dataset plan;
- split and leakage prevention rules;
- training model plan;
- training artifacts;
- model card requirements;
- experiment types;
- experiment import expectations.

This document is not canonical for runtime inference, upload validation, API routes, UI layout, or database field definitions.

## Training Boundary

Training is not part of the running web application.

The web UI and backend must not launch model training.

Training is performed in free cloud notebook environments such as Kaggle Notebook or Google Colab. The application later imports the resulting model weights, metrics, and artifacts.

Local training is not the primary plan. Local smoke training may be used only to verify the pipeline on a tiny subset, and local fallback training may be used only when cloud training is unavailable.

## Responsibility Split

### Human Responsibilities

The human user is responsible for:

- running Kaggle or Google Colab notebooks;
- logging into cloud notebook platforms;
- requesting free-tier GPU resources;
- running long training sessions;
- downloading trained weights and metrics;
- placing resulting artifacts under project storage;
- registering final models through admin tooling or UI.

### Code-Agent Responsibilities

Code agents are responsible for creating:

- training scripts;
- Kaggle/Colab notebooks;
- configuration files;
- dataset split scripts;
- training README instructions;
- artifact schemas;
- import utilities for model cards and metrics;
- application logic that reads model artifacts and registers them.

Code agents must not attempt to execute multi-hour Kaggle/Colab sessions themselves.

## Training Environments

Primary training environment:

- Kaggle Notebook or Google Colab with free GPU when available.

Local environment:

- used for development;
- used for Docker launches;
- used for inference;
- used for live demonstration;
- may be used for tiny smoke training only.

Local machine GPU target:

- NVIDIA GeForce GTX 1660 SUPER for local inference and demonstration.

Local training is not the primary plan.

## Local Smoke Training

Local smoke training may be implemented only to verify that the training pipeline works.

Recommended smoke training characteristics:

- tiny subset;
- very small epoch count;
- not used as final model;
- not used as final evaluation evidence;
- same dataset format and artifact structure as full training.

Smoke training must not replace cloud training.

## Local Training Fallback

If cloud training is unavailable, a local fallback may use:

- YOLO26n, or approved YOLO11n fallback if YOLO26 is unavailable;
- smaller dataset subset;
- fewer epochs;
- smaller batch size;
- same YOLO dataset format;
- same output artifact structure.

Training environment limitations must not change the final application architecture.

## Detection Task

Training task:

- single-class object detection.

Required class:

- `drone`.

Birds must not be trained as a second primary detection class. Bird-vs-drone data is reserved for false-positive analysis.

## Model Plan

Primary model family:

- Ultralytics YOLO26.

Training plan:

| Model | Purpose |
|---|---|
| YOLO26n fine-tuned | Baseline and lightweight benchmark. |
| YOLO26s fine-tuned | Main application model after training. |

Training starts from pretrained YOLO weights. Do not train from scratch.

## YOLO11 Fallback for Training

If YOLO26 weights or package support are unavailable after the issue is reported and documented, the fallback family is YOLO11.

Fallback mapping:

| Primary model | Fallback model |
|---|---|
| YOLO26n | YOLO11n |
| YOLO26s | YOLO11s |

Any fallback must be recorded in:

- model card;
- experiment metadata;
- model registry metadata.

## Default Training Parameters

Recommended defaults:

| Parameter | Value |
|---|---|
| Image size | 640 |
| Epochs | 50 |
| Batch | Auto or maximum stable value |
| Patience | 10 |
| Seed | 42 |
| Task | Detect |
| Class count | 1 |
| Class name | `drone` |

Changes caused by hardware limits must be recorded in experiment metadata.

## Primary Dataset

Primary dataset:

- Seraphim Drone Detection Dataset.

Final planned subset size:

- 20,000 images.

Required split:

| Split | Image count |
|---|---:|
| Train | 16,000 |
| Validation | 2,000 |
| Test | 2,000 |

Final reported training and evaluation metrics must be based on the Seraphim subset unless explicitly documented otherwise.

## Split and Leakage Prevention

Seraphim is a compiled multi-source dataset. Random per-image splitting can leak near-duplicate or sequential frames across splits.

Split priority:

1. If source dataset identifiers, sequence identifiers, video identifiers, or grouping metadata are available, split by group first.
2. A given source, sequence, or video group must exist entirely in one split.
3. Random per-image splitting is allowed only if grouping metadata is unavailable.
4. The split must be deterministic with seed `42`.

The split script must save a split manifest.

Required manifest columns:

| Column | Meaning |
|---|---|
| `image_path` | Image path. |
| `label_path` | Label path. |
| `source_group_id` | Source/sequence/video group when available; may be empty. |
| `split` | `train`, `val`, or `test`. |

The manifest must be referenced in model cards and experiment metadata.

## Dataset Format

Canonical project annotation format:

- YOLO format.

Canonical dataset path:

- `storage/datasets/seraphim_subset`.

Required dataset structure:

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

`data.yaml` must define exactly one class:

- class `0`: `drone`.

Any dataset in another annotation format must be converted into this YOLO-compatible structure before training.

## Additional Datasets

Allowed additional dataset uses:

| Dataset | Allowed purpose |
|---|---|
| Bird vs Drone dataset | False-positive analysis only. |
| Kaggle Drone Detection dataset | Early pipeline smoke tests only. |

Additional datasets must not replace the Seraphim subset for final reported training/evaluation metrics unless explicitly documented and approved.

## Training Artifacts

Training scripts must save artifacts in a structured way.

Required artifact categories:

- train run artifacts;
- validation artifacts;
- test artifacts;
- final weights;
- model card;
- metrics file;
- plots such as confusion matrix or PR curve when available.

Recommended model artifact layout under model storage:

```text
models/
  yolo26n-seraphim-subset-v1/
    weights.pt
    model_card.json
    metrics.json
  yolo26s-seraphim-subset-v1/
    weights.pt
    model_card.json
    metrics.json
```

Under YOLO11 fallback, names should reflect the actual model family.

## Model Card Requirements

Each trained or placeholder model registration must have a model card.

Required model card fields:

| Field | Meaning |
|---|---|
| `name` | Model version name. |
| `model_family` | `YOLO26` or documented fallback `YOLO11`. |
| `variant` | Model variant such as `n` or `s`. |
| `task` | `detect`. |
| `classes` | Must contain `drone`. |
| `dataset` | Dataset name, usually Seraphim subset. |
| `split_manifest` | Path to split manifest. |
| `train_images` | Train split count. |
| `val_images` | Validation split count. |
| `test_images` | Test split count. |
| `image_size` | Training image size. |
| `epochs` | Epoch count. |
| `metrics` | Precision, recall, mAP, FPS, latency, and related metrics. |

Metric values may be `null` before actual training results are available. The schema must still exist.

## Required Detection Metrics

The training/evaluation workflow must collect:

- precision;
- recall;
- mAP@0.5;
- mAP@0.5:0.95;
- confusion matrix.

## Required Performance Metrics

The workflow must collect or derive:

- model size in MB;
- inference latency per frame in milliseconds;
- end-to-end processing FPS;
- total processing time;
- average FPS for video processing.

## Experiment Runs

The project must support importing and displaying these experiment records:

1. Model comparison.
2. Confidence threshold analysis.
3. Tracker behavior comparison.
4. False-positive analysis.

Experiments are imported into the application. They are not launched from the web UI.

## Experiment 1: Model Comparison

Compare:

- YOLO26n fine-tuned;
- YOLO26s fine-tuned.

Under fallback:

- YOLO11n fine-tuned;
- YOLO11s fine-tuned.

Required comparison metrics:

- precision;
- recall;
- mAP@0.5;
- mAP@0.5:0.95;
- inference latency;
- FPS;
- model size.

## Experiment 2: Confidence Threshold Analysis

For the final main model, compare:

- confidence threshold 0.25;
- confidence threshold 0.50;
- confidence threshold 0.70.

Goal:

- show recall vs false-positive trade-off;
- explain how threshold affects detections.

## Experiment 3: Tracker Behavior Comparison

Compare:

- ByteTrack;
- BoT-SORT.

Use the same videos and same trained main model.

This is a tracker behavior comparison, not an absolute tracking accuracy comparison.

Required indicators:

- video processing FPS;
- number of unique track IDs;
- number of frames with detections;
- average confidence;
- track fragmentation proxy;
- qualitative visual stability of track IDs;
- documented examples of observed ID switches when any are found.

Do not require MOTA, IDF1, HOTA, or any metric requiring manually annotated track identities.

## Experiment 4: False-Positive Analysis

Use Bird vs Drone images to check whether visually similar bird images cause false drone detections.

This experiment analyzes model limitations. It is not a second-class training task.

## Experiment Import Expectations

Admin import should support structured experiment artifacts that can populate:

- `experiment_runs`;
- `experiment_metrics`;
- report artifact paths;
- published/unpublished visibility.

Regular users see only published experiment results.

Admins see all imported experiment results.

Metric values may be incomplete or `null`; the frontend must render empty states rather than raw `null`.

## Artifact Registration Workflow

Expected high-level workflow:

1. Code agent creates scripts, notebooks, configs, and README.
2. Human runs training in Kaggle/Colab.
3. Human downloads weights, metrics, model card, and report artifacts.
4. Human places artifacts under project storage.
5. Admin registers model version in the application.
6. Admin activates the final main model.
7. Admin imports experiment results.
8. Frontend displays models and experiment metrics.

## Training and Experiment Invariants

The training workflow must always preserve these rules:

- Training is not launched from the web UI.
- Code agents do not run multi-hour cloud notebook sessions themselves.
- The task remains single-class `drone` detection.
- YOLO26 is primary.
- YOLO11 is fallback only after documented YOLO26 unavailability.
- Training starts from pretrained weights, not from scratch.
- Seraphim subset is the primary dataset.
- Split must prevent leakage when grouping metadata is available.
- Experiment 3 is behavior comparison, not absolute tracking accuracy.
- Bird-vs-drone data is for false-positive analysis only.
- Model cards and metrics schemas must exist even when metric values are placeholders.
- Large datasets, weights, processed videos, and generated results must not be committed to Git.
