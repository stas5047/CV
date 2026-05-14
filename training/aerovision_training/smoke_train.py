from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tiny local YOLO smoke training only.")
    parser.add_argument("--data-yaml", type=Path, default=Path("storage/datasets/seraphim_subset/data.yaml"))
    parser.add_argument("--model", default="yolo26n.pt")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--project", type=Path, default=Path("storage/temp/training-smoke"))
    args = parser.parse_args()

    if args.epochs > 3:
        raise SystemExit("Local smoke training is limited to 3 epochs and is not final evidence.")
    if not args.data_yaml.is_file():
        raise SystemExit(f"data.yaml not found: {args.data_yaml}")

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Install ultralytics in the training environment before smoke training.") from exc

    model = YOLO(args.model)
    model.train(
        data=str(args.data_yaml),
        epochs=args.epochs,
        imgsz=args.imgsz,
        seed=args.seed,
        task="detect",
        project=str(args.project),
        name="tiny-smoke",
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
