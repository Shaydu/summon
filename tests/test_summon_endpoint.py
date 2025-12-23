import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

def test_summon():
    data = {
        "token_id": "550e8400-e29b-41d4-a716-446655440000",
        "server_ip": "10.0.0.19",
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
    response = client.post("/summon", json=data, headers=headers)
    assert response.status_code == 200
    resp = response.json()
    assert resp["status"] == "ok"
    assert "executed" in resp
    # Expect the server to construct the command using the target player and entity
    expected_cmd = f"execute as @a[name={data['summoned_player']}] at @s run summon {data['entity_summoned']} ~ ~5 ~4"
    assert resp.get("executed") == expected_cmd
    assert "operation_id" in resp
    # Ensure the command was sent to the server console
    assert resp.get("sent") is True
