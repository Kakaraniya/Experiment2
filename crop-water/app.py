import os
from typing import Any, Dict, List

import joblib
import pandas as pd
from flask import Flask, jsonify, request


MODEL_PATH = "crop-water/models/model.joblib"
FEATURE_COLUMNS = [
    "temperature",
    "humidity",
    "rainfall",
    "soil_moisture",
    "solar_rad",
    "crop_stage",
]


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok", "model_exists": os.path.exists(MODEL_PATH)})

    @app.post("/predict")
    def predict() -> Any:
        if not os.path.exists(MODEL_PATH):
            return jsonify({"error": "Model not found. Run training first: python crop-water/train.py"}), 500

        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        try:
            rows = _normalize_payload(payload)
            frame = pd.DataFrame(rows, columns=FEATURE_COLUMNS)

            model = joblib.load(MODEL_PATH)
            predictions = model.predict(frame)
            values = [float(p) for p in predictions]
            return jsonify({"predictions": values})
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:
            return jsonify({"error": f"Prediction failed: {exc}"}), 500

    return app


def _normalize_payload(payload: Any) -> List[Dict[str, float]]:
    if isinstance(payload, dict) and "instances" in payload:
        instances = payload["instances"]
        if not isinstance(instances, list) or not instances:
            raise ValueError("'instances' must be a non-empty list of objects.")
        return [_parse_row(item) for item in instances]

    if isinstance(payload, dict):
        return [_parse_row(payload)]

    raise ValueError("JSON payload must be an object or contain an 'instances' list.")


def _parse_row(item: Any) -> Dict[str, float]:
    if not isinstance(item, dict):
        raise ValueError("Each instance must be a JSON object.")

    missing = [col for col in FEATURE_COLUMNS if col not in item]
    if missing:
        raise ValueError(f"Missing required feature(s): {', '.join(missing)}")

    row: Dict[str, float] = {}
    for col in FEATURE_COLUMNS:
        try:
            row[col] = float(item[col])
        except (TypeError, ValueError):
            raise ValueError(f"Feature '{col}' must be numeric.")

    return row


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)