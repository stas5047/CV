from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from aerovision_training.schemas import (
    ArtifactValidationError,
    validate_metrics_artifact,
    validate_model_card,
)

SendJson = Callable[[str, str, dict[str, Any] | None, str], dict[str, Any]]

EXPERIMENT_NAMES = {
    "model_comparison": "Model comparison",
    "threshold_analysis": "Confidence threshold analysis",
    "tracker_comparison": "Tracker behavior comparison",
    "false_positive_analysis": "False-positive analysis",
}


class BackendRequestError(RuntimeError):
    """Raised when backend artifact registration/import request fails."""


def load_json_artifact(path: Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ArtifactValidationError("artifact root must be an object")
    return data


def build_model_registration_payload(
    model_card: dict[str, Any],
    *,
    weights_path: str,
    activate: bool = False,
) -> dict[str, Any]:
    validate_model_card(model_card)
    validated_weights_path = _validate_relative_import_path(
        weights_path,
        label="weights_path",
        required_prefix="models/",
    )

    return {
        "name": model_card["name"],
        "model_family": model_card["model_family"],
        "variant": model_card["variant"],
        "weights_path": validated_weights_path,
        "dataset_name": model_card["dataset"],
        "dataset_split_description": (
            f"train={model_card['train_images']}; "
            f"val={model_card['val_images']}; "
            f"test={model_card['test_images']}; "
            f"split_manifest={model_card['split_manifest']}"
        ),
        "metrics_json": {
            "metrics": model_card["metrics"],
            "task": model_card["task"],
            "classes": model_card["classes"],
            "image_size": model_card["image_size"],
            "epochs": model_card["epochs"],
            "split_manifest": model_card["split_manifest"],
        },
        "is_active": activate,
    }


def build_experiment_import_payloads(
    metrics_artifact: dict[str, Any],
    *,
    artifacts_path: str,
    dataset_name: str | None = None,
    model_version_id: str | None = None,
    is_published: bool = False,
) -> list[dict[str, Any]]:
    validate_metrics_artifact(metrics_artifact)
    validated_artifacts_path = _validate_relative_import_path(
        artifacts_path,
        label="artifacts_path",
        required_prefix="reports/",
    )

    payloads: list[dict[str, Any]] = []
    for experiment in metrics_artifact["experiments"]:
        experiment_type = experiment["type"]
        payloads.append(
            {
                "name": EXPERIMENT_NAMES[experiment_type],
                "experiment_type": experiment_type,
                "description": experiment["summary"],
                "model_version_id": model_version_id,
                "dataset_name": dataset_name or experiment.get("dataset"),
                "config_json": {
                    key: value
                    for key, value in experiment.items()
                    if key not in {"type", "summary", "metrics"}
                },
                "artifacts_path": validated_artifacts_path,
                "is_published": is_published,
                "metrics": _build_metric_payloads(experiment["metrics"]),
            }
        )
    return payloads


def send_json_request(
    method: str,
    url: str,
    payload: dict[str, Any] | None,
    token: str,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - admin-provided backend URL.
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        raise BackendRequestError(f"backend request failed with HTTP {exc.code}") from exc
    except URLError as exc:
        raise BackendRequestError("backend request failed") from exc
    if not response_body:
        return {}
    data = json.loads(response_body)
    if not isinstance(data, dict):
        raise BackendRequestError("backend response was not a JSON object")
    return data


@dataclass(slots=True)
class ArtifactImportClient:
    base_url: str
    token: str
    send_json: SendJson = send_json_request

    def register_model(
        self,
        model_card: dict[str, Any],
        *,
        weights_path: str,
        activate: bool = False,
    ) -> dict[str, Any]:
        payload = build_model_registration_payload(
            model_card,
            weights_path=weights_path,
            activate=False,
        )
        created = self.send_json("POST", _api_url(self.base_url, "/api/models"), payload, self.token)
        print(f"Registered model {created.get('id', '<unknown>')}")
        if activate:
            model_id = created.get("id")
            if not model_id:
                raise BackendRequestError("backend response did not include model id")
            activated = self.send_json(
                "PATCH",
                _api_url(self.base_url, f"/api/models/{model_id}/activate"),
                None,
                self.token,
            )
            print(f"Activated model {activated.get('id', model_id)}")
            return activated
        return created

    def import_experiments(
        self,
        metrics_artifact: dict[str, Any],
        *,
        artifacts_path: str,
        dataset_name: str | None = None,
        model_version_id: str | None = None,
        is_published: bool = False,
    ) -> list[dict[str, Any]]:
        payloads = build_experiment_import_payloads(
            metrics_artifact,
            artifacts_path=artifacts_path,
            dataset_name=dataset_name,
            model_version_id=model_version_id,
            is_published=is_published,
        )
        created: list[dict[str, Any]] = []
        for payload in payloads:
            response = self.send_json(
                "POST",
                _api_url(self.base_url, "/api/experiments/import"),
                payload,
                self.token,
            )
            print(f"Imported experiment {response.get('id', '<unknown>')}")
            created.append(response)
        return created


def _build_metric_payloads(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for name, value in metrics.items():
        metric_value: float | None
        metadata_json: dict[str, Any]
        if isinstance(value, int | float) and not isinstance(value, bool):
            metric_value = float(value)
            metadata_json = {}
        elif value is None:
            metric_value = None
            metadata_json = {}
        else:
            metric_value = None
            metadata_json = {"value": value}
        payloads.append(
            {
                "metric_name": name,
                "metric_value": metric_value,
                "metric_unit": _metric_unit(name),
                "metadata_json": metadata_json,
            }
        )
    return payloads


def _metric_unit(metric_name: str) -> str | None:
    if metric_name in {"fps", "video_processing_fps", "average_video_fps"}:
        return "fps"
    if metric_name in {"latency_ms_per_frame"}:
        return "ms"
    if metric_name in {"model_size_mb"}:
        return "MB"
    if metric_name in {"total_processing_time_seconds"}:
        return "seconds"
    return None


def _validate_relative_import_path(value: str, *, label: str, required_prefix: str) -> str:
    normalized = value.strip().replace("\\", "/")
    if (
        not normalized
        or normalized.startswith(("/", "\\"))
        or ":" in normalized
        or normalized.startswith("storage/")
        or ".." in Path(normalized).parts
    ):
        raise ArtifactValidationError(f"{label} must be a safe relative path")
    if not normalized.startswith(required_prefix):
        raise ArtifactValidationError(f"{label} must be under {required_prefix.rstrip('/')}")
    return normalized


def _api_url(base_url: str, path: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
