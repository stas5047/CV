from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._ -]+")


def validate_relative_storage_path(path: str) -> str:
    raw_path = str(path).strip()
    if not raw_path or "\x00" in raw_path:
        raise ValueError("Storage path must be a non-empty relative path")
    if "//" in raw_path or "\\\\" in raw_path:
        raise ValueError("Storage path must not contain empty or UNC path segments")

    posix_path = PurePosixPath(raw_path.replace("\\", "/"))
    windows_path = PureWindowsPath(raw_path)
    if posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive:
        raise ValueError("Storage path must be relative")
    if any(part in {"", ".", ".."} for part in posix_path.parts):
        raise ValueError("Storage path must not contain traversal segments")

    return posix_path.as_posix()


def safe_join_storage_path(storage_root: str | Path, relative_path: str) -> Path:
    validated_path = validate_relative_storage_path(relative_path)
    root = Path(storage_root).resolve()
    candidate = (root / validated_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Resolved storage path escapes storage root")
    return candidate


def sanitize_upload_filename(filename: str, *, fallback: str = "file") -> str:
    return _sanitize_filename(filename, fallback=fallback)


def safe_download_filename(filename: str, *, fallback: str = "download") -> str:
    return _sanitize_filename(filename, fallback=fallback)


def _sanitize_filename(filename: str, *, fallback: str) -> str:
    name = str(filename or "").replace("\\", "/").split("/")[-1].strip()
    name = SAFE_FILENAME_RE.sub("_", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if not name:
        return fallback

    stem, dot, suffix = name.partition(".")
    if stem.upper() in WINDOWS_RESERVED_NAMES:
        return f"{fallback}{dot}{suffix}" if suffix else fallback
    return name[:255]
