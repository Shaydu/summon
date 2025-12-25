import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)
API_KEY = "super-secret-test-key22"


def test_list_summons_success(monkeypatch):
    sample = [
        {
            "id": 1,
            "server_ip": "1.2.3.4",
            "server_port": 19132,
            "summoned_object_type": "piglin",
            "summoning_player": "scanner",
            "summoned_player": "WiryHealer4014",
            "timestamp_utc": "2025-12-24T12:00:00Z",
            "gps_lat": 12.34,
            "gps_lon": 56.78,
        }
    ]
    monkeypatch.setattr("summon_db.get_all_summons", lambda: sample)
    resp = client.get("/summons", headers={"x-api-key": API_KEY})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["summons"], list)
    assert data["summons"][0]["server_ip"] == "1.2.3.4"


def test_list_summons_invalid_key():
    resp = client.get("/summons", headers={"x-api-key": "bad"})
    assert resp.status_code == 401
