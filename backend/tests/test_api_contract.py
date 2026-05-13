from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import hash_password
from app.db.models import (
    Base,
    Detection,
    ExperimentMetric,
    ExperimentRun,
    MediaFile,
    ModelVersion,
    ProcessingJob,
    Track,
    User,
)
from app.db.session import get_engine
from app.main import create_app

DOCUMENTED_PATHS = {
    "/api/health",
    "/api/health/db",
    "/api/auth/register",
    "/api/auth/login",
    "/api/auth/me",
    "/api/media",
    "/api/media/{media_id}",
    "/api/jobs",
    "/api/jobs/{job_id}",
    "/api/jobs/{job_id}/summary",
    "/api/jobs/{job_id}/detections",
    "/api/jobs/{job_id}/tracks",
    "/api/jobs/{job_id}/result",
    "/api/jobs/{job_id}/download/media",
    "/api/jobs/{job_id}/download/csv",
    "/api/jobs/{job_id}/download/json",
    "/api/models",
    "/api/models/{model_id}",
    "/api/models/{model_id}/activate",
    "/api/experiments",
    "/api/experiments/import",
    "/api/experiments/{experiment_id}",
    "/api/admin/stats",
    "/api/admin/jobs",
    "/api/admin/users",
    "/api/admin/storage/cleanup",
}

PAGINATED_PATHS = {
    "/api/media",
    "/api/jobs",
    "/api/jobs/{job_id}/detections",
    "/api/jobs/{job_id}/tracks",
    "/api/models",
    "/api/experiments",
    "/api/admin/jobs",
    "/api/admin/users",
}

FORBIDDEN_RESPONSE_TEXT = {
    "password_hash",
    "jwt_secret",
    "jwt-secret-value",
    "db-secret",
    "DATABASE_URL",
    "interception",
    "flight_control",
    "motor_command",
    "aiming_command",
    "payload_command",
    "geospatial",
    "engagement",
}


@pytest.fixture
def contract_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'contract.db'}"
    storage_root = tmp_path / "storage"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("STORAGE_ROOT", str(storage_root))
    monkeypatch.setenv("MODELS_ROOT", str(storage_root / "models"))
    get_engine.cache_clear()
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()

    with TestClient(create_app()) as client:
        yield client

    Base.metadata.drop_all(get_engine())
    get_engine.cache_clear()


def _assert_safe_response_payload(payload: Mapping[str, Any] | list[Any] | str) -> None:
    text = str(payload)
    for forbidden in FORBIDDEN_RESPONSE_TEXT:
        assert forbidden not in text
    assert "C:\\\\" not in text
    assert "/app/storage" not in text
    assert "Traceback" not in text


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _create_contract_records() -> tuple[UUID, UUID]:
    user_id = uuid4()
    admin_id = uuid4()
    media_id = uuid4()
    model_id = uuid4()
    job_id = uuid4()
    experiment_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add_all(
            [
                User(
                    id=user_id,
                    email="user@example.local",
                    password_hash=hash_password("user-secret-value"),
                    role="user",
                    is_active=True,
                ),
                User(
                    id=admin_id,
                    email="admin@example.local",
                    password_hash=hash_password("admin-secret-value"),
                    role="admin",
                    is_active=True,
                ),
            ]
        )
        session.add(
            MediaFile(
                id=media_id,
                user_id=user_id,
                original_filename="source.png",
                stored_path=f"uploads/{user_id}/{media_id}/source.png",
                media_type="image",
                mime_type="image/png",
                file_size_bytes=128,
                width=640,
                height=480,
                frame_count=1,
            )
        )
        session.add(
            ModelVersion(
                id=model_id,
                name="YOLO26s",
                model_family="YOLO26",
                variant="s",
                weights_path=f"models/{model_id}/weights.pt",
                dataset_name="Seraphim",
                dataset_split_description="test split",
                metrics_json={"map50": 0.71},
                is_active=True,
                created_by_user_id=admin_id,
            )
        )
        session.add(
            ProcessingJob(
                id=job_id,
                user_id=user_id,
                media_file_id=media_id,
                model_version_id=model_id,
                status="completed",
                input_params_json={
                    "confidence_threshold": 0.25,
                    "iou_threshold": 0.45,
                    "image_size": 640,
                    "tracker_type": "bytetrack",
                    "frame_stride": 1,
                },
                summary_json={"total_detections": 1, "average_confidence": 0.8},
                result_media_path=f"results/{job_id}/annotated.png",
                csv_path=f"results/{job_id}/detections.csv",
                json_path=f"results/{job_id}/detections.json",
                progress_percent=100,
                retry_count=0,
            )
        )
        session.add(
            Detection(
                id=uuid4(),
                job_id=job_id,
                media_file_id=media_id,
                frame_index=0,
                timestamp_ms=0,
                class_id=0,
                class_name="drone",
                confidence=0.8,
                bbox_x1=10,
                bbox_y1=20,
                bbox_x2=50,
                bbox_y2=80,
                frame_width=640,
                frame_height=480,
            )
        )
        session.add(
            Track(
                id=uuid4(),
                job_id=job_id,
                track_id=7,
                class_name="drone",
                first_frame_index=0,
                last_frame_index=2,
                frames_count=3,
                average_confidence=0.8,
                max_confidence=0.9,
            )
        )
        session.add(
            ExperimentRun(
                id=experiment_id,
                name="Model comparison",
                experiment_type="model_comparison",
                description="Imported metrics",
                model_version_id=model_id,
                dataset_name="Seraphim",
                config_json={"image_size": 640},
                artifacts_path="reports/model-comparison/metrics.json",
                is_published=True,
                created_by_user_id=admin_id,
            )
        )
        session.add(
            ExperimentMetric(
                id=uuid4(),
                experiment_run_id=experiment_id,
                metric_name="map50",
                metric_value=0.71,
                metric_unit=None,
                metadata_json={"source": "notebook"},
            )
        )
        session.commit()
    return job_id, experiment_id


