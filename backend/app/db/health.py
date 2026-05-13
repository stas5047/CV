from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_engine


class DatabaseHealthError(RuntimeError):
    """Raised when the database health probe cannot complete."""


def check_database() -> None:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise DatabaseHealthError("database unavailable") from exc
