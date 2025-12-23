import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)

API_KEY = "super-secret-test-key22"

# Unit test for /chat endpoint

def test_chat_success():
    payload = {"sender": "Steve", "message": "Hello world!"}
    response = client.post("/chat", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "<Steve> Hello world!" in data["executed"]

def test_chat_missing_sender():
    payload = {"message": "Hi"}
    response = client.post("/chat", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "sender" in data["error"]

def test_chat_missing_message():
    payload = {"sender": "Alex"}
    response = client.post("/chat", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "message" in data["error"]

def test_chat_invalid_api_key():
    payload = {"sender": "Alex", "message": "Hi"}
    response = client.post("/chat", json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401
