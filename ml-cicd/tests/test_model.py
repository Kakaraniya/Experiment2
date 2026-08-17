from pathlib import Path

import numpy as np

from src.data import build_sample_dataset
from src.model import load_model, predict, save_model, train_and_evaluate


def test_model_is_created_successfully(tmp_path: Path) -> None:
    frame = build_sample_dataset(rows=240)
    results = train_and_evaluate(frame)

    assert results["model"] is not None
    assert results["metrics"]["rmse"] > 0

    registry = save_model(results["model"], tmp_path, metrics=results["metrics"])
    saved_model_path = Path(registry["model_path"])

    assert saved_model_path.exists()
    assert (tmp_path / "latest.json").exists()


def test_saved_model_can_be_loaded(tmp_path: Path) -> None:
    frame = build_sample_dataset(rows=240)
    results = train_and_evaluate(frame)
    registry = save_model(results["model"], tmp_path, metrics=results["metrics"])

    loaded_model = load_model(registry["model_path"])
    sample_features = frame.drop(columns=["target_temperature_c"]).head(5)

    predictions = predict(loaded_model, sample_features)

    assert len(predictions) == 5
    assert np.isfinite(predictions).all()


def test_model_produces_valid_predictions(tmp_path: Path) -> None:
    frame = build_sample_dataset(rows=240)
    results = train_and_evaluate(frame)
    registry = save_model(results["model"], tmp_path, metrics=results["metrics"])
    loaded_model = load_model(registry["model_path"])

    feature_frame = frame.drop(columns=["target_temperature_c"]).iloc[:10]
    predictions = predict(loaded_model, feature_frame)

    assert predictions.shape == (10,)
    assert np.isfinite(predictions).all()
    assert (predictions > 0).all()
