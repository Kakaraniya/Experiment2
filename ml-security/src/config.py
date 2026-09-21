import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
MODEL_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DATA_PATH = DATA_DIR / "battery_thermal_sensor.csv"
DEFAULT_MODEL_DIR = MODEL_DIR
DEFAULT_MODEL_NAME = "battery_thermal_model"
FEATURE_COLUMNS = [
    "temperature_c",
    "voltage_v",
    "current_a",
    "coolant_flow_lpm",
]
TARGET_COLUMN = "target_temperature_c"
DEFAULT_PERFORMANCE_THRESHOLD = 1.5
DEFAULT_ABNORMAL_TEMPERATURE_THRESHOLD_C = 60.0
ABNORMAL_TEMPERATURE_THRESHOLD_C = float(
    os.getenv("ABNORMAL_TEMPERATURE_THRESHOLD_C", DEFAULT_ABNORMAL_TEMPERATURE_THRESHOLD_C)
)
RANDOM_STATE = 42
