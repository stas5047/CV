from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.storage_paths import safe_join_storage_path, validate_relative_storage_path
from app.db.models import (
    Detection,
    ExperimentRun,
    MediaFile,
    ModelVersion,
    ProcessingJob,
    Track,
    User,
)
from app.schemas.admin import (
    AdminCountStats,
    AdminExperimentsStats,
    AdminJobsStats,
    AdminMediaStats,
    AdminModelsStats,
    AdminStatsResponse,
    AdminUsersStats,
    StorageCleanupResponse,
)
from app.schemas.auth import UserResponse

LOGGER = logging.getLogger(__name__)
STORAGE_CATEGORIES = {"uploads", "results", "reports", "models", "temp", "datasets"}


def get_admin_stats(session: Session) -> AdminStatsResponse:
    return AdminStatsResponse(
        users=AdminUsersStats(
            total=_count(session, User),
            active=_count(session, User, User.is_active.is_(True)),
            admins=_count(session, User, User.role == "admin"),
        ),
        media=AdminMediaStats(
            total=_count(session, MediaFile),
            images=_count(session, MediaFile, MediaFile.media_type == "image"),
            videos=_count(session, MediaFile, MediaFile.media_type == "video"),
        ),
        jobs=AdminJobsStats(
            total=_count(session, ProcessingJob),
            by_status=_job_status_counts(session),
        ),
        detections=AdminCountStats(total=_count(session, Detection)),
        tracks=AdminCountStats(total=_count(session, Track)),
        models=AdminModelsStats(
            total=_count(session, ModelVersion),
            active=_count(session, ModelVersion, ModelVersion.is_active.is_(True)),
        ),
        experiments=AdminExperimentsStats(
            total=_count(session, ExperimentRun),
            published=_count(session, ExperimentRun, ExperimentRun.is_published.is_(True)),
        ),
    )


