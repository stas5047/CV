from __future__ import annotations

import shutil
import struct
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.storage_paths import (
    safe_join_storage_path,
    sanitize_upload_filename,
    validate_relative_storage_path,
)
from app.db.models import MediaFile, User, utc_now

IMAGE_MIME_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
VIDEO_MIME_BY_EXTENSION = {
    ".mp4": {"video/mp4"},
    ".avi": {"video/x-msvideo", "video/avi"},
    ".mov": {"video/quicktime"},
    ".mkv": {"video/x-matroska", "video/matroska"},
}
CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class MediaMetadata:
    width: int | None
    height: int | None
    frame_count: int | None
    fps: float | None
    duration_seconds: float | None


def create_media_from_upload(
    *,
    session: Session,
    current_user: User,
    upload: UploadFile,
    storage_root: str,
    max_image_size_mb: int,
    max_video_size_mb: int,
) -> MediaFile:
    sanitized_filename = _sanitize_required_filename(upload.filename)
    extension = Path(sanitized_filename).suffix.lower()
    media_type = _media_type_for_extension(extension)
    expected_mime = _validate_content_type(extension, upload.content_type)
    max_bytes = _max_bytes(media_type, max_image_size_mb, max_video_size_mb)
    media_id = uuid4()
    stored_path = _stored_path(current_user.id, media_id, extension)
    final_path = safe_join_storage_path(storage_root, stored_path)
    final_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = _write_limited_temp(upload, max_bytes, final_path.parent)
    try:
        metadata = _extract_metadata(temp_path, media_type, extension)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temp_path), final_path)
        media = MediaFile(
            id=media_id,
            user_id=current_user.id,
            original_filename=sanitized_filename,
            stored_path=stored_path,
            media_type=media_type,
            mime_type=expected_mime,
            file_size_bytes=final_path.stat().st_size,
            width=metadata.width,
            height=metadata.height,
            frame_count=metadata.frame_count,
            fps=metadata.fps,
            duration_seconds=metadata.duration_seconds,
        )
        session.add(media)
        session.commit()
        session.refresh(media)
        return media
    except Exception:
        _cleanup_path(temp_path)
        _cleanup_path(final_path)
        raise


def list_visible_media(
    *,
    session: Session,
    current_user: User,
    limit: int,
    offset: int,
    media_type: str | None,
    owner_id: UUID | None,
) -> tuple[list[MediaFile], int]:
    statement = select(MediaFile).where(MediaFile.deleted_at.is_(None))
    count_statement = (
        select(func.count()).select_from(MediaFile).where(MediaFile.deleted_at.is_(None))
    )

    if media_type is not None:
        if media_type not in {"image", "video"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid media type",
            )
        statement = statement.where(MediaFile.media_type == media_type)
        count_statement = count_statement.where(MediaFile.media_type == media_type)

    if current_user.role == "admin":
        if owner_id is not None:
            statement = statement.where(MediaFile.user_id == owner_id)
            count_statement = count_statement.where(MediaFile.user_id == owner_id)
    else:
        statement = statement.where(MediaFile.user_id == current_user.id)
        count_statement = count_statement.where(MediaFile.user_id == current_user.id)

    total = session.scalar(count_statement) or 0
    items = list(
        session.scalars(
            statement.order_by(MediaFile.created_at.desc()).limit(limit).offset(offset)
        )
    )
    return items, total


def get_visible_media(session: Session, media_id: UUID, current_user: User) -> MediaFile:
    media = session.scalar(
        select(MediaFile).where(MediaFile.id == media_id, MediaFile.deleted_at.is_(None))
    )
    if media is None or (current_user.role != "admin" and media.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return media


def soft_delete_media(session: Session, media_id: UUID, current_user: User) -> None:
    media = get_visible_media(session, media_id, current_user)
    media.deleted_at = utc_now()
    session.commit()


def _sanitize_required_filename(filename: str | None) -> str:
    sanitized = sanitize_upload_filename(filename or "")
    if sanitized == "file" or not Path(sanitized).suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload filename is invalid",
        )
    return sanitized


def _media_type_for_extension(extension: str) -> str:
    if extension in IMAGE_MIME_BY_EXTENSION:
        return "image"
    if extension in VIDEO_MIME_BY_EXTENSION:
        return "video"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type",
    )


