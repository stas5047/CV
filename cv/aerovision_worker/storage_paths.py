from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath


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
