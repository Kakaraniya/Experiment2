from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .config import DEFAULT_DATA_PATH, DEFAULT_MODEL_DIR, DEFAULT_PERFORMANCE_THRESHOLD
from .data import load_dataset, split_features_target
from .model import load_model, predict, resolve_latest_model_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the trained model for deployment.")
    parser.add_argument("--data-path", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    parser.add_argument("--threshold", type=float, default=DEFAULT_PERFORMANCE_THRESHOLD)
    return parser.parse_args()


def resolve_model_path(model_path: str, model_dir: str) -> Path:
    if model_path:
        return Path(model_path)
    model_path_resolved, _registry = resolve_latest_model_artifact(model_dir)
    return model_path_resolved


def main() -> None:
    args = parse_args()
    dataset = load_dataset(args.data_path)
    features, target = split_features_target(dataset)
    model_path = resolve_model_path(args.model_path, args.model_dir)
    model = load_model(model_path)
    predictions = predict(model, features)

    if len(predictions) != len(target):
        raise SystemExit("Validation failed: prediction count does not match input rows")
    if not np.isfinite(predictions).all():
        raise SystemExit("Validation failed: predictions contain invalid values")

    rmse = float(np.sqrt(np.mean((predictions - target.to_numpy()) ** 2)))
    if rmse > args.threshold:
        raise SystemExit(f"Validation failed: rmse {rmse:.4f} exceeds threshold {args.threshold:.4f}")

    print({"status": "passed", "rmse": rmse, "model_path": str(model_path)})


if __name__ == "__main__":
    main()
