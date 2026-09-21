# ml-cicd

Battery thermal sensor ML project for Experiment 5.

## What it does

- Trains a regression model from battery sensor features: temperature, voltage, current, and coolant flow rate.
- Saves a versioned model artifact under `models/`.
- Serves predictions through a FastAPI API.
- Classifies predictions as abnormal when the predicted temperature reaches the configured threshold.
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

Open `http://localhost:8000/dashboard` for the Thermal Watch dashboard. It shows live model status, recent forecast trends, abnormal readings, and an interactive prediction form.

## Docker

```bash
docker build -t battery-thermal-ml .
docker run -p 8000:8000 battery-thermal-ml
```

The Docker image uses `requirements-docker.txt` so it only installs runtime dependencies.

## Kubernetes deployment

For Minikube, build directly into its image store so the cluster can use the local image:

```bash
minikube image build -t battery-thermal-ml:local .
minikube addons enable metrics-server
kubectl apply -f k8s/battery-thermal.yaml
kubectl rollout status deployment/battery-thermal-ml
minikube service battery-thermal-ml --url
```

Build the image after training so the versioned model artifact and `latest.json` are included. For a remote registry, replace `battery-thermal-ml:local` in `k8s/battery-thermal.yaml` with the pushed image reference and keep `imagePullPolicy: IfNotPresent`:

```bash
python -m src.train --data-path data/battery_thermal_sensor.csv --model-dir models --threshold 1.5
docker build -t ghcr.io/YOUR_GITHUB_ORG/battery-thermal-ml:latest .
docker push ghcr.io/YOUR_GITHUB_ORG/battery-thermal-ml:latest
kubectl port-forward service/battery-thermal-ml 8000:80
```

The manifest starts two replicas and scales them from 2 to 10 based on CPU utilization. It uses `/health` for liveness and `/ready` to keep pods out of service until the model is loaded. The `/predict` response includes `abnormal`; set `ABNORMAL_TEMPERATURE_THRESHOLD_C` to change the threshold.

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

## Experiment 7 — Security testing of the battery thermal ML application

This project is also configured for the security-testing experiment from the provided Windows lab manual. The workflow covers dependency analysis, source-code scanning, secret detection, Docker/Trivy scanning, and JWT-protected ML API access.

### Security tools used

1. **pip-audit** — scans Python dependencies for known vulnerabilities/CVEs.
2. **Bandit** — scans `src/` for common insecure Python coding patterns.
3. **Gitleaks** — detects exposed secrets in the project and Git history.
4. **Docker + Trivy** — builds the ML container and scans it for vulnerabilities, secrets, and misconfigurations.
5. **FastAPI + JWT + Argon2** — protects `/predict` and `/api/dashboard` with authentication and token expiration.

### Security test commands

```powershell
pip install -r requirements.txt
pip install pip-audit bandit
.\security\run_security_tests.ps1
```

The scan reports are stored in `reports/` as JSON/HTML files. For the safe Gitleaks classroom test, run `security\create_demo_secret.ps1`, scan the fake secret, and then remove `security\demo-secret.txt` immediately.

### Secure API test

Set a local signing key before starting the API:

```powershell
$env:JWT_SECRET_KEY="replace-with-a-random-value-at-least-32-characters"
uvicorn src.app:app --reload
```

Expected access-control results:

| Test | Endpoint | Expected |
|---|---|---|
| No token | `POST /predict` | HTTP 401 |
| Valid username/password | `POST /token` | HTTP 200 + JWT |
| Valid token | `POST /predict` | HTTP 200 + thermal prediction |
| Invalid token | `POST /predict` | HTTP 401 |
| Expired token | `POST /predict` | HTTP 401 |

This follows the security-test matrix in the supplied lab manual, while replacing its generic Iris/Heatwave example with the existing battery-temperature prediction application.
