from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import hash_password
from app.db.models import Base, ModelVersion, User
from app.db.session import get_engine
from app.main import create_app


@pytest.fixture
def models_client(
    required_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    database_url = f"sqlite+pysqlite:///{tmp_path / 'models.db'}"
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
    factory = sessionmaker(bind=get_engine())
    with factory() as session:
        user = User(
            email=email.strip().lower(),
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.commit()
        return user.id


def _create_weights(path: Path, relative_path: str) -> None:
    weights = path / "storage" / relative_path
    weights.parent.mkdir(parents=True, exist_ok=True)
    weights.write_bytes(b"test-weights")


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _model_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "name": "YOLO26s Seraphim subset v1",
        "model_family": "YOLO26",
        "variant": "s",
        "weights_path": "models/yolo26s-seraphim-subset-v1/weights.pt",
        "dataset_name": "Seraphim",
        "dataset_split_description": "16k train / 2k val / 2k test",
        "metrics_json": {"map50": 0.7},
        "is_active": False,
    }
    payload.update(overrides)
    return payload


def _register_model(
    client: TestClient,
    token: str,
    tmp_path: Path,
    **overrides: object,
) -> dict[str, object]:
    payload = _model_payload(**overrides)
    _create_weights(tmp_path, str(payload["weights_path"]))
    response = client.post("/api/models", json=payload, headers=_auth(token))
    assert response.status_code == 201, response.text
    return response.json()


def test_model_endpoints_require_active_user(models_client: TestClient) -> None:
    list_response = models_client.get("/api/models")
    detail_response = models_client.get(f"/api/models/{UUID(int=0)}")

    assert list_response.status_code == 401
    assert detail_response.status_code == 401


def test_inactive_user_token_cannot_list_models(models_client: TestClient) -> None:
    user_id = _create_user("inactive@example.local", "user-secret-value", is_active=False)
    token = jwt.encode({"sub": str(user_id)}, Settings().jwt_secret_key, algorithm="HS256")

    response = models_client.get("/api/models", headers=_auth(token))

    assert response.status_code == 401


def test_authenticated_user_can_list_and_fetch_models(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    _create_user("user@example.local", "user-secret-value")
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    user_token = _login(models_client, "user@example.local", "user-secret-value")
    admin_token = _login(models_client, "admin@example.local", "admin-secret-value")
    model = _register_model(models_client, admin_token, tmp_path)

    list_response = models_client.get("/api/models", headers=_auth(user_token))
    detail_response = models_client.get(f"/api/models/{model['id']}", headers=_auth(user_token))

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == model["id"]
    assert detail_response.status_code == 200
    assert detail_response.json()["weights_path"] == model["weights_path"]
    assert str(tmp_path) not in list_response.text
    assert str(tmp_path) not in detail_response.text


def test_regular_user_cannot_register_or_activate_model(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    _create_user("user@example.local", "user-secret-value")
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    user_token = _login(models_client, "user@example.local", "user-secret-value")
    admin_token = _login(models_client, "admin@example.local", "admin-secret-value")
    model = _register_model(models_client, admin_token, tmp_path)
    _create_weights(tmp_path, "models/blocked/weights.pt")

    create_response = models_client.post(
        "/api/models",
        json=_model_payload(weights_path="models/blocked/weights.pt"),
        headers=_auth(user_token),
    )
    activate_response = models_client.patch(
        f"/api/models/{model['id']}/activate",
        headers=_auth(user_token),
    )

    assert create_response.status_code == 403
    assert activate_response.status_code == 403


def test_inactive_admin_token_cannot_register_model(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    admin_id = _create_user(
        "inactive-admin@example.local",
        "admin-secret-value",
        role="admin",
        is_active=False,
    )
    _create_weights(tmp_path, "models/inactive-admin/weights.pt")
    token = jwt.encode({"sub": str(admin_id)}, Settings().jwt_secret_key, algorithm="HS256")

    response = models_client.post(
        "/api/models",
        json=_model_payload(weights_path="models/inactive-admin/weights.pt"),
        headers=_auth(token),
    )

    assert response.status_code == 401


def test_admin_registers_yolo26_and_yolo11_metadata(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")

    yolo26 = _register_model(models_client, token, tmp_path)
    yolo11 = _register_model(
        models_client,
        token,
        tmp_path,
        name="YOLO11s fallback",
        model_family="YOLO11",
        weights_path="models/yolo11s-fallback-v1/weights.pt",
        metrics_json={"fallback_reason": "YOLO26 unavailable in training environment"},
    )

    assert yolo26["model_family"] == "YOLO26"
    assert yolo11["model_family"] == "YOLO11"
    assert yolo11["metrics_json"]["fallback_reason"] == (
        "YOLO26 unavailable in training environment"
    )
    assert "password_hash" not in str(yolo11)


def test_admin_activates_exactly_one_model(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")
    first = _register_model(
        models_client,
        token,
        tmp_path,
        weights_path="models/first/weights.pt",
        is_active=True,
    )
    second = _register_model(
        models_client,
        token,
        tmp_path,
        weights_path="models/second/weights.pt",
    )

    response = models_client.patch(f"/api/models/{second['id']}/activate", headers=_auth(token))

    assert response.status_code == 200
    assert response.json()["id"] == second["id"]
    assert response.json()["is_active"] is True
    with sessionmaker(bind=get_engine())() as session:
        active_models = list(session.scalars(select(ModelVersion).where(ModelVersion.is_active)))
        first_model = session.get(ModelVersion, UUID(first["id"]))
    assert [model.id for model in active_models] == [UUID(second["id"])]
    assert first_model is not None
    assert first_model.is_active is False


def test_activation_rejects_model_with_missing_weights_file(
    models_client: TestClient,
) -> None:
    admin_id = _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")
    with sessionmaker(bind=get_engine())() as session:
        model = ModelVersion(
            name="Manually inserted missing model",
            model_family="YOLO26",
            variant="s",
            weights_path="models/manual-missing/weights.pt",
            dataset_name="Seraphim",
            dataset_split_description="train/val/test",
            metrics_json={},
            is_active=False,
            created_by_user_id=admin_id,
        )
        session.add(model)
        session.commit()
        model_id = model.id

    response = models_client.patch(f"/api/models/{model_id}/activate", headers=_auth(token))

    assert response.status_code == 400
    with sessionmaker(bind=get_engine())() as session:
        refreshed_model = session.get(ModelVersion, model_id)
    assert refreshed_model is not None
    assert refreshed_model.is_active is False


def test_model_registration_rejects_invalid_family(
    models_client: TestClient,
    tmp_path: Path,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")
    _create_weights(tmp_path, "models/invalid-family/weights.pt")

    response = models_client.post(
        "/api/models",
        json=_model_payload(
            model_family="YOLO10",
            weights_path="models/invalid-family/weights.pt",
        ),
        headers=_auth(token),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "weights_path",
    [
        "/app/storage/models/weights.pt",
        "C:/storage/models/weights.pt",
        "../weights.pt",
        "models/../weights.pt",
        "temp/model.pt",
    ],
)
def test_model_registration_rejects_unsafe_or_outside_paths(
    models_client: TestClient,
    tmp_path: Path,
    weights_path: str,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")
    if weights_path == "temp/model.pt":
        _create_weights(tmp_path, weights_path)

    response = models_client.post(
        "/api/models",
        json=_model_payload(weights_path=weights_path),
        headers=_auth(token),
    )

    assert response.status_code == 400
    assert str(tmp_path) not in response.text


def test_model_registration_rejects_missing_weights_file(
    models_client: TestClient,
) -> None:
    _create_user("admin@example.local", "admin-secret-value", role="admin")
    token = _login(models_client, "admin@example.local", "admin-secret-value")

    response = models_client.post(
        "/api/models",
        json=_model_payload(weights_path="models/missing/weights.pt"),
        headers=_auth(token),
    )

    assert response.status_code == 400
