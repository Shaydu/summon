import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)
API_KEY = "super-secret-test-key22"

def test_give_success():
    payload = {"player": "WiryHealer4014", "item": "diamond_sword", "amount": 1}
    response = client.post("/give", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "give WiryHealer4014 diamond_sword 1" in data["executed"]

def test_give_missing_player():
    payload = {"item": "diamond_sword", "amount": 1}
    response = client.post("/give", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "player" in data["error"]

def test_give_missing_item():
    payload = {"player": "WiryHealer4014", "amount": 1}
    response = client.post("/give", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "item" in data["error"]

def test_give_invalid_amount():
    payload = {"player": "WiryHealer4014", "item": "diamond_sword", "amount": 0}
    response = client.post("/give", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "amount" in data["error"]

def test_give_invalid_api_key():
    payload = {"player": "WiryHealer4014", "item": "diamond_sword", "amount": 1}
    response = client.post("/give", json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
