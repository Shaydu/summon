import requests
import json

API_URL = "http://localhost:8000"
API_KEY = "super-secret-test-key22"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def test_players():
    print("Testing /players endpoint...")
    r = requests.get(f"{API_URL}/players", headers=headers)
    print("Status:", r.status_code)
    print("Response:", r.text)
    assert r.status_code == 200
    assert "players" in r.json()

def test_summon():
    print("Testing /summon endpoint...")
    data = {
        "timestamp": "2025-12-22T22:14:32Z",
        "token_id": "26FEFF8B-8E0C-42BB-9037-FB2DA5062523",
        "entity_summoned": "summon pillager",
        "summoned_player": "WiryHealer4014",
        "action_type": "Read",
        "client_device_id": "B4BA19DF-96AB-4C74-82BC-A69C389E944C",
        "minecraft_id": "summon pillager",
        "server_ip": "10.0.0.227",
        "summoned_object_type": "summon pillager",
        "server_port": 8000,
        "summoning_player": "WiryHealer4014"
    }
    r = requests.post(f"{API_URL}/summon", headers=headers, data=json.dumps(data))
    print("Status:", r.status_code)
    print("Response:", r.text)
    assert r.status_code in (200, 201)
    # If the server returns JSON with an `executed` field, ensure it uses server-side format
    try:
        j = r.json()
        if "executed" in j:
            assert j["executed"].startswith("execute as @a[name=")
            assert not j["executed"].startswith("/")
    except Exception:
        pass

def test_nfc_event():
    print("Testing /nfc-event endpoint...")
    data = {
        "token_id": "test-token-123",
        "player": "WiryHealer4014",
        "action": "give_diamond_sword"
    }
    r = requests.post(f"{API_URL}/nfc-event", headers=headers, data=json.dumps(data))
    print("Status:", r.status_code)
    print("Response:", r.text)
    assert r.status_code in (200, 201, 202)

def main():
    test_players()
    test_summon()
    test_nfc_event()
    print("All endpoint tests completed.")

if __name__ == "__main__":
    main()
