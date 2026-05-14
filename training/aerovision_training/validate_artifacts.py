from __future__ import annotations

import argparse
from pathlib import Path

from aerovision_training.schemas import (
    ArtifactValidationError,
    validate_json_file,
    validate_metrics_artifact,
    validate_model_card,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate offline model card and metrics artifacts.")
    parser.add_argument("--model-card", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    args = parser.parse_args()

    try:
        validate_model_card(validate_json_file(args.model_card))
        validate_metrics_artifact(validate_json_file(args.metrics))
    except ArtifactValidationError as exc:
        raise SystemExit(f"INVALID: {exc}") from exc

    print("VALID: model card and metrics artifacts match offline import-readiness contract")


if __name__ == "__main__":
    main()
