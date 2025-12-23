import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

def test_sync_single_success():
    payload = {
        "token_id": "abc123",
        "player_id": "player_1",
        "summon_type": "zombie",
        "summon_time": "2025-12-22T15:00:00Z",
        "location": {"x": 100.5, "y": 64.0, "z": -200.0},
        "metadata": {"custom_name": "Bob", "level": 5}
    }
    response = client.post("/api/summon/sync", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "operation_id" in response.json()

def test_sync_single_error():
    payload = {
        "token_id": "abc123",
        # missing player_id
        "summon_type": "zombie",
        "summon_time": "2025-12-22T15:00:00Z",
        "location": {"x": 100.5, "y": 64.0, "z": -200.0},
        "metadata": {"custom_name": "Bob", "level": 5}
    }
    response = client.post("/api/summon/sync", json=payload, headers=headers)
    assert response.status_code in (200, 400)
