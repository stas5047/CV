from __future__ import annotations

import json
from pathlib import Path


def check_notebook_template(path: Path, required_weight: str) -> None:
    with Path(path).open("r", encoding="utf-8") as handle:
        notebook = json.load(handle)

    sources: list[str] = []
    for cell in notebook.get("cells", []):
        source = cell.get("source", "")
        sources.append("".join(source) if isinstance(source, list) else str(source))

    joined = "\n".join(sources)
    lower = joined.lower()
    if required_weight not in joined:
        raise AssertionError(f"notebook must start from pretrained {required_weight}")
    if "YOLO(" not in joined:
        raise AssertionError("notebook must use Ultralytics YOLO")
    if "imgsz=640" not in joined:
        raise AssertionError("notebook must use image size 640")
    if "seed=42" not in joined:
        raise AssertionError("notebook must use seed 42")
    if "scratch" in lower:
        raise AssertionError("notebook must not describe scratch training")
