from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from .config import DEFAULT_MODEL_NAME, FEATURE_COLUMNS, RANDOM_STATE
from .data import split_features_target


def build_model(random_state: int = RANDOM_STATE) -> RandomForestRegressor:
    return RandomForestRegressor(
        n_estimators=400,
        max_depth=16,
        min_samples_split=2,
        random_state=random_state,
    )


def train_and_evaluate(frame: pd.DataFrame) -> dict[str, object]:
    features, target = split_features_target(frame)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    model = build_model()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    mse = mean_squared_error(y_test, predictions)

    metrics = {
        "rmse": float(np.sqrt(mse)),
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }

    return {
        "model": model,
        "metrics": metrics,
        "x_test": x_test,
        "y_test": y_test,
        "predictions": predictions,
    }


def build_versioned_model_path(model_dir: str | Path, model_name: str = DEFAULT_MODEL_NAME) -> tuple[Path, str]:
    model_directory = Path(model_dir)
    model_directory.mkdir(parents=True, exist_ok=True)
    version = datetime.now(timezone.utc).strftime("v%Y%m%d%H%M%S")
    return model_directory / f"{model_name}_{version}.joblib", version


def save_model(
    model: RandomForestRegressor,
    model_dir: str | Path,
    model_name: str = DEFAULT_MODEL_NAME,
    metrics: dict[str, float] | None = None,
) -> dict[str, str]:
    model_path, version = build_versioned_model_path(model_dir, model_name=model_name)
    joblib.dump(model, model_path)

    registry_entry = {
        "version": version,
        "model_path": str(model_path),
        "model_name": model_name,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if metrics is not None:
        registry_entry["metrics"] = metrics

    registry_path = Path(model_dir) / "latest.json"
    registry_path.write_text(json.dumps(registry_entry, indent=2), encoding="utf-8")

    history_path = Path(model_dir) / "model_history.json"
    history: list[dict[str, str]] = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    history.append(registry_entry)
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return registry_entry


def load_model(model_path: str | Path):
    normalized_path = Path(str(model_path).replace("\\", "/"))
    return joblib.load(normalized_path)


def resolve_latest_model_artifact(model_dir: str | Path) -> tuple[Path, dict[str, str]]:
    model_directory = Path(model_dir)
    registry_path = model_directory / "latest.json"
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry_model_path = Path(str(registry["model_path"]).replace("\\", "/"))
        if not registry_model_path.is_absolute():
            registry_model_path = (model_directory.parent / registry_model_path).resolve()
        return registry_model_path, registry

    model_files = sorted(model_directory.glob("*.joblib"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not model_files:
        raise FileNotFoundError(
            f"No trained model found in {model_directory}. Run the training script first."
        )

    model_path = model_files[0]
    registry = {
        "version": model_path.stem,
        "model_path": model_path.relative_to(model_directory.parent).as_posix(),
        "model_name": model_path.stem,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return model_path, registry


def load_latest_model(model_dir: str | Path) -> tuple[object, dict[str, str]]:
    model_path, registry = resolve_latest_model_artifact(model_dir)
    return load_model(model_path), registry


def predict(model, feature_frame: pd.DataFrame) -> np.ndarray:
    ordered_features = feature_frame[FEATURE_COLUMNS]
    return np.asarray(model.predict(ordered_features), dtype=float)
