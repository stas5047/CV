from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CvDevice = Literal["auto", "cpu", "cuda"]


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    database_url: str = Field(alias="DATABASE_URL")
    storage_root: str = Field(default="/app/storage", alias="STORAGE_ROOT")
    models_root: str = Field(default="/app/storage/models", alias="MODELS_ROOT")
    cv_device: CvDevice = Field(default="cpu", alias="CV_DEVICE")
    active_model_id: str | None = Field(default=None, alias="ACTIVE_MODEL_ID")
    poll_interval_seconds: int = Field(default=2, gt=0, alias="WORKER_POLL_INTERVAL_SECONDS")
    heartbeat_frames: int = Field(default=30, gt=0, alias="WORKER_HEARTBEAT_FRAMES")
    heartbeat_seconds: int = Field(default=2, gt=0, alias="WORKER_HEARTBEAT_SECONDS")
    stale_job_minutes: int = Field(default=10, gt=0, alias="WORKER_STALE_JOB_MINUTES")
    max_retries: int = Field(default=2, ge=0, alias="WORKER_MAX_RETRIES")

    def safe_log_payload(self) -> dict[str, str | int | None]:
        return {
            "database_url": "<redacted>",
            "storage_root": "<path>",
            "models_root": "<path>",
            "cv_device": self.cv_device,
            "active_model_id": self.active_model_id or None,
            "poll_interval_seconds": self.poll_interval_seconds,
            "heartbeat_frames": self.heartbeat_frames,
            "heartbeat_seconds": self.heartbeat_seconds,
            "stale_job_minutes": self.stale_job_minutes,
            "max_retries": self.max_retries,
        }


@lru_cache
def get_settings() -> WorkerSettings:
    return WorkerSettings()
