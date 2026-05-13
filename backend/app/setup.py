from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.passwords import hash_password
from app.db.models import User
from app.db.session import get_session_factory

logger = logging.getLogger(__name__)

REQUIRED_STORAGE_DIRS = (
    "uploads",
    "results",
    "reports",
    "models",
    "temp",
    "datasets",
)


class SeedConflictError(RuntimeError):
    pass


@dataclass(frozen=True)
class SetupResult:
    storage_dirs_created: tuple[str, ...]
    admin_created: bool
    admin_updated: bool


def bootstrap_storage(storage_root: str) -> tuple[str, ...]:
    root = Path(storage_root)
    root.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    for name in REQUIRED_STORAGE_DIRS:
        directory = root / name
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if not existed:
            created.append(name)
    return tuple(created)


def seed_admin(session: Session, settings: Settings) -> tuple[bool, bool]:
    email = settings.admin_email.strip().lower()
    existing = session.scalar(select(User).where(User.email == email))

    if existing is None:
        session.add(
            User(
                email=email,
                password_hash=hash_password(settings.admin_password),
                role="admin",
                is_active=True,
            )
        )
        session.commit()
        return True, False

    if existing.role != "admin":
        session.rollback()
        raise SeedConflictError("ADMIN_EMAIL already belongs to a non-admin user")

    existing.password_hash = hash_password(settings.admin_password)
    existing.is_active = True
    session.commit()
    return False, True


def run_setup(
    settings: Settings | None = None,
    session_factory: sessionmaker | None = None,
) -> SetupResult:
    settings = settings or get_settings()
    session_factory = session_factory or get_session_factory()

    created_dirs = bootstrap_storage(settings.storage_root)
    with session_factory() as session:
        admin_created, admin_updated = seed_admin(session, settings)

    return SetupResult(
        storage_dirs_created=created_dirs,
        admin_created=admin_created,
        admin_updated=admin_updated,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    result = run_setup()
    logger.info(
        "setup complete: storage_dirs_created=%s admin_created=%s admin_updated=%s",
        len(result.storage_dirs_created),
        result.admin_created,
        result.admin_updated,
    )


if __name__ == "__main__":
    main()
