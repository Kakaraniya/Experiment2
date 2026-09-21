from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient
from src import app as app_module
from src.data import build_sample_dataset
from src.model import train_and_evaluate
from src.security import JWT_ALGORITHM, JWT_SECRET_KEY


def test_health_and_prediction_endpoints(monkeypatch) -> None:
    frame = build_sample_dataset(rows=240)
    results = train_and_evaluate(frame)

    monkeypatch.setattr(
        app_module,
        "load_latest_model",
        lambda _model_dir: (results["model"], {"version": "test-version"}),
    )

    with TestClient(app_module.app) as client:
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "ok"

        unauthenticated = client.post(
            "/predict",
            json={
                "temperature_c": 42.0,
                "voltage_v": 3.8,
                "current_a": 2.5,
                "coolant_flow_lpm": 3.0,
            },
        )
        assert unauthenticated.status_code == 401

        token_response = client.post(
            "/token",
            data={"username": "student", "password": "student123"},
        )
        assert token_response.status_code == 200
        token = token_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        prediction_response = client.post(
            "/predict",
            headers=headers,
            json={
                "temperature_c": 42.0,
                "voltage_v": 3.8,
                "current_a": 2.5,
                "coolant_flow_lpm": 3.0,
            },
        )

        assert prediction_response.status_code == 200
        payload = prediction_response.json()
        assert payload["model_version"] == "test-version"
        assert payload["predicted_temperature_c"] > 0
        assert isinstance(payload["abnormal"], bool)
        assert payload["abnormal_temperature_threshold_c"] == 60.0

        invalid_token = client.post(
            "/predict",
            headers={"Authorization": "Bearer invalid-token"},
            json={
                "temperature_c": 42.0,
                "voltage_v": 3.8,
                "current_a": 2.5,
                "coolant_flow_lpm": 3.0,
            },
        )
        assert invalid_token.status_code == 401

        expired_token = jwt.encode(
            {
                "sub": "student",
                "role": "student",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )
        expired_response = client.post(
            "/predict",
            headers={"Authorization": f"Bearer {expired_token}"},
            json={
                "temperature_c": 42.0,
                "voltage_v": 3.8,
                "current_a": 2.5,
                "coolant_flow_lpm": 3.0,
            },
        )
        assert expired_response.status_code == 401

        dashboard_response = client.get("/dashboard")
        assert dashboard_response.status_code == 200
        assert "Thermal Watch" in dashboard_response.text

        monkeypatch.setattr(
            app_module,
            "load_dataset",
            lambda _path: build_sample_dataset(rows=24),
        )
        summary_response = client.get("/api/dashboard")
        assert summary_response.status_code == 200
        assert summary_response.json()["sample_count"] == 24
