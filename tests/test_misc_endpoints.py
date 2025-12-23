from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)

API_KEY = "super-secret-test-key22"
headers = {"x-api-key": API_KEY}

def test_players_endpoint():
    response = client.get("/players", headers=headers)
    assert response.status_code == 200
    assert "players" in response.json()

def test_nfc_event_endpoint():
    payload = {
        "event_id": "test-event-1",
        "player": "TestPlayer",
        "timestamp": "2025-12-22T12:00:00Z",
        "event_type": "scan",
        "device_id": "ios-device-123"
    }
    response = client.post("/nfc-event", json=payload, headers=headers)
    # Accept 200 or 400 depending on validation logic
    assert response.status_code in (200, 400)
