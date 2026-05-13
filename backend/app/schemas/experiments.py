from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

ExperimentType = Literal[
    "model_comparison",
    "threshold_analysis",
    "tracker_comparison",
    "false_positive_analysis",
]


class ExperimentMetricImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_name: str = Field(min_length=1, max_length=255)
    metric_value: float | None = None
    metric_unit: str | None = Field(default=None, max_length=80)
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    @field_validator("metric_name", "metric_unit", mode="before")
    @classmethod
    def strip_string(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class ExperimentImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    experiment_type: ExperimentType
    description: str | None = None
    model_version_id: UUID | None = None
    dataset_name: str | None = Field(default=None, max_length=255)
    config_json: dict[str, Any] = Field(default_factory=dict)
    artifacts_path: str | None = Field(default=None, max_length=2048)
    is_published: bool = False
    metrics: list[ExperimentMetricImportRequest] = Field(default_factory=list)

    @field_validator("name", "description", "dataset_name", "artifacts_path", mode="before")
    @classmethod
    def strip_optional_string(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class ExperimentMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    experiment_run_id: UUID
    metric_name: str
    metric_value: float | None
    metric_unit: str | None
    metadata_json: dict[str, Any]
    created_at: datetime


class ExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    experiment_type: str
    description: str | None
    model_version_id: UUID | None
    dataset_name: str | None
    config_json: dict[str, Any]
    artifacts_path: str | None
    is_published: bool
    created_by_user_id: UUID | None
    created_at: datetime
    metrics: list[ExperimentMetricResponse] = Field(default_factory=list)


class ExperimentListResponse(BaseModel):
    items: list[ExperimentResponse]
    total: int
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
