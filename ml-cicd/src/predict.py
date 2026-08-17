from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .model import predict as model_predict


@dataclass
class SensorReading:
    temperature_c: float
    voltage_v: float
    current_a: float
    coolant_flow_lpm: float


def predict_single(model, reading: SensorReading) -> float:
    frame = pd.DataFrame([asdict(reading)])
    return float(model_predict(model, frame)[0])
