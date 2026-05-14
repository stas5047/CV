from __future__ import annotations

import time
from collections.abc import Callable

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def create_worker_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(
        bind=create_worker_engine(database_url),
        autoflush=False,
        autocommit=False,
    )


def check_database(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        session.execute(text("select 1")).scalar_one()


def wait_for_database(
    check: Callable[[], None],
    *,
    attempts: int,
    delay_seconds: float,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            check()
            return
        except Exception as exc:
            last_error = exc
            if attempt < attempts and delay_seconds > 0:
                time.sleep(delay_seconds)
    raise RuntimeError(f"database unavailable after {attempts} attempts") from last_error
