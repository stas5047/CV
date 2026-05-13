from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TrackerType = Literal["bytetrack", "botsort"]


class JobCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    media_id: UUID
    model_version_id: UUID | None = None
    confidence_threshold: float | None = Field(default=None, ge=0, le=1)
    iou_threshold: float | None = Field(default=None, ge=0, le=1)
    tracker_type: TrackerType | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    media_file_id: UUID
    model_version_id: UUID | None
    status: str
    input_params_json: dict[str, Any]
    summary_json: dict[str, Any] | None
    error_message: str | None
    progress_percent: int
    last_heartbeat_at: datetime | None
    locked_by: str | None
    locked_at: datetime | None
    retry_count: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
