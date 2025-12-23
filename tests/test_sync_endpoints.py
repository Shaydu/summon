
import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)

# Test /api/summon/sync endpoint
def test_sync_endpoint():
    payload = {
        "token_id": "test-token",
        "server_ip": "127.0.0.1",
        "server_port": 19132,
        "summoned_object_type": "piglin",
        "summoning_player": "ActorPlayer",
        "summoned_player": "TargetPlayer",
        "action_type": "Read",
        "minecraft_id": "piglin",
        "entity_summoned": "piglin",
        "timestamp": "2025-12-22T12:00:00Z",
        "gps_lat": 37.7749,
        "gps_lon": -122.4194,
        "client_device_id": "ios-device-123"
    }
    headers = {"x-api-key": "super-secret-test-key22"}
    response = client.post("/api/summon/sync", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "operation_id" in response.json()

# Test /api/summon/sync/batch endpoint
def test_sync_batch_endpoint():
    batch_payload = {
        "summons": [
            {
                "token_id": "test-token-1",
                "player_id": "ActorPlayer1",
                "summon_type": "piglin",
                "summon_time": "2025-12-22T12:00:00Z",
                "location": {"x": 100.5, "y": 64.0, "z": -200.0},
                "metadata": {"custom_name": "Bob", "level": 5}
            },
            {
                "token_id": "test-token-2",
                "player_id": "ActorPlayer2",
                "summon_type": "zombie",
                "summon_time": "2025-12-22T12:01:00Z",
                "location": {"x": 101.5, "y": 65.0, "z": -201.0},
                "metadata": {"custom_name": "Alice", "level": 10}
            }
        ]
    }
    headers = {"x-api-key": "super-secret-test-key22"}
    response = client.post("/api/summon/sync/batch", json=batch_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "operation_id" in response.json()
