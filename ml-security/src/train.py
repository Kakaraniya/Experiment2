from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODEL_DIR,
    DEFAULT_MODEL_NAME,
    DEFAULT_PERFORMANCE_THRESHOLD,
)
from .data import load_dataset
from .model import save_model, train_and_evaluate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the battery thermal regression model.")
    parser.add_argument("--data-path", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--model-dir", default=str(DEFAULT_MODEL_DIR))
    parser.add_argument("--threshold", type=float, default=DEFAULT_PERFORMANCE_THRESHOLD)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_dataset(args.data_path)
    results = train_and_evaluate(frame)
    metrics = results["metrics"]

    if metrics["rmse"] > args.threshold:
        raise SystemExit(
            f"Model rejected: rmse {metrics['rmse']:.4f} exceeds threshold {args.threshold:.4f}"
        )

    registry = save_model(
        results["model"],
        args.model_dir,
        model_name=args.model_name,
        metrics=metrics,
    )

    output_path = Path(args.model_dir) / f"metrics_{registry['version']}.json"
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps({"registry": registry, "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
