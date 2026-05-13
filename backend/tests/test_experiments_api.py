from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import hash_password
from app.db.models import Base, ExperimentRun, ModelVersion, ProcessingJob, User
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture
def experiments_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'experiments.db'}"
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


def _create_user(
    email: str,
    password: str,
    *,
    role: str = "user",
    is_active: bool = True,
) -> UUID:
    with sessionmaker(bind=get_engine())() as session:
        user = User(
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.commit()
        return user.id


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _write_report(relative_path: str, content: bytes = b"{}") -> None:
    path = Path(Settings().storage_root) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _create_experiment(
    *,
    name: str,
    experiment_type: str,
    is_published: bool,
    created_by_user_id: UUID | None = None,
    artifacts_path: str | None = None,
) -> UUID:
    experiment_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            ExperimentRun(
                id=experiment_id,
                name=name,
                experiment_type=experiment_type,
                description="Imported metrics",
                dataset_name="Seraphim",
                config_json={"threshold": 0.25},
                artifacts_path=artifacts_path,
                is_published=is_published,
                created_by_user_id=created_by_user_id,
            )
        )
        session.commit()
        return experiment_id


def _create_model() -> UUID:
    model_id = uuid4()
    with sessionmaker(bind=get_engine())() as session:
        session.add(
            ModelVersion(
                id=model_id,
                name="YOLO26s",
                model_family="YOLO26",
                variant="s",
                weights_path=f"models/{model_id}/weights.pt",
                metrics_json={},
                is_active=False,
            )
        )
        session.commit()
        return model_id


