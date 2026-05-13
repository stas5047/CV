from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.config import Settings, get_settings
from app.db.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token_subject(token: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise auth_error() from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise auth_error()
    return subject


def user_from_credentials(
    credentials: HTTPAuthorizationCredentials | None,
    session: Session,
    settings: Settings,
) -> User | None:
    if credentials is None:
        return None

    subject = decode_token_subject(credentials.credentials, settings)
    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise auth_error() from exc

    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise auth_error()
    return user


def get_optional_authenticated_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    try:
        return user_from_credentials(credentials, session, settings)
    except HTTPException:
        return None


def get_current_active_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    user = user_from_credentials(credentials, session, settings)
    if user is None or not user.is_active:
        raise auth_error()
    return user


def auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
