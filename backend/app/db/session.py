from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory() -> sessionmaker:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
