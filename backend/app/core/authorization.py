from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.db.models import User

OwnerIdGetter = Callable[[Any], UUID | None]

SAFE_NOT_FOUND_DETAIL = "Resource not found"


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


def ensure_owner_or_admin[ResourceT](
    resource: ResourceT | None,
    current_user: User,
    owner_id_getter: OwnerIdGetter,
    *,
    not_found_detail: str = SAFE_NOT_FOUND_DETAIL,
) -> ResourceT:
    if resource is None:
        raise _resource_not_found(not_found_detail)

    if current_user.role == "admin":
        return resource

    owner_id = owner_id_getter(resource)
    if owner_id != current_user.id:
        raise _resource_not_found(not_found_detail)

    return resource


def owner_id_from_user_field(resource: Any) -> UUID | None:
    owner_id = getattr(resource, "user_id", None)
    return owner_id if isinstance(owner_id, UUID) else None


def owner_id_from_media(resource: Any) -> UUID | None:
    media_file = getattr(resource, "media_file", None)
    if media_file is not None:
        return owner_id_from_user_field(media_file)
    return owner_id_from_user_field(resource)


def owner_id_from_job(resource: Any) -> UUID | None:
    job = getattr(resource, "job", None) or resource
    media_file = getattr(job, "media_file", None)
    if media_file is not None:
        return owner_id_from_user_field(media_file)
    return owner_id_from_user_field(job)


def _resource_not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