def _import_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "YOLO26 model comparison",
        "experiment_type": "model_comparison",
        "description": "Imported from notebook artifacts",
        "model_version_id": None,
        "dataset_name": "Seraphim",
        "config_json": {"image_size": 640},
        "artifacts_path": "reports/model-comparison/metrics.json",
        "is_published": True,
        "metrics": [
            {
                "metric_name": "map50",
                "metric_value": 0.71,
                "metric_unit": None,
                "metadata_json": {"model": "YOLO26s"},
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_experiment_endpoints_require_active_user(
    experiments_client: TestClient,
) -> None:
    experiment_id = uuid4()

    list_response = experiments_client.get("/api/experiments")
    detail_response = experiments_client.get(f"/api/experiments/{experiment_id}")
    import_response = experiments_client.post("/api/experiments/import", json=_import_payload())

    assert list_response.status_code == 401
    assert detail_response.status_code == 401
    assert import_response.status_code == 401


def test_published_visibility_for_user_and_admin(
    experiments_client: TestClient,
) -> None:
    _create_user("user@example.local", "user-secret-value")
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    published_id = _create_experiment(
        name="Published run",
        experiment_type="model_comparison",
        is_published=True,
    )
    unpublished_id = _create_experiment(
        name="Draft run",
        experiment_type="threshold_analysis",
        is_published=False,
    )
    user_token = _login(experiments_client, "user@example.local", "user-secret-value")
    admin_token = _login(experiments_client, "admin@example.local", "admin-secret-value")

    user_list = experiments_client.get("/api/experiments", headers=_auth(user_token))
    user_published_detail = experiments_client.get(
        f"/api/experiments/{published_id}",
        headers=_auth(user_token),
    )
    user_unpublished_detail = experiments_client.get(
        f"/api/experiments/{unpublished_id}",
        headers=_auth(user_token),
    )
    admin_list = experiments_client.get("/api/experiments", headers=_auth(admin_token))
    admin_unpublished_detail = experiments_client.get(
        f"/api/experiments/{unpublished_id}",
        headers=_auth(admin_token),
    )

    assert user_list.status_code == 200
    assert [item["id"] for item in user_list.json()["items"]] == [str(published_id)]
    assert user_published_detail.status_code == 200
    assert user_published_detail.json()["id"] == str(published_id)
    assert user_unpublished_detail.status_code == 404
    assert admin_list.status_code == 200
    assert {item["id"] for item in admin_list.json()["items"]} == {
        str(published_id),
        str(unpublished_id),
    }
    assert admin_unpublished_detail.status_code == 200


def test_experiment_list_pagination_and_filters(
    experiments_client: TestClient,
) -> None:
    _create_user("user@example.local", "user-secret-value")
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    user_token = _login(experiments_client, "user@example.local", "user-secret-value")
    admin_token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    first_id = _create_experiment(
        name="First",
        experiment_type="model_comparison",
        is_published=True,
    )
    second_id = _create_experiment(
        name="Second",
        experiment_type="threshold_analysis",
        is_published=True,
    )
    draft_id = _create_experiment(
        name="Draft",
        experiment_type="threshold_analysis",
        is_published=False,
    )

    page_response = experiments_client.get(
        "/api/experiments?limit=1&offset=1",
        headers=_auth(admin_token),
    )
    type_response = experiments_client.get(
        "/api/experiments?experiment_type=threshold_analysis",
        headers=_auth(admin_token),
    )
    unpublished_response = experiments_client.get(
        "/api/experiments?is_published=false",
        headers=_auth(admin_token),
    )
    user_unpublished_filter = experiments_client.get(
        "/api/experiments?is_published=false",
        headers=_auth(user_token),
    )

    assert page_response.status_code == 200
    page = page_response.json()
    assert page["total"] == 3
    assert page["limit"] == 1
    assert page["offset"] == 1
    assert len(page["items"]) == 1
    assert {item["experiment_type"] for item in type_response.json()["items"]} == {
        "threshold_analysis"
    }
    assert {item["id"] for item in type_response.json()["items"]} == {
        str(second_id),
        str(draft_id),
    }
    assert [item["id"] for item in unpublished_response.json()["items"]] == [str(draft_id)]
    assert user_unpublished_filter.status_code == 200
    assert [item["id"] for item in user_unpublished_filter.json()["items"]] == [
        str(first_id),
        str(second_id),
    ]


def test_regular_user_and_inactive_admin_cannot_import(
    experiments_client: TestClient,
) -> None:
    _create_user("user@example.local", "user-secret-value")
    inactive_admin_id = _create_user(
        "inactive-admin@example.local",
        "admin-secret-value",
        role="admin",
        is_active=False,
    )
    user_token = _login(experiments_client, "user@example.local", "user-secret-value")
    inactive_token = jwt.encode(
        {"sub": str(inactive_admin_id)},
        Settings().jwt_secret_key,
        algorithm="HS256",
    )
    _write_report("reports/model-comparison/metrics.json")

    user_response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(),
        headers=_auth(user_token),
    )
    inactive_response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(),
        headers=_auth(inactive_token),
    )

    assert user_response.status_code == 403
    assert inactive_response.status_code == 401


@pytest.mark.parametrize(
    "experiment_type",
    [
        "model_comparison",
        "threshold_analysis",
        "tracker_comparison",
        "false_positive_analysis",
    ],
)
def test_admin_can_import_supported_experiment_types(
    experiments_client: TestClient,
    experiment_type: str,
) -> None:
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    model_id = _create_model()
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    artifact_path = f"reports/{experiment_type}/metrics.json"
    _write_report(artifact_path)

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(
            experiment_type=experiment_type,
            model_version_id=str(model_id),
            artifacts_path=artifact_path,
            metrics=[
                {
                    "metric_name": "video_processing_fps"
                    if experiment_type == "tracker_comparison"
                    else "map50",
                    "metric_value": None,
                    "metric_unit": "fps" if experiment_type == "tracker_comparison" else None,
                    "metadata_json": {"source": "notebook"},
                }
            ],
        ),
        headers=_auth(token),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["experiment_type"] == experiment_type
    assert body["model_version_id"] == str(model_id)
    assert body["created_by_user_id"] == str(admin_id)
    assert body["metrics"][0]["metric_value"] is None
    assert str(Path(Settings().storage_root)) not in response.text


