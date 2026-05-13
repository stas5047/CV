from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.auth import UserResponse
from app.schemas.jobs import JobDetailResponse


class AdminUsersStats(BaseModel):
    total: int
    active: int
    admins: int


class AdminMediaStats(BaseModel):
    total: int
    images: int
    videos: int


class AdminJobsStats(BaseModel):
    total: int
    by_status: dict[str, int]


class AdminCountStats(BaseModel):
    total: int


class AdminModelsStats(BaseModel):
    total: int
    active: int


class AdminExperimentsStats(BaseModel):
    total: int
    published: int


class AdminStatsResponse(BaseModel):
    users: AdminUsersStats
    media: AdminMediaStats
    jobs: AdminJobsStats
    detections: AdminCountStats
    tracks: AdminCountStats
    models: AdminModelsStats
    experiments: AdminExperimentsStats


class AdminUserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class AdminJobListResponse(BaseModel):
    items: list[JobDetailResponse]
    total: int
    limit: int
    offset: int


class StorageCleanupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dry_run: bool = False


class StorageCleanupResponse(BaseModel):
    dry_run: bool
    scanned_files: int
    deleted_files: int
    would_delete_files: int
    protected_files: int
    reported_files: int
    skipped_files: int
    deleted_by_category: dict[str, int]
    would_delete_by_category: dict[str, int]
    protected_by_category: dict[str, int]
    reported_by_category: dict[str, int]
    skipped_by_category: dict[str, int]
