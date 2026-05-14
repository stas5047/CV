from __future__ import annotations

import csv
from pathlib import Path

import pytest

from aerovision_training.dataset_split import prepare_yolo_dataset


def _write_sample(root: Path, stem: str, group: str | None = None) -> tuple[Path, Path]:
    image_dir = root / "images"
    label_dir = root / "labels"
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"{stem}.jpg"
    label_path = label_dir / f"{stem}.txt"
    image_path.write_bytes(b"fake-jpeg")
    label_path.write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
    return image_path, label_path


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_prepare_yolo_dataset_is_deterministic_and_writes_required_outputs(tmp_path: Path) -> None:
    source = tmp_path / "source"
    for index in range(10):
        _write_sample(source, f"drone_{index}")

    first = tmp_path / "out-a"
    second = tmp_path / "out-b"

    prepare_yolo_dataset(source / "images", source / "labels", first, seed=42)
    prepare_yolo_dataset(source / "images", source / "labels", second, seed=42)

    first_manifest = _read_manifest(first / "split_manifest.csv")
    second_manifest = _read_manifest(second / "split_manifest.csv")

    assert first_manifest == second_manifest
    assert set(first_manifest[0]) == {"image_path", "label_path", "source_group_id", "split"}
    assert {row["split"] for row in first_manifest} <= {"train", "val", "test"}
    assert all(row["source_group_id"] == "" for row in first_manifest)
    assert (first / "images" / "train").is_dir()
    assert (first / "labels" / "val").is_dir()
    assert (first / "data.yaml").read_text(encoding="utf-8").count("drone") == 1
    assert "nc: 1" in (first / "data.yaml").read_text(encoding="utf-8")


def test_prepare_yolo_dataset_uses_group_split_without_leakage(tmp_path: Path) -> None:
    source = tmp_path / "source"
    metadata = source / "metadata.csv"
    rows: list[tuple[str, str, str]] = []

    for group in ("video-a", "video-b", "video-c", "video-d"):
        for item in range(3):
            image_path, label_path = _write_sample(source, f"{group}_{item}")
            rows.append((image_path.name, label_path.name, group))

    metadata.parent.mkdir(parents=True, exist_ok=True)
    with metadata.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image_path", "label_path", "source_group_id"])
        writer.writerows(rows)

    output = tmp_path / "grouped"
    prepare_yolo_dataset(
        source / "images",
        source / "labels",
        output,
        metadata_csv=metadata,
        group_column="source_group_id",
        seed=42,
    )

    splits_by_group: dict[str, set[str]] = {}
    for row in _read_manifest(output / "split_manifest.csv"):
        splits_by_group.setdefault(row["source_group_id"], set()).add(row["split"])

    assert splits_by_group
    assert all(len(splits) == 1 for splits in splits_by_group.values())


def test_prepare_yolo_dataset_rejects_non_empty_output_dir(tmp_path: Path) -> None:
    source = tmp_path / "source"
    _write_sample(source, "drone")
    output = tmp_path / "out"
    stale_file = output / "images" / "train" / "stale.jpg"
    stale_file.parent.mkdir(parents=True)
    stale_file.write_bytes(b"old")

    with pytest.raises(ValueError, match="output directory must be empty"):
        prepare_yolo_dataset(source / "images", source / "labels", output)


def test_prepare_yolo_dataset_rejects_duplicate_output_targets(tmp_path: Path) -> None:
    source = tmp_path / "source"
    image_a = source / "images" / "camera-a"
    image_b = source / "images" / "camera-b"
    label_a = source / "labels" / "camera-a"
    label_b = source / "labels" / "camera-b"
    for directory in (image_a, image_b, label_a, label_b):
        directory.mkdir(parents=True, exist_ok=True)
    (image_a / "duplicate.jpg").write_bytes(b"a")
    (image_b / "duplicate.jpg").write_bytes(b"b")
    (label_a / "duplicate.txt").write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")
    (label_b / "duplicate.txt").write_text("0 0.4 0.4 0.2 0.2\n", encoding="utf-8")

    metadata = source / "metadata.csv"
    with metadata.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image_path", "label_path"])
        writer.writerow(["camera-a/duplicate.jpg", "camera-a/duplicate.txt"])
        writer.writerow(["camera-b/duplicate.jpg", "camera-b/duplicate.txt"])

    with pytest.raises(ValueError, match="duplicate output target"):
        prepare_yolo_dataset(source / "images", source / "labels", tmp_path / "out", metadata_csv=metadata, seed=42)
