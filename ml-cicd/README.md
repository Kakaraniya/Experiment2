# ml-cicd

Battery thermal sensor ML project for Experiment 5.

## What it does

- Trains a regression model from battery sensor features: temperature, voltage, current, and coolant flow rate.
- Saves a versioned model artifact under `models/`.
- Serves predictions through a FastAPI API.
- Validates model performance before deployment.
- Runs linting, tests, validation, Docker build, and image push in GitHub Actions.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Generate data and train

```bash
python scripts/generate_sample_data.py
python -m src.train --data-path data/battery_thermal_sensor.csv --model-dir models --threshold 1.5
```

## Run validation

```bash
python -m src.validate_model --data-path data/battery_thermal_sensor.csv --model-dir models --threshold 1.5
```

## Run tests

```bash
pytest -q
```

## Run the API

```bash
uvicorn src.app:app --reload
```

## Docker

```bash
docker build -t battery-thermal-ml .
docker run -p 8000:8000 battery-thermal-ml
```

The Docker image uses `requirements-docker.txt` so it only installs runtime dependencies.

## Versioning and rollback

- Each trained model is written as a versioned file such as `models/battery_thermal_model_vYYYYMMDDHHMMSS.joblib`.
- The active version is recorded in `models/latest.json`.
- Use `scripts/rollback_model.py` to restore the previous registry entry if a deployment fails.

## GitHub Actions

The workflow in `.github/workflows/ci-cd.yml` runs on pushes and pull requests. It:

- Checks out the code
- Installs dependencies
- Generates the sample dataset
- Runs `ruff`
- Trains the model
- Runs tests
- Validates model performance
- Builds the Docker image
- Pushes the image to GHCR on pushes to `main`

## Secrets

If you deploy to a registry other than GHCR, add repository secrets for the registry username and token instead of hardcoding them in source control.
