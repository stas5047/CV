from pathlib import Path

import pytest

from aerovision_worker.storage_paths import safe_join_storage_path, validate_relative_storage_path


def test_validate_relative_storage_path_normalizes_safe_paths() -> None:
    assert validate_relative_storage_path(r"uploads\user\media\original.mp4") == (
        "uploads/user/media/original.mp4"
    )


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/app/storage/uploads/file.jpg",
        r"C:\storage\uploads\file.jpg",
        r"\\server\share\file.jpg",
        "../uploads/file.jpg",
        "uploads/../file.jpg",
        "uploads/file.jpg\x00",
        "uploads//file.jpg",
    ],
)
def test_validate_relative_storage_path_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(ValueError):
        validate_relative_storage_path(path)


def test_safe_join_storage_path_keeps_result_under_root(tmp_path: Path) -> None:
    result = safe_join_storage_path(tmp_path, "uploads/user/file.jpg")

    assert result == tmp_path.resolve() / "uploads" / "user" / "file.jpg"


def test_safe_join_storage_path_rejects_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        safe_join_storage_path(tmp_path, "../outside/file.jpg")