def list_admin_users(
    session: Session,
    *,
    limit: int,
    offset: int,
) -> tuple[list[UserResponse], int]:
    total = _count(session, User)
    users = list(
        session.scalars(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
    )
    return [UserResponse.model_validate(user) for user in users], total


def cleanup_storage(
    session: Session,
    *,
    storage_root: str,
    dry_run: bool,
) -> StorageCleanupResponse:
    root = Path(storage_root).resolve()
    protected_exact, protected_prefixes = _protected_storage_paths(session)
    result = _CleanupAccumulator(dry_run=dry_run)

    if not root.exists():
        return result.response()

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        result.scanned_files += 1
        relative_path = _safe_relative_file(root, file_path)
        if relative_path is None:
            result.skipped(_category_for_path(""))
            continue

        category = _category_for_path(relative_path)
        if _is_protected(relative_path, protected_exact, protected_prefixes):
            result.protected(category)
            continue

        if category == "temp":
            if dry_run:
                result.would_delete(category)
            else:
                file_path.unlink()
                result.deleted(category)
            continue

        result.reported(category)

    response = result.response()
    LOGGER.info(
        "admin storage cleanup scanned=%s deleted=%s would_delete=%s protected=%s "
        "reported=%s skipped=%s dry_run=%s",
        response.scanned_files,
        response.deleted_files,
        response.would_delete_files,
        response.protected_files,
        response.reported_files,
        response.skipped_files,
        response.dry_run,
    )
    return response


def _count(session: Session, model: type[object], *predicates: object) -> int:
    statement = select(func.count()).select_from(model)
    for predicate in predicates:
        statement = statement.where(predicate)
    return session.scalar(statement) or 0


def _job_status_counts(session: Session) -> dict[str, int]:
    counts = {"queued": 0, "processing": 0, "completed": 0, "failed": 0, "cancelled": 0}
    rows = session.execute(
        select(ProcessingJob.status, func.count()).group_by(ProcessingJob.status)
    ).all()
    for status, count in rows:
        counts[str(status)] = int(count)
    return counts


def _protected_storage_paths(session: Session) -> tuple[set[str], set[str]]:
    exact: set[str] = set()
    prefixes: set[str] = set()

    for path in session.scalars(
        select(MediaFile.stored_path).where(MediaFile.deleted_at.is_(None))
    ):
        _add_exact_path(exact, path)

    for job in session.scalars(select(ProcessingJob).where(ProcessingJob.deleted_at.is_(None))):
        _add_exact_path(exact, job.result_media_path)
        _add_exact_path(exact, job.csv_path)
        _add_exact_path(exact, job.json_path)

    for model in session.scalars(select(ModelVersion)):
        _add_exact_path(exact, model.weights_path)
        if model.is_active:
            _add_model_card_protection(exact, prefixes, model.id, model.weights_path)

    for artifacts_path in session.scalars(select(ExperimentRun.artifacts_path)):
        _add_prefix_or_exact(exact, prefixes, artifacts_path)

    return exact, prefixes


def _add_exact_path(target: set[str], path: str | None) -> None:
    if path is None:
        return
    try:
        target.add(validate_relative_storage_path(path))
    except ValueError:
        return


def _add_prefix_or_exact(exact: set[str], prefixes: set[str], path: str | None) -> None:
    if path is None:
        return
    try:
        normalized = validate_relative_storage_path(path).rstrip("/")
    except ValueError:
        return
    if Path(normalized).suffix:
        exact.add(normalized)
    else:
        prefixes.add(f"{normalized}/")


def _add_model_card_protection(
    exact: set[str],
    prefixes: set[str],
    model_id: UUID,
    weights_path: str,
) -> None:
    try:
        normalized = validate_relative_storage_path(weights_path)
    except ValueError:
        exact.add(f"models/{model_id}/model_card.json")
        prefixes.add(f"models/{model_id}/")
        return

    parent = str(Path(normalized).parent).replace("\\", "/")
    if parent and parent != ".":
        prefixes.add(f"{parent.rstrip('/')}/")
        exact.add(f"{parent.rstrip('/')}/model_card.json")
    exact.add(f"models/{model_id}/model_card.json")
    prefixes.add(f"models/{model_id}/")


def _safe_relative_file(root: Path, file_path: Path) -> str | None:
    try:
        relative_path = file_path.resolve().relative_to(root).as_posix()
        safe_join_storage_path(root, relative_path)
        return validate_relative_storage_path(relative_path)
    except ValueError:
        return None


def _category_for_path(relative_path: str) -> str:
    category = relative_path.split("/", 1)[0] if relative_path else "unknown"
    return category if category in STORAGE_CATEGORIES else "unknown"


def _is_protected(relative_path: str, exact: set[str], prefixes: set[str]) -> bool:
    return relative_path in exact or any(relative_path.startswith(prefix) for prefix in prefixes)


class _CleanupAccumulator:
    def __init__(self, *, dry_run: bool) -> None:
        self.dry_run = dry_run
        self.scanned_files = 0
        self.deleted_files = 0
        self.would_delete_files = 0
        self.protected_files = 0
        self.reported_files = 0
        self.skipped_files = 0
        self.deleted_by_category: dict[str, int] = {}
        self.would_delete_by_category: dict[str, int] = {}
        self.protected_by_category: dict[str, int] = {}
        self.reported_by_category: dict[str, int] = {}
        self.skipped_by_category: dict[str, int] = {}

    def deleted(self, category: str) -> None:
        self.deleted_files += 1
        self._increment(self.deleted_by_category, category)

    def would_delete(self, category: str) -> None:
        self.would_delete_files += 1
        self._increment(self.would_delete_by_category, category)

    def protected(self, category: str) -> None:
        self.protected_files += 1
        self._increment(self.protected_by_category, category)

    def reported(self, category: str) -> None:
        self.reported_files += 1
        self._increment(self.reported_by_category, category)

    def skipped(self, category: str) -> None:
        self.skipped_files += 1
        self._increment(self.skipped_by_category, category)

    def response(self) -> StorageCleanupResponse:
        return StorageCleanupResponse(
            dry_run=self.dry_run,
            scanned_files=self.scanned_files,
            deleted_files=self.deleted_files,
            would_delete_files=self.would_delete_files,
            protected_files=self.protected_files,
            reported_files=self.reported_files,
            skipped_files=self.skipped_files,
            deleted_by_category=self.deleted_by_category,
            would_delete_by_category=self.would_delete_by_category,
            protected_by_category=self.protected_by_category,
            reported_by_category=self.reported_by_category,
            skipped_by_category=self.skipped_by_category,
        )

    @staticmethod
    def _increment(bucket: dict[str, int], category: str) -> None:
        bucket[category] = bucket.get(category, 0) + 1
