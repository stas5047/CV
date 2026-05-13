from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.core.passwords import verify_password
from app.db.models import Base, User
from app.setup import REQUIRED_STORAGE_DIRS, SeedConflictError, bootstrap_storage, run_setup


@pytest.fixture
def settings(required_env: None, tmp_path: Path) -> Settings:
    return Settings(storage_root=str(tmp_path))


@pytest.fixture
def db_session_factory() -> Iterator[sessionmaker]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_bootstrap_storage_creates_required_dirs_and_is_idempotent(tmp_path: Path) -> None:
    first_created = bootstrap_storage(str(tmp_path))
    second_created = bootstrap_storage(str(tmp_path))

    assert set(first_created) == set(REQUIRED_STORAGE_DIRS)
    assert second_created == ()
    for name in REQUIRED_STORAGE_DIRS:
        assert (tmp_path / name).is_dir()


def test_run_setup_creates_admin_with_hashed_password(
    settings: Settings,
    db_session_factory: sessionmaker,
) -> None:
    result = run_setup(settings, db_session_factory)

    with db_session_factory() as session:
        admin = session.scalar(select(User).where(User.email == "admin@example.local"))

    assert result.admin_created is True
    assert result.admin_updated is False
    assert admin is not None
    assert admin.role == "admin"
    assert admin.is_active is True
    assert admin.password_hash != "admin-secret-value"
    assert verify_password("admin-secret-value", admin.password_hash)


def test_run_setup_is_idempotent_and_refreshes_existing_admin_hash(
    settings: Settings,
    db_session_factory: sessionmaker,
) -> None:
    run_setup(settings, db_session_factory)
    updated_settings = Settings(
        storage_root=settings.storage_root,
        admin_password="new-secret-value",
    )

    result = run_setup(updated_settings, db_session_factory)

    with db_session_factory() as session:
        admins = session.scalars(select(User).where(User.email == "admin@example.local")).all()

    assert result.admin_created is False
    assert result.admin_updated is True
    assert len(admins) == 1
    assert verify_password("new-secret-value", admins[0].password_hash)


def test_run_setup_fails_when_admin_email_belongs_to_regular_user(
    settings: Settings,
    db_session_factory: sessionmaker,
) -> None:
    with db_session_factory() as session:
        session.add(
            User(
                email="admin@example.local",
                password_hash="existing-hash",
                role="user",
                is_active=True,
            )
        )
        session.commit()

    with pytest.raises(SeedConflictError):
        run_setup(settings, db_session_factory)

    with db_session_factory() as session:
        user = session.scalar(select(User).where(User.email == "admin@example.local"))

    assert user is not None
    assert user.role == "user"
    assert user.password_hash == "existing-hash"
