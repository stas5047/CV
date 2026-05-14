from __future__ import annotations

import argparse
import csv
import random
import shutil
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MANIFEST_COLUMNS = ["image_path", "label_path", "source_group_id", "split"]
GROUP_COLUMNS = ("source_group_id", "group_id", "source_id", "sequence_id", "video_id", "source", "sequence", "video")


@dataclass(frozen=True)
class DatasetItem:
    image_path: Path
    label_path: Path
    source_group_id: str


def prepare_yolo_dataset(
    images_dir: Path,
    labels_dir: Path,
    output_dir: Path,
    *,
    metadata_csv: Path | None = None,
    group_column: str | None = None,
    seed: int = 42,
) -> Path:
    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)
    output_dir = Path(output_dir)
    items = _load_items(images_dir, labels_dir, metadata_csv, group_column)
    assignments = _assign_splits(items, seed)

    _ensure_empty_output_dir(output_dir)
    _ensure_unique_output_targets(assignments)
    _create_output_dirs(output_dir)
    manifest_rows: list[dict[str, str]] = []
    for item, split in assignments:
        image_target = output_dir / "images" / split / item.image_path.name
        label_target = output_dir / "labels" / split / item.label_path.name
        shutil.copy2(item.image_path, image_target)
        shutil.copy2(item.label_path, label_target)
        manifest_rows.append(
            {
                "image_path": image_target.relative_to(output_dir).as_posix(),
                "label_path": label_target.relative_to(output_dir).as_posix(),
                "source_group_id": item.source_group_id,
                "split": split,
            }
        )

    _write_manifest(output_dir / "split_manifest.csv", manifest_rows)
    _write_data_yaml(output_dir / "data.yaml")
    return output_dir


def _load_items(
    images_dir: Path,
    labels_dir: Path,
    metadata_csv: Path | None,
    group_column: str | None,
) -> list[DatasetItem]:
    if metadata_csv is None:
        return _discover_items(images_dir, labels_dir)

    with Path(metadata_csv).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        if not reader.fieldnames:
            raise ValueError("metadata CSV must include headers")
        selected_group_column = group_column or next((column for column in GROUP_COLUMNS if column in reader.fieldnames), None)

    items: list[DatasetItem] = []
    for row in rows:
        image_value = row.get("image_path") or row.get("image") or row.get("filename")
        if not image_value:
            raise ValueError("metadata row missing image_path")
        label_value = row.get("label_path") or f"{Path(image_value).stem}.txt"
        image_path = _resolve_input_path(images_dir, image_value)
        label_path = _resolve_input_path(labels_dir, label_value)
        if not image_path.is_file():
            raise FileNotFoundError(f"image not found: {image_path}")
        if not label_path.is_file():
            raise FileNotFoundError(f"label not found: {label_path}")
        source_group_id = row.get(selected_group_column, "") if selected_group_column else ""
        items.append(DatasetItem(image_path=image_path, label_path=label_path, source_group_id=source_group_id or ""))
    return items


def _discover_items(images_dir: Path, labels_dir: Path) -> list[DatasetItem]:
    items: list[DatasetItem] = []
    for image_path in sorted(images_dir.rglob("*")):
        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        label_path = labels_dir / f"{image_path.stem}.txt"
        if not label_path.is_file():
            raise FileNotFoundError(f"label not found for image {image_path.name}: {label_path}")
        items.append(DatasetItem(image_path=image_path, label_path=label_path, source_group_id=""))
    if not items:
        raise ValueError("no supported images found")
    return items


def _resolve_input_path(base_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() and path.is_file():
        return path
    candidate = base_dir / path
    if candidate.is_file():
        return candidate
    return base_dir / path.name


def _assign_splits(items: list[DatasetItem], seed: int) -> list[tuple[DatasetItem, str]]:
    if any(item.source_group_id for item in items):
        units: list[list[DatasetItem]] = []
        by_group: dict[str, list[DatasetItem]] = {}
        for item in items:
            by_group.setdefault(item.source_group_id or item.image_path.stem, []).append(item)
        units = [sorted(group_items, key=lambda item: item.image_path.name) for group_items in by_group.values()]
    else:
        units = [[item] for item in items]

    random.Random(seed).shuffle(units)
    split_by_unit = _split_units(len(units))

    assigned: list[tuple[DatasetItem, str]] = []
    for unit, split in zip(units, split_by_unit, strict=True):
        for item in unit:
            assigned.append((item, split))
    return sorted(assigned, key=lambda pair: pair[0].image_path.name)


def _split_units(count: int) -> list[str]:
    if count <= 0:
        raise ValueError("dataset is empty")
    if count == 1:
        return ["train"]
    if count == 2:
        return ["train", "val"]

    train_count = max(1, round(count * 0.8))
    val_count = max(1, round(count * 0.1))
    test_count = count - train_count - val_count
    if test_count <= 0:
        test_count = 1
        train_count = max(1, train_count - 1)
    while train_count + val_count + test_count > count:
        train_count -= 1
    return ["train"] * train_count + ["val"] * val_count + ["test"] * test_count


def _create_output_dirs(output_dir: Path) -> None:
    for split in ("train", "val", "test"):
        (output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
        (output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def _ensure_empty_output_dir(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"output directory must be empty before dataset preparation: {output_dir}")


def _ensure_unique_output_targets(assignments: list[tuple[DatasetItem, str]]) -> None:
    seen_names: set[tuple[str, str]] = set()
    for item, split in assignments:
        for kind, name in (("images", item.image_path.name), ("labels", item.label_path.name)):
            target = (kind, name)
            if target in seen_names:
                raise ValueError(f"duplicate output target would overwrite {kind}/{split}/{name}")
            seen_names.add(target)


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _write_data_yaml(path: Path) -> None:
    path.write_text(
        "path: .\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "nc: 1\n"
        "names:\n"
        "  0: drone\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare deterministic one-class YOLO dataset split.")
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("storage/datasets/seraphim_subset"))
    parser.add_argument("--metadata-csv", type=Path)
    parser.add_argument("--group-column")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output = prepare_yolo_dataset(
        args.images_dir,
        args.labels_dir,
        args.output_dir,
        metadata_csv=args.metadata_csv,
        group_column=args.group_column,
        seed=args.seed,
    )
    print(f"Prepared YOLO dataset at {output}")


if __name__ == "__main__":
    main()