def _validate_content_type(extension: str, content_type: str | None) -> str:
    if extension in IMAGE_MIME_BY_EXTENSION:
        expected = IMAGE_MIME_BY_EXTENSION[extension]
        if content_type != expected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MIME type",
            )
        return expected

    expected_set = VIDEO_MIME_BY_EXTENSION[extension]
    if content_type not in expected_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MIME type",
        )
    return content_type or next(iter(expected_set))


def _max_bytes(media_type: str, max_image_size_mb: int, max_video_size_mb: int) -> int:
    mb = max_image_size_mb if media_type == "image" else max_video_size_mb
    return mb * 1024 * 1024


def _stored_path(user_id: UUID, media_id: UUID, extension: str) -> str:
    return validate_relative_storage_path(f"uploads/{user_id}/{media_id}/original{extension}")


def _write_limited_temp(upload: UploadFile, max_bytes: int, directory: Path) -> Path:
    total = 0
    with NamedTemporaryFile(
        prefix="upload-",
        suffix=".tmp",
        dir=directory,
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)
        while chunk := upload.file.read(CHUNK_SIZE):
            total += len(chunk)
            if total > max_bytes:
                _cleanup_path(temp_path)
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="Uploaded file is too large",
                )
            temp_file.write(chunk)

    if total == 0:
        _cleanup_path(temp_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )
    return temp_path


def _extract_metadata(path: Path, media_type: str, extension: str) -> MediaMetadata:
    if media_type == "image":
        return _extract_image_metadata(path, extension)
    return _extract_video_metadata(path, extension)


def _extract_image_metadata(path: Path, extension: str) -> MediaMetadata:
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        if extension != ".png":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image metadata support is not available",
            ) from exc
        width, height = _extract_png_size(path)
    else:
        try:
            with Image.open(path) as image:
                _validate_image_format(image.format, extension)
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
        except (SyntaxError, UnidentifiedImageError, OSError) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image content",
            ) from exc
    return MediaMetadata(
        width=width,
        height=height,
        frame_count=1,
        fps=None,
        duration_seconds=None,
    )


def _validate_image_format(decoded_format: str | None, extension: str) -> None:
    expected = {
        ".jpg": {"JPEG"},
        ".jpeg": {"JPEG"},
        ".png": {"PNG"},
        ".webp": {"WEBP"},
    }[extension]
    if decoded_format not in expected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image content does not match extension",
        )


def _extract_png_size(path: Path) -> tuple[int, int]:
    try:
        with path.open("rb") as image_file:
            header = image_file.read(24)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image content",
        ) from exc
    if not header.startswith(b"\x89PNG\r\n\x1a\n") or header[12:16] != b"IHDR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image content",
        )
    return struct.unpack(">II", header[16:24])


def _extract_video_metadata(path: Path, extension: str) -> MediaMetadata:
    _validate_video_container(path, extension)

    try:
        import cv2
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video metadata support is not available",
        ) from exc

    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid video content",
            )
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) or None
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) or None
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)) or None
        fps = float(capture.get(cv2.CAP_PROP_FPS)) or None
        duration = frame_count / fps if frame_count and fps else None
    finally:
        capture.release()

    return MediaMetadata(
        width=width,
        height=height,
        frame_count=frame_count,
        fps=fps,
        duration_seconds=duration,
    )


def _validate_video_container(path: Path, extension: str) -> None:
    try:
        with path.open("rb") as video_file:
            header = video_file.read(64)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video content",
        ) from exc

    if extension == ".avi":
        is_expected = len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"AVI "
    elif extension == ".mkv":
        is_expected = header.startswith(b"\x1a\x45\xdf\xa3")
    elif extension in {".mp4", ".mov"}:
        is_expected = _is_expected_iso_video_container(header, extension)
    else:
        is_expected = False

    if not is_expected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video content does not match extension",
        )


def _is_expected_iso_video_container(header: bytes, extension: str) -> bool:
    if len(header) < 12 or header[4:8] != b"ftyp":
        return False

    major_brand = header[8:12]
    compatible_brands = header[16:64]
    has_quicktime_brand = major_brand == b"qt  " or b"qt  " in compatible_brands
    if extension == ".mov":
        return has_quicktime_brand
    return not has_quicktime_brand


def _cleanup_path(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass
