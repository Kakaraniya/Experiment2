from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import DEFAULT_MODEL_DIR
from .model import load_latest_model
from .predict import SensorReading, predict_single

app = FastAPI(title="Battery Thermal ML API", version="1.0.0")
model = None
model_registry = None


class PredictionRequest(BaseModel):
    temperature_c: float = Field(..., ge=-40, le=150)
    voltage_v: float = Field(..., ge=0.0, le=10.0)
    current_a: float = Field(..., ge=0.0, le=100.0)
    coolant_flow_lpm: float = Field(..., ge=0.0, le=50.0)


class PredictionResponse(BaseModel):
    predicted_temperature_c: float
    model_version: str


@app.on_event("startup")
def load_app_model() -> None:
    global model, model_registry
    model, model_registry = load_latest_model(DEFAULT_MODEL_DIR)


@app.get("/health")
def health_check() -> dict[str, str]:
    if model is None or model_registry is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ok", "model_version": model_registry["version"]}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    if model is None or model_registry is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    reading = SensorReading(**payload.model_dump())
    predicted_temperature = predict_single(model, reading)
    return PredictionResponse(
        predicted_temperature_c=predicted_temperature,
        model_version=model_registry["version"],
    )
