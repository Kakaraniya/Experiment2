from fastapi.testclient import TestClient

from src import app as app_module
from src.data import build_sample_dataset
from src.model import train_and_evaluate


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

        prediction_response = client.post(
            "/predict",
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
