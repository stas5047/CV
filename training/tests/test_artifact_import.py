from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from aerovision_training.artifact_import import (
    ArtifactImportClient,
    build_experiment_import_payloads,
    build_model_registration_payload,
)
from aerovision_training.register_artifacts import main as register_artifacts_main
from aerovision_training.schemas import ArtifactValidationError


def _model_card(**overrides: object) -> dict[str, Any]:
    card = json.loads(Path("training/templates/model_card.placeholder.json").read_text(encoding="utf-8"))
    card.update(overrides)
    return card


def _metrics_artifact() -> dict[str, Any]:
    return json.loads(Path("training/templates/metrics.placeholder.json").read_text(encoding="utf-8"))


def test_build_model_registration_payload_preserves_relative_weight_path_and_nullable_metrics() -> None:
    payload = build_model_registration_payload(
        _model_card(),
        weights_path="models/yolo26s-seraphim-subset-v1/weights.pt",
        activate=True,
    )

    assert payload == {
        "name": "yolo26s-seraphim-subset-v1",
        "model_family": "YOLO26",
        "variant": "s",
        "weights_path": "models/yolo26s-seraphim-subset-v1/weights.pt",
        "dataset_name": "Seraphim Drone Detection Dataset subset",
        "dataset_split_description": (
            "train=16000; val=2000; test=2000; split_manifest=datasets/seraphim_subset/split_manifest.csv"
        ),
        "metrics_json": {
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
            "task": "detect",
            "classes": ["drone"],
            "image_size": 640,
            "epochs": 50,
            "split_manifest": "datasets/seraphim_subset/split_manifest.csv",
        },
        "is_active": True,
    }


@pytest.mark.parametrize(
    "weights_path",
    [
        "/app/storage/models/yolo26s/weights.pt",
        "C:/storage/models/yolo26s/weights.pt",
        "models/../secret.pt",
        "storage/models/yolo26s/weights.pt",
    ],
)
def test_build_model_registration_payload_rejects_unsafe_weight_paths(weights_path: str) -> None:
    with pytest.raises(ArtifactValidationError):
        build_model_registration_payload(_model_card(), weights_path=weights_path)


def test_build_model_registration_payload_rejects_path_leaks_inside_model_card() -> None:
    card = _model_card()
    card["metrics"]["plot_path"] = "C:/Users/me/report.png"

    with pytest.raises(ArtifactValidationError):
        build_model_registration_payload(card, weights_path="models/yolo26s/weights.pt")


def test_build_model_registration_payload_rejects_absolute_path_in_non_path_metric_key() -> None:
    card = _model_card()
    card["metrics"]["source"] = "/app/storage/reports/leak.png"

    with pytest.raises(ArtifactValidationError):
        build_model_registration_payload(card, weights_path="models/yolo26s/weights.pt")


def test_build_experiment_import_payloads_uses_canonical_backend_types_and_relative_artifacts() -> None:
    payloads = build_experiment_import_payloads(
        _metrics_artifact(),
        artifacts_path="reports/yolo26s-seraphim-subset-v1",
        dataset_name="Seraphim Drone Detection Dataset subset",
        is_published=True,
    )

    assert [payload["experiment_type"] for payload in payloads] == [
        "model_comparison",
        "threshold_analysis",
        "tracker_comparison",
        "false_positive_analysis",
    ]
    assert all(payload["artifacts_path"] == "reports/yolo26s-seraphim-subset-v1" for payload in payloads)
    assert all(payload["dataset_name"] == "Seraphim Drone Detection Dataset subset" for payload in payloads)
    assert all(payload["is_published"] is True for payload in payloads)
    tracker_payload = next(payload for payload in payloads if payload["experiment_type"] == "tracker_comparison")
    assert {
        "video_processing_fps",
        "unique_track_ids",
        "observed_id_switch_examples",
    } <= {metric["metric_name"] for metric in tracker_payload["metrics"]}
    assert any(metric["metric_value"] is None for metric in tracker_payload["metrics"])


@pytest.mark.parametrize(
    "artifacts_path",
    [
        "/app/storage/reports/metrics.json",
        "C:/storage/reports/metrics.json",
        "reports/../secret",
        "storage/reports/metrics.json",
    ],
)
def test_build_experiment_import_payloads_rejects_unsafe_artifact_paths(artifacts_path: str) -> None:
    with pytest.raises(ArtifactValidationError):
        build_experiment_import_payloads(_metrics_artifact(), artifacts_path=artifacts_path)


def test_build_experiment_import_payloads_rejects_path_leaks_before_mutation() -> None:
    metrics = _metrics_artifact()
    metrics["experiments"][0]["metadata"] = {"report_path": "/app/storage/reports/leak.png"}

    with pytest.raises(ArtifactValidationError):
        build_experiment_import_payloads(metrics, artifacts_path="reports/yolo26s")


def test_import_client_uses_backend_routes_and_redacts_token(capsys: pytest.CaptureFixture[str]) -> None:
    requests: list[tuple[str, str, dict[str, Any], str]] = []

    def fake_send(method: str, url: str, payload: dict[str, Any] | None, token: str) -> dict[str, Any]:
        requests.append((method, url, payload or {}, token))
        if url.endswith("/api/models"):
            return {"id": "model-id"}
        if url.endswith("/api/models/model-id/activate"):
            return {"id": "model-id", "is_active": True}
        return {"id": f"experiment-{len(requests)}"}

    client = ArtifactImportClient(
        base_url="http://backend.local/",
        token="secret-token-value",
        send_json=fake_send,
    )

    model = client.register_model(
        _model_card(),
        weights_path="models/yolo26s-seraphim-subset-v1/weights.pt",
        activate=True,
    )
    experiments = client.import_experiments(
        _metrics_artifact(),
        artifacts_path="reports/yolo26s-seraphim-subset-v1",
    )

    output = capsys.readouterr().out
    assert model["id"] == "model-id"
    assert len(experiments) == 4
    assert requests[0][0:2] == ("POST", "http://backend.local/api/models")
    assert requests[1][0:2] == ("PATCH", "http://backend.local/api/models/model-id/activate")
    assert all(request[0] == "POST" for request in requests[2:])
    assert all(request[1] == "http://backend.local/api/experiments/import" for request in requests[2:])
    assert all(request[3] == "secret-token-value" for request in requests)
    assert "secret-token-value" not in output
    assert "/app/storage" not in output


def test_register_artifacts_cli_uses_env_token_and_fake_transport(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    requests: list[tuple[str, str, dict[str, Any], str]] = []

    def fake_send(method: str, url: str, payload: dict[str, Any] | None, token: str) -> dict[str, Any]:
        requests.append((method, url, payload or {}, token))
        return {"id": "created-id"}

    monkeypatch.setenv("AEROVISION_API_TOKEN", "env-secret-token")
    register_artifacts_main(
        [
            "--backend-url",
            "http://backend.local",
            "register-model",
            "--model-card",
            "training/templates/model_card.placeholder.json",
            "--weights-path",
            "models/yolo26s-seraphim-subset-v1/weights.pt",
        ],
        send_json=fake_send,
    )

    output = capsys.readouterr().out
    assert requests[0][0:2] == ("POST", "http://backend.local/api/models")
    assert requests[0][3] == "env-secret-token"
    assert requests[0][2]["model_family"] == "YOLO26"
    assert "env-secret-token" not in output
