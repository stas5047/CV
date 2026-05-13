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


class JobMediaReference(BaseModel):
    id: UUID
    original_filename: str
    media_type: str
    width: int | None
    height: int | None
    frame_count: int | None
    fps: float | None
    duration_seconds: float | None


class JobModelReference(BaseModel):
    id: UUID
    name: str
    model_family: str
    variant: str


class JobDownloadReference(BaseModel):
    available: bool
    download_url: str


class JobResultReferences(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    media: JobDownloadReference
    csv: JobDownloadReference
    json_export: JobDownloadReference = Field(alias="json")


class JobDetailResponse(BaseModel):
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
    media: JobMediaReference
    model: JobModelReference | None
    result: JobResultReferences


class JobListResponse(BaseModel):
    items: list[JobDetailResponse]
    total: int
    limit: int
    offset: int


class JobSummaryResponse(BaseModel):
    job_id: UUID
    status: str
    summary: dict[str, Any]


class DetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    media_file_id: UUID
    frame_index: int
    timestamp_ms: int
    class_id: int
    class_name: str
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    center_x: float
    center_y: float
    bbox_width: float
    bbox_height: float
    frame_width: int
    frame_height: int
    track_id: int | None
    created_at: datetime


class DetectionListResponse(BaseModel):
    items: list[DetectionResponse]
    total: int
    limit: int
    offset: int


class TrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    track_id: int
    class_name: str
    first_frame_index: int
    last_frame_index: int
    frames_count: int
    average_confidence: float | None
    max_confidence: float | None
    created_at: datetime


class TrackListResponse(BaseModel):
    items: list[TrackResponse]
    total: int
    limit: int
    offset: int


class JobResultResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_id: UUID
    status: str
    summary: dict[str, Any] | None
    media: JobDownloadReference
    csv: JobDownloadReference
    json_export: JobDownloadReference = Field(alias="json")
