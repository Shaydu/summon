import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)
API_KEY = "super-secret-test-key22"


def test_time_set_day_success(monkeypatch):
    # patch send_command_to_minecraft to avoid calling screen
    import services.time_service as ts

    monkeypatch.setattr("services.time_service.send_command_to_minecraft", lambda cmd: True)

    payload = {"time": "day"}
    resp = client.post("/time", json=payload, headers={"x-api-key": API_KEY})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "time set" in data["executed"]
    assert data.get("sent") is True


def test_time_set_ticks_success(monkeypatch):
    monkeypatch.setattr("services.time_service.send_command_to_minecraft", lambda cmd: True)
    payload = {"time": 6000}
    resp = client.post("/time", json=payload, headers={"x-api-key": API_KEY})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "time set 6000" in data["executed"]
    assert data.get("sent") is True


def test_time_missing_field():
    payload = {}
    resp = client.post("/time", json=payload, headers={"x-api-key": API_KEY})
    assert resp.status_code == 400
    data = resp.json()
    assert data["status"] == "error"


def test_time_invalid_api_key():
    payload = {"time": "day"}
    resp = client.post("/time", json=payload, headers={"x-api-key": "bad"})
    assert resp.status_code == 401
