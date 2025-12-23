from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

data = {
    "token_id": "550e8400-e29b-41d4-a716-446655440000",
    "server_ip": "10.0.0.19",
    "server_port": 19132,
    "summoned_object_type": "piglin",
    "summoning_player": "ActorPlayer",
    "summoned_player": "WiryHealer4014",
    "action_type": "Read",
    "minecraft_id": "ender_dragon",
    "entity_summoned": "ender_dragon",
    "timestamp": "2025-12-22T12:00:00Z",
    "gps_lat": 37.7749,
    "gps_lon": -122.4194,
    "client_device_id": "ios-device-123"
}

resp = client.post("/summon", json=data, headers=headers)
print('status_code=', resp.status_code)
try:
    print(resp.json())
except Exception as e:
    print('response text:', resp.text)