@pytest.mark.parametrize(
    "experiment_type",
    ["tracking_accuracy", "tracker_behavior_comparison"],
)
def test_import_rejects_unsupported_experiment_types(
    experiments_client: TestClient,
    experiment_type: str,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    _write_report("reports/invalid/metrics.json")

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(
            experiment_type=experiment_type,
            artifacts_path="reports/invalid/metrics.json",
        ),
        headers=_auth(token),
    )

    assert response.status_code == 422


def test_import_rejects_missing_model_version_safely(
    experiments_client: TestClient,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    _write_report("reports/model-comparison/metrics.json")

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(model_version_id=str(uuid4())),
        headers=_auth(token),
    )

    assert response.status_code == 400
    assert "FOREIGN KEY" not in response.text
    assert "Traceback" not in response.text
    assert str(Path(Settings().storage_root)) not in response.text


@pytest.mark.parametrize(
    "metric",
    [
        {"metric_name": "tracking_accuracy", "metric_value": 0.9, "metadata_json": {}},
        {"metric_name": "tracking_accuracy_score", "metric_value": 0.9, "metadata_json": {}},
        {"metric_name": "MOTA", "metric_value": 0.9, "metadata_json": {}},
        {"metric_name": "mota_score", "metric_value": 0.9, "metadata_json": {}},
        {"metric_name": "IDF1", "metric_value": 0.9, "metadata_json": {}},
        {"metric_name": "HOTA", "metric_value": 0.9, "metadata_json": {}},
        {
            "metric_name": "video_processing_fps",
            "metric_value": 12.0,
            "metadata_json": {"label": "tracking_accuracy"},
        },
        {
            "metric_name": "video_processing_fps",
            "metric_value": 12.0,
            "metadata_json": {"label": "IDF1 metric"},
        },
    ],
)
def test_tracker_comparison_rejects_accuracy_metric_wording(
    experiments_client: TestClient,
    metric: dict[str, object],
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    _write_report("reports/tracker-comparison/metrics.json")

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(
            experiment_type="tracker_comparison",
            artifacts_path="reports/tracker-comparison/metrics.json",
            metrics=[metric],
        ),
        headers=_auth(token),
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "artifact_path",
    [
        "/app/storage/reports/exp/metrics.json",
        "C:/storage/reports/exp/metrics.json",
        "../reports/exp/metrics.json",
        "reports/../secret/metrics.json",
        "temp/experiment/metrics.json",
        "reports/missing/metrics.json",
    ],
)
def test_import_rejects_unsafe_or_missing_artifact_paths(
    experiments_client: TestClient,
    artifact_path: str,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    if artifact_path == "temp/experiment/metrics.json":
        _write_report(artifact_path)

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(artifacts_path=artifact_path),
        headers=_auth(token),
    )

    assert response.status_code == 400
    assert str(Path(Settings().storage_root)) not in response.text


def test_import_rejects_metadata_with_absolute_paths_and_has_no_training_side_effect(
    experiments_client: TestClient,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    _write_report("reports/model-comparison/metrics.json")

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(
            metrics=[
                {
                    "metric_name": "map50",
                    "metric_value": 0.7,
                    "metric_unit": None,
                    "metadata_json": {"path": str(Path(Settings().storage_root) / "secret")},
                }
            ]
        ),
        headers=_auth(token),
    )

    assert response.status_code == 400
    assert str(Path(Settings().storage_root)) not in response.text
    with sessionmaker(bind=get_engine())() as session:
        assert session.scalar(select(ProcessingJob)) is None


def test_import_rejects_config_json_with_absolute_paths(
    experiments_client: TestClient,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(experiments_client, "admin@example.local", "admin-secret-value")
    _write_report("reports/model-comparison/metrics.json")

    response = experiments_client.post(
        "/api/experiments/import",
        json=_import_payload(
            config_json={"artifact": str(Path(Settings().storage_root) / "report.json")}
        ),
        headers=_auth(token),
    )

    assert response.status_code == 400
    assert str(Path(Settings().storage_root)) not in response.text
