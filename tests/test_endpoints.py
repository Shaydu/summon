import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

def test_nfc_event():
    payload = {"token_id": "123", "player": "WiryHealer4014", "action": "give_diamond_sword"}
    response = client.post("/nfc-event", json=payload, headers=headers)
    assert response.status_code in (200, 400)

def test_players():
    response = client.get("/players", headers=headers)
    assert response.status_code == 200
    assert "players" in response.json()
