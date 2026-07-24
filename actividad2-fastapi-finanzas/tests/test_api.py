from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from financial_api import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_predict_direction_missing_model(client):
    payload = {
        "symbol": "NONEXISTENT",
        "prediction_horizon": 1,
        "use_cached_data": True
    }
    response = client.post("/predict/direction", json=payload)
    assert response.status_code == 404


def test_predict_return_missing_model(client):
    payload = {
        "symbol": "NONEXISTENT",
        "prediction_horizon": 1,
        "use_cached_data": True
    }
    response = client.post("/predict/return", json=payload)
    assert response.status_code == 404


def test_predict_volatility_missing_model(client):
    payload = {
        "symbol": "NONEXISTENT",
        "prediction_horizon": 1,
        "use_cached_data": True
    }
    response = client.post("/predict/volatility", json=payload)
    assert response.status_code == 404


def test_model_info_invalid_type(client):
    response = client.get("/predict/model/AAPL/invalid_type")
    assert response.status_code == 400
