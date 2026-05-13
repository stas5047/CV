from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

ModelFamily = Literal["YOLO26", "YOLO11"]


class ModelCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    model_family: ModelFamily
    variant: str = Field(min_length=1, max_length=50)
    weights_path: str = Field(min_length=1, max_length=2048)
    dataset_name: str | None = Field(default=None, max_length=255)
    dataset_split_description: str | None = None
    metrics_json: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = False

    @field_validator("name", "variant", "weights_path", "dataset_name", mode="before")
    @classmethod
    def strip_string(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    model_family: str
    variant: str
    weights_path: str
    dataset_name: str | None
    dataset_split_description: str | None
    metrics_json: dict[str, Any]
    is_active: bool
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime


class ModelListResponse(BaseModel):
    items: list[ModelResponse]
    total: int
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
