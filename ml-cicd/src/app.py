from __future__ import annotations

from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import ABNORMAL_TEMPERATURE_THRESHOLD_C, DEFAULT_DATA_PATH, DEFAULT_MODEL_DIR
from .data import load_dataset
from .model import load_latest_model
from .predict import SensorReading, predict_single

app = FastAPI(title="Battery Thermal ML API", version="1.0.0")
STATIC_DIR = Path(__file__).resolve().parent / "static"
model = None
model_registry = None


class PredictionRequest(BaseModel):
    temperature_c: float = Field(..., ge=-40, le=150)
    voltage_v: float = Field(..., ge=0.0, le=10.0)
    current_a: float = Field(..., ge=0.0, le=100.0)
    coolant_flow_lpm: float = Field(..., ge=0.0, le=50.0)


class PredictionResponse(BaseModel):
    predicted_temperature_c: float
    abnormal: bool
    abnormal_temperature_threshold_c: float
    model_version: str


@app.on_event("startup")
def load_app_model() -> None:
    global model, model_registry
    model, model_registry = load_latest_model(DEFAULT_MODEL_DIR)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/dashboard", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "dashboard.html")


@app.get("/ready")
def readiness_check() -> dict[str, str]:
    if model is None or model_registry is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ready", "model_version": model_registry["version"]}


@app.get("/api/dashboard")
def dashboard_data() -> dict[str, object]:
    if model is None or model_registry is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    frame = load_dataset(DEFAULT_DATA_PATH)
    recent = frame.tail(24).copy()
    recent_predictions = np.asarray(model.predict(recent[[
        "temperature_c",
        "voltage_v",
        "current_a",
        "coolant_flow_lpm",
    ]]), dtype=float)
    abnormal_count = int((recent_predictions >= ABNORMAL_TEMPERATURE_THRESHOLD_C).sum())
    return {
        "status": "operational",
        "model_version": model_registry["version"],
        "threshold_c": ABNORMAL_TEMPERATURE_THRESHOLD_C,
        "sample_count": int(len(frame)),
        "abnormal_count": abnormal_count,
        "mean_temperature_c": round(float(recent_predictions.mean()), 2),
        "peak_temperature_c": round(float(recent_predictions.max()), 2),
        "recent": [
            {
                "temperature_c": round(float(row.temperature_c), 2),
                "predicted_temperature_c": round(float(prediction), 2),
                "current_a": round(float(row.current_a), 2),
                "coolant_flow_lpm": round(float(row.coolant_flow_lpm), 2),
                "abnormal": bool(prediction >= ABNORMAL_TEMPERATURE_THRESHOLD_C),
            }
            for row, prediction in zip(recent.itertuples(index=False), recent_predictions)
        ],
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    if model is None or model_registry is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    reading = SensorReading(**payload.model_dump())
    predicted_temperature = predict_single(model, reading)
    return PredictionResponse(
        predicted_temperature_c=predicted_temperature,
        abnormal=predicted_temperature >= ABNORMAL_TEMPERATURE_THRESHOLD_C,
        abnormal_temperature_threshold_c=ABNORMAL_TEMPERATURE_THRESHOLD_C,
        model_version=model_registry["version"],
    )