def test_openapi_exposes_documented_api_paths_with_api_prefix(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"])

    assert DOCUMENTED_PATHS <= paths
    assert all(path.startswith("/api/") for path in paths)
    assert "/api/jobs/{job_id}/download/{kind}" not in paths


def test_openapi_paginated_list_schemas_are_frontend_usable(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    for path in PAGINATED_PATHS:
        response_schema = schema["paths"][path]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        ref = response_schema["$ref"].rsplit("/", maxsplit=1)[-1]
        properties = schema["components"]["schemas"][ref]["properties"]
        assert {"items", "total", "limit", "offset"} <= set(properties)


def test_error_responses_use_safe_fastapi_detail_payloads(client: TestClient) -> None:
    unauthorized = client.get("/api/auth/me")
    validation = client.post("/api/auth/login", json={})
    missing = client.get("/api/does-not-exist")

    assert unauthorized.status_code == 401
    assert isinstance(unauthorized.json()["detail"], str)
    assert validation.status_code == 422
    assert isinstance(validation.json()["detail"], list)
    assert missing.status_code == 404
    assert isinstance(missing.json()["detail"], str)

    _assert_safe_response_payload(unauthorized.json())
    _assert_safe_response_payload(validation.json())
    _assert_safe_response_payload(missing.json())


def test_successful_api_json_responses_do_not_expose_internal_or_forbidden_fields(
    contract_client: TestClient,
) -> None:
    job_id, experiment_id = _create_contract_records()
    user_token = _login(contract_client, "user@example.local", "user-secret-value")
    admin_token = _login(contract_client, "admin@example.local", "admin-secret-value")

    checked_responses = [
        contract_client.get("/api/auth/me", headers=_auth(user_token)),
        contract_client.get("/api/media", headers=_auth(user_token)),
        contract_client.get("/api/jobs", headers=_auth(user_token)),
        contract_client.get(f"/api/jobs/{job_id}", headers=_auth(user_token)),
        contract_client.get(f"/api/jobs/{job_id}/summary", headers=_auth(user_token)),
        contract_client.get(f"/api/jobs/{job_id}/detections", headers=_auth(user_token)),
        contract_client.get(f"/api/jobs/{job_id}/tracks", headers=_auth(user_token)),
        contract_client.get(f"/api/jobs/{job_id}/result", headers=_auth(user_token)),
        contract_client.get("/api/models", headers=_auth(user_token)),
        contract_client.get("/api/experiments", headers=_auth(user_token)),
        contract_client.get(
            f"/api/experiments/{experiment_id}",
            headers=_auth(user_token),
        ),
        contract_client.get("/api/admin/stats", headers=_auth(admin_token)),
        contract_client.get("/api/admin/jobs", headers=_auth(admin_token)),
        contract_client.get("/api/admin/users", headers=_auth(admin_token)),
    ]

    for response in checked_responses:
        assert response.status_code == 200, response.text
        _assert_safe_response_payload(response.json())
        assert str(Path(Settings().storage_root)) not in response.text
        assert "stored_path" not in response.text
        assert "result_media_path" not in response.text
        assert "csv_path" not in response.text
        assert "json_path" not in response.text
