import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

DATA_PATH = "crop-water/data/sugarcane_dataset.csv"
MODEL_DIR = "crop-water/models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")


def generate_synthetic_dataset(n_samples=2000, seed=42):
    rng = np.random.RandomState(seed)
    # Features ranges
    temperature = rng.uniform(20, 38, n_samples)  # degC
    humidity = rng.uniform(40, 90, n_samples)  # %
    rainfall = rng.uniform(0, 80, n_samples)  # mm/week
    soil_moisture = rng.uniform(5, 45, n_samples)  # % volumetric
    solar_rad = rng.uniform(8, 25, n_samples)  # MJ/m2/day average
    # crop stage: 0 - early, 1 - mid, 2 - late
    crop_stage = rng.choice([0, 1, 2], size=n_samples, p=[0.3, 0.5, 0.2])

    # Simple agronomic-inspired rule to compute water requirement (mm/week)
    # baseline influenced by temperature and solar radiation
    baseline = 0.9 * temperature + 1.5 * solar_rad
    # reduce by rainfall and soil moisture
    reduction = 0.6 * rainfall + 0.8 * soil_moisture
    # stage multiplier: mid-season needs more water
    stage_mult = 1.0 + crop_stage * 0.15
    # combine and clip to realistic bounds (20-80 mm/week for sugarcane in many conditions)
    water_req = (baseline * stage_mult - reduction) / 2.0
    noise = rng.normal(0, 5.0, n_samples)
    water_req = water_req + noise
    water_req = np.clip(water_req, 10, 90)

    df = pd.DataFrame({
        "temperature": np.round(temperature, 2),
        "humidity": np.round(humidity, 2),
        "rainfall": np.round(rainfall, 2),
        "soil_moisture": np.round(soil_moisture, 2),
        "solar_rad": np.round(solar_rad, 2),
        "crop_stage": crop_stage,
        "water_mm_per_week": np.round(water_req, 2),
    })
    return df


def ensure_data():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        print("Generating synthetic sugarcane dataset...")
        df = generate_synthetic_dataset()
        df.to_csv(DATA_PATH, index=False)
        print(f"Saved dataset to {DATA_PATH}")
    else:
        print(f"Dataset found at {DATA_PATH}")


def train_and_save():
    ensure_data()
    df = pd.read_csv(DATA_PATH)
    X = df[["temperature", "humidity", "rainfall", "soil_moisture", "solar_rad", "crop_stage"]]
    y = df["water_mm_per_week"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # define a set of candidate regressors to compare
    models = {
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42),
        "ExtraTrees": ExtraTreesRegressor(n_estimators=200, random_state=42),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=200, random_state=42),
        "HistGradientBoosting": HistGradientBoostingRegressor(random_state=42),
        "Ridge": Ridge(),
        "SVR": SVR(),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)

    results = []
    trained_pipelines = {}

    print("Training and evaluating models...")
    for name, estimator in models.items():
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", estimator),
        ])
        print(f"- Training {name}...")
        pipeline.fit(X_train, y_train)

        preds = pipeline.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results.append({"model": name, "mae": mae, "r2": r2})
        trained_pipelines[name] = pipeline

        # save individual model artifact
        file_path = os.path.join(MODEL_DIR, f"model_{name}.joblib")
        joblib.dump(pipeline, file_path)

    res_df = pd.DataFrame(results).sort_values("mae")
    print("\nModel comparison (sorted by MAE):")
    print(res_df.to_string(index=False, formatters={"mae": "{:.3f}".format, "r2": "{:.3f}".format}))

    # pick best by MAE
    best_row = res_df.iloc[0]
    best_name = best_row["model"]
    best_pipeline = trained_pipelines[best_name]

    # save best model to the canonical path
    joblib.dump(best_pipeline, MODEL_PATH)
    print(f"\nBest model: {best_name} (MAE={best_row['mae']:.3f}, R2={best_row['r2']:.3f})")
    print(f"Best model saved to {MODEL_PATH}")

    # sample prediction using best model
    sample = pd.DataFrame([{
        "temperature": 30.0,
        "humidity": 70.0,
        "rainfall": 10.0,
        "soil_moisture": 20.0,
        "solar_rad": 18.0,
        "crop_stage": 1
    }])
    pred_sample = best_pipeline.predict(sample)[0]
    print(f"Sample sugarcane water requirement (mm/week) by {best_name}: {pred_sample:.2f}")


if __name__ == "__main__":
    train_and_save()
