from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MODEL_CARD_REQUIRED_KEYS = {
    "name",
    "model_family",
    "variant",
    "task",
    "classes",
    "dataset",
    "split_manifest",
    "train_images",
    "val_images",
    "test_images",
    "image_size",
    "epochs",
    "metrics",
}

MODEL_METRIC_KEYS = {
    "precision",
    "recall",
    "map_50",
    "map_50_95",
    "confusion_matrix",
    "model_size_mb",
    "latency_ms_per_frame",
    "fps",
    "total_processing_time_seconds",
    "average_video_fps",
}

EXPERIMENT_TYPES = {
    "model_comparison",
    "confidence_threshold_analysis",
    "tracker_behavior_comparison",
    "false_positive_analysis",
}

FORBIDDEN_TRACKER_METRICS = {"mota", "idf1", "hota", "trackingaccuracy"}
NORMALIZED_PATH_REFERENCE_KEYS = {
    "artifactpath",
    "artifactpaths",
    "confusionmatrix",
    "confusionmatrixpath",
    "figurepath",
    "figurepaths",
    "plotpath",
    "plotpaths",
    "reportartifact",
    "reportartifacts",
    "reportpath",
    "reportpaths",
}


class ArtifactValidationError(ValueError):
    """Raised when offline training artifacts do not match Phase 21 contracts."""


def validate_model_card(card: dict[str, Any]) -> None:
    _require_keys(card, MODEL_CARD_REQUIRED_KEYS, "model card")
    if card["model_family"] not in {"YOLO26", "YOLO11"}:
        raise ArtifactValidationError("model_family must be YOLO26 or documented fallback YOLO11")
    if card["task"] != "detect":
        raise ArtifactValidationError("task must be detect")
    if card["classes"] != ["drone"]:
        raise ArtifactValidationError("classes must contain exactly drone")
    _validate_relative_path(str(card["split_manifest"]), "split_manifest")

    metrics = card["metrics"]
    if not isinstance(metrics, dict):
        raise ArtifactValidationError("metrics must be an object")
    _require_keys(metrics, MODEL_METRIC_KEYS, "model card metrics")
    confusion_matrix = metrics.get("confusion_matrix")
    if isinstance(confusion_matrix, str):
        _validate_relative_path(confusion_matrix, "confusion_matrix")


def validate_metrics_artifact(metrics: dict[str, Any]) -> None:
    _require_keys(metrics, {"schema_version", "detection_metrics", "performance_metrics", "experiments"}, "metrics")
    _require_keys(metrics["detection_metrics"], {"precision", "recall", "map_50", "map_50_95", "confusion_matrix"}, "detection_metrics")
    _require_keys(
        metrics["performance_metrics"],
        {"model_size_mb", "latency_ms_per_frame", "fps", "total_processing_time_seconds", "average_video_fps"},
        "performance_metrics",
    )
    experiments = metrics["experiments"]
    if not isinstance(experiments, list):
        raise ArtifactValidationError("experiments must be a list")
    found_types = {experiment.get("type") for experiment in experiments if isinstance(experiment, dict)}
    if found_types != EXPERIMENT_TYPES:
        raise ArtifactValidationError(f"experiments must contain exactly {sorted(EXPERIMENT_TYPES)}")
    _validate_path_references(metrics["detection_metrics"], "detection_metrics")

    for experiment in experiments:
        if not isinstance(experiment, dict):
            raise ArtifactValidationError("experiment must be an object")
        _validate_experiment(experiment)
        _validate_path_references(experiment, f"{experiment['type']} experiment")


def validate_json_file(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _validate_experiment(experiment: dict[str, Any]) -> None:
    experiment_type = experiment["type"]
    _require_keys(experiment, {"type", "summary", "metrics"}, f"{experiment_type} experiment")
    if experiment_type == "model_comparison":
        _require_keys(experiment, {"models"}, "model_comparison experiment")
    elif experiment_type == "confidence_threshold_analysis":
        thresholds = experiment.get("thresholds")
        if thresholds != [0.25, 0.5, 0.7]:
            raise ArtifactValidationError("confidence threshold analysis must cover 0.25, 0.50, and 0.70")
    elif experiment_type == "tracker_behavior_comparison":
        trackers = set(experiment.get("trackers", []))
        if trackers != {"ByteTrack", "BoT-SORT"}:
            raise ArtifactValidationError("tracker behavior comparison must cover ByteTrack and BoT-SORT")
        metric_keys = set(experiment["metrics"])
        normalized = {_normalize_metric_key(key) for key in metric_keys}
        if normalized & FORBIDDEN_TRACKER_METRICS:
            raise ArtifactValidationError("tracker behavior comparison must not use absolute tracking accuracy metrics")
    elif experiment_type == "false_positive_analysis":
        if experiment.get("dataset_purpose") != "false_positive_analysis":
            raise ArtifactValidationError("Bird vs Drone data is allowed only for false-positive analysis")


def _require_keys(data: dict[str, Any], required: set[str], label: str) -> None:
    missing = required - set(data)
    if missing:
        raise ArtifactValidationError(f"{label} missing required keys: {sorted(missing)}")


def _validate_relative_path(value: str, label: str) -> None:
    path = Path(value)
    if path.is_absolute() or value.startswith(("/", "\\")) or ":" in value:
        raise ArtifactValidationError(f"{label} must be a relative path")
    if ".." in path.parts:
        raise ArtifactValidationError(f"{label} must not contain traversal segments")


def _validate_path_references(value: Any, label: str, *, in_path_reference: bool = False) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = _normalize_metric_key(str(key))
            child_is_path = (
                in_path_reference
                or normalized_key in NORMALIZED_PATH_REFERENCE_KEYS
                or normalized_key.endswith("path")
                or normalized_key.endswith("paths")
            )
            _validate_path_references(child, f"{label}.{key}", in_path_reference=child_is_path)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_path_references(child, f"{label}[{index}]", in_path_reference=in_path_reference)
        return

    if in_path_reference and isinstance(value, str):
        _validate_relative_path(value, label)


def _normalize_metric_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())
