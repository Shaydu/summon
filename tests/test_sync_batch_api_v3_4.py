import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

def test_sync_batch_valid():
    batch_payload = {
        "summons": [
            {
                "token_id": "abc123",
                "player_id": "ActorPlayer",
                "summon_type": "piglin",
                "summon_time": "2025-12-22T15:00:00Z",
                "location": {"x": 100.5, "y": 64.0, "z": -200.0},
                "metadata": {"custom_name": "Bob", "level": 5}
            },
            {
                "token_id": "def456",
                "player_id": "ActorPlayer2",
                "summon_type": "zombie",
                "summon_time": "2025-12-22T16:00:00Z",
                "location": {"x": 101.5, "y": 65.0, "z": -201.0},
                "metadata": {"custom_name": "Alice", "level": 10}
            }
        ]
    }
    response = client.post("/api/summon/sync/batch", json=batch_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "operation_id" in response.json()

def test_sync_batch_invalid():
    batch_payload = {
        "summons": [
            {
                "token_id": "abc123",
                # missing player_id
                "summon_type": "piglin",
                "summon_time": "2025-12-22T15:00:00Z",
                "location": {"x": 100.5, "y": 64.0, "z": -200.0},
                "metadata": {"custom_name": "Bob", "level": 5}
            },
            {
                "token_id": "def456",
                "player_id": "ActorPlayer2",
                "summon_type": "zombie",
                "summon_time": "2025-12-22T16:00:00Z",
                "location": {"x": 101.5, "y": 65.0, "z": -201.0},
                # metadata missing
            }
        ]
    }
    response = client.post("/api/summon/sync/batch", json=batch_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "errors" in data
    assert any(e["field"] == "player_id" for e in data["errors"])
    assert any(e["field"] == "metadata" for e in data["errors"])
