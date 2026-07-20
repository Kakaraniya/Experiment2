import argparse
import joblib
import os
import pandas as pd

MODEL_PATH = "crop-water/models/model.joblib"


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found. Run training first: python3 crop-water/train.py")
    return joblib.load(MODEL_PATH)


def main():
    p = argparse.ArgumentParser(description="Predict sugarcane water requirement (mm/week)")
    p.add_argument("--temp", type=float, required=True)
    p.add_argument("--hum", type=float, required=True)
    p.add_argument("--rain", type=float, required=True)
    p.add_argument("--soil", type=float, required=True)
    p.add_argument("--solar", type=float, required=True)
    p.add_argument("--stage", type=int, choices=[0,1,2], default=1)
    args = p.parse_args()

    model = load_model()
    df = pd.DataFrame([{
        "temperature": args.temp,
        "humidity": args.hum,
        "rainfall": args.rain,
        "soil_moisture": args.soil,
        "solar_rad": args.solar,
        "crop_stage": args.stage,
    }])
    pred = model.predict(df)[0]
    print(f"Predicted water requirement for sugarcane: {pred:.2f} mm/week")


if __name__ == "__main__":
    main()
