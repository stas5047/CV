from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from aerovision_training.artifact_import import (
    BackendRequestError,
    SendJson,
    ArtifactImportClient,
    load_json_artifact,
    send_json_request,
)
from aerovision_training.schemas import ArtifactValidationError


def main(argv: Sequence[str] | None = None, *, send_json: SendJson = send_json_request) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    token = args.api_token or os.getenv(args.token_env)
    if not token:
        raise SystemExit(f"INVALID: missing admin token in --api-token or {args.token_env}")

    client = ArtifactImportClient(args.backend_url, token, send_json=send_json)
    try:
        if args.command == "register-model":
            model_card = load_json_artifact(args.model_card)
            client.register_model(model_card, weights_path=args.weights_path, activate=args.activate)
        elif args.command == "import-experiments":
            metrics = load_json_artifact(args.metrics)
            client.import_experiments(
                metrics,
                artifacts_path=args.artifacts_path,
                dataset_name=args.dataset_name,
                model_version_id=args.model_version_id,
                is_published=args.published,
            )
        else:
            parser.error("missing command")
    except ArtifactValidationError as exc:
        raise SystemExit(f"INVALID: {exc}") from exc
    except BackendRequestError as exc:
        raise SystemExit(f"FAILED: {exc}") from exc


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Register offline AeroVision model and experiment artifacts through backend API.",
    )
    parser.add_argument("--backend-url", required=True, help="Backend base URL, for example http://localhost:8000")
    parser.add_argument("--api-token", default=None, help="Admin JWT token. Prefer environment variable.")
    parser.add_argument("--token-env", default="AEROVISION_API_TOKEN", help="Environment variable containing admin JWT token.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    register = subparsers.add_parser("register-model")
    register.add_argument("--model-card", type=Path, required=True)
    register.add_argument("--weights-path", required=True)
    register.add_argument("--activate", action="store_true")

    experiments = subparsers.add_parser("import-experiments")
    experiments.add_argument("--metrics", type=Path, required=True)
    experiments.add_argument("--artifacts-path", required=True)
    experiments.add_argument("--dataset-name", default=None)
    experiments.add_argument("--model-version-id", default=None)
    experiments.add_argument("--published", action="store_true")
    return parser


if __name__ == "__main__":
    main()
