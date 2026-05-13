from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    original_filename: str
    media_type: str
    mime_type: str
    file_size_bytes: int
    width: int | None
    height: int | None
    frame_count: int | None
    fps: float | None
    duration_seconds: float | None
    created_at: datetime


class MediaListResponse(BaseModel):
    items: list[MediaResponse]
    total: int
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
