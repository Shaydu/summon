import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)
API_KEY = "super-secret-test-key22"

def test_say_success():
    payload = {"message": "Hello, world!"}
    response = client.post("/say", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "say Hello, world!" in data["executed"]

def test_say_missing_message():
    payload = {}
    response = client.post("/say", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data["error"]

def test_say_invalid_api_key():
    payload = {"message": "Hi"}
    response = client.post("/say", json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
