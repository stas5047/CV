from __future__ import annotations

import json
from pathlib import Path

import pytest

from aerovision_training.schemas import (
    ArtifactValidationError,
    validate_metrics_artifact,
    validate_model_card,
)


def _model_card() -> dict[str, object]:
    return {
        "name": "yolo26s-seraphim-subset-v1",
        "model_family": "YOLO26",
        "variant": "s",
        "task": "detect",
        "classes": ["drone"],
        "dataset": "Seraphim Drone Detection Dataset subset",
        "split_manifest": "datasets/seraphim_subset/split_manifest.csv",
        "train_images": 16000,
        "val_images": 2000,
        "test_images": 2000,
        "image_size": 640,
        "epochs": 50,
        "metrics": {
            "precision": None,
            "recall": None,
            "map_50": None,
            "map_50_95": None,
            "confusion_matrix": None,
            "model_size_mb": None,
            "latency_ms_per_frame": None,
            "fps": None,
            "total_processing_time_seconds": None,
            "average_video_fps": None,
        },
    }


def test_model_card_accepts_placeholder_metrics_and_rejects_missing_required_key() -> None:
    validate_model_card(_model_card())

    invalid = _model_card()
    invalid.pop("model_family")

    with pytest.raises(ArtifactValidationError):
        validate_model_card(invalid)


def test_model_card_rejects_absolute_or_traversal_paths() -> None:
    invalid = _model_card()
    invalid["split_manifest"] = "/app/storage/datasets/seraphim_subset/split_manifest.csv"

    with pytest.raises(ArtifactValidationError):
        validate_model_card(invalid)

    invalid["split_manifest"] = "datasets/../secrets.csv"
    with pytest.raises(ArtifactValidationError):
        validate_model_card(invalid)


def test_metrics_artifact_requires_all_documented_experiment_families() -> None:
    metrics = json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))

    validate_metrics_artifact(metrics)

    experiment_types = {experiment["type"] for experiment in metrics["experiments"]}
    assert experiment_types == {
        "model_comparison",
        "threshold_analysis",
        "tracker_comparison",
        "false_positive_analysis",
    }


def test_metrics_artifact_rejects_legacy_experiment_aliases() -> None:
    metrics = json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))
    threshold_experiment = next(
        experiment for experiment in metrics["experiments"] if experiment["type"] == "threshold_analysis"
    )
    threshold_experiment["type"] = "confidence_threshold_analysis"

    with pytest.raises(ArtifactValidationError):
        validate_metrics_artifact(metrics)


def test_tracker_behavior_rejects_absolute_accuracy_metrics() -> None:
    metrics = json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))
    tracker_experiment = next(
        experiment
        for experiment in metrics["experiments"]
        if experiment["type"] == "tracker_comparison"
    )
    tracker_experiment["metrics"]["MOTA"] = None

    with pytest.raises(ArtifactValidationError):
        validate_metrics_artifact(metrics)


def test_metrics_artifact_rejects_absolute_or_traversal_report_paths() -> None:
    metrics = json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))
    metrics["detection_metrics"]["confusion_matrix"] = "/app/storage/reports/confusion.png"

    with pytest.raises(ArtifactValidationError):
        validate_metrics_artifact(metrics)

    metrics["detection_metrics"]["confusion_matrix"] = None
    metrics["experiments"][0]["report_artifacts"] = ["reports/../secrets.json"]

    with pytest.raises(ArtifactValidationError):
        validate_metrics_artifact(metrics)


def test_metrics_artifact_rejects_absolute_path_text_inside_metadata() -> None:
    metrics = json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))
    metrics["experiments"][0]["notes"] = "generated at /app/storage/reports/leak.png"

    with pytest.raises(ArtifactValidationError):
        validate_metrics_artifact(metrics)
