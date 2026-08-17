from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS, RANDOM_STATE, TARGET_COLUMN


def build_sample_dataset(rows: int = 500, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    temperature = rng.uniform(20.0, 65.0, rows)
    voltage = rng.uniform(3.2, 4.25, rows)
    current = rng.uniform(0.4, 7.5, rows)
    coolant_flow = rng.uniform(0.8, 6.5, rows)
    noise = rng.normal(0, 0.08, rows)

    target_temperature = (
        0.72 * temperature
        + 0.9 * current
        - 1.6 * coolant_flow
        - 2.2 * (voltage - 3.7)
        + 18.0
        + noise
    )

    frame = pd.DataFrame(
        {
            FEATURE_COLUMNS[0]: temperature,
            FEATURE_COLUMNS[1]: voltage,
            FEATURE_COLUMNS[2]: current,
            FEATURE_COLUMNS[3]: coolant_flow,
            TARGET_COLUMN: target_temperature,
        }
    )
    return frame.round(4)


def load_dataset(path: str | Path) -> pd.DataFrame:
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    return pd.read_csv(data_path)


def validate_dataset(frame: pd.DataFrame) -> None:
    missing = [column for column in [*FEATURE_COLUMNS, TARGET_COLUMN] if column not in frame.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")


def split_features_target(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    validate_dataset(frame)
    features = frame[FEATURE_COLUMNS].copy()
    target = frame[TARGET_COLUMN].copy()
    return features, target
