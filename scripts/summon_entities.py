from fastapi.testclient import TestClient
import sys, os, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nfc_api import app

client = TestClient(app)
headers = {"x-api-key": "super-secret-test-key22"}

def make_payload(entity, player="WiryHealer4014"):
    return {
        "token_id": "test-token-" + entity,
        "server_ip": "10.0.0.19",
        "server_port": 19132,
        "summoned_object_type": entity,
        "summoning_player": player,
        "summoned_player": player,
        "action_type": "Read",
        "minecraft_id": entity,
        "entity_summoned": entity,
        "timestamp": "2025-12-23T12:00:00Z",
        "gps_lat": 0.0,
        "gps_lon": 0.0,
        "client_device_id": "test-client-1"
    }

for ent in ("piglin", "ender_dragon"):
    payload = make_payload(ent)
    resp = client.post("/summon", json=payload, headers=headers)
    print("---", ent)
    print("status_code:", resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print("response_text:", resp.text)
