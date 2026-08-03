Crop Water Requirement Prediction (Sugarcane)

Overview
- This small project generates a synthetic sugarcane irrigation dataset, trains a regression model to predict weekly water requirement (mm/week), and provides a prediction script.

Quickstart
1. Create a Python environment (recommended: venv).
2. Install dependencies:

```bash
pip install -r crop-water/requirements.txt
```

3. Train model (generates data if missing):

```bash
python3 crop-water/train.py
```

4. Predict using sample CLI (values: temperature, humidity, rainfall, soil_moisture, solar_rad, crop_stage_index)

```bash
python3 crop-water/predict.py --temp 30 --hum 70 --rain 10 --soil 20 --solar 18 --stage 1
```

Files
- `crop-water/train.py`: trains and saves model to `crop-water/models/model.joblib`.
- `crop-water/predict.py`: loads model and predicts water requirement.
- `crop-water/requirements.txt`: packages.

Notes
- The dataset is synthetic and intended for demo/POC only. For production use, replace `data` with real measured irrigation records for sugarcane and retrain.

Docker
- Build the image:

```bash
docker build -t crop-water .
```

- Run the container:

```bash
docker run --rm crop-water
```
