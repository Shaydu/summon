"""
Test script for API Sync v3 endpoints.
Covers single, batch, and error use cases.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api/summon/sync"
BATCH_URL = "http://127.0.0.1:5000/api/summon/sync/batch"


def print_response(resp):
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text)

# --- Single Success ---
single_payload = {
    "token_id": "abc123",
    "player_id": "player_1",
    "summon_type": "zombie",
    "summon_time": "2025-12-22T15:00:00Z",
    "location": {"x": 100.5, "y": 64.0, "z": -200.0},
    "metadata": {"custom_name": "Bob", "level": 5}
}
print("\n--- Single Sync Success ---")
resp = requests.post(BASE_URL, json=single_payload)
print_response(resp)

# --- Single Error (missing player_id) ---
single_error_payload = dict(single_payload)
del single_error_payload["player_id"]
print("\n--- Single Sync Error (missing player_id) ---")
resp = requests.post(BASE_URL, json=single_error_payload)
print_response(resp)

# --- Batch Success ---
batch_payload = {
    "summons": [
        single_payload,
        {
            "token_id": "def456",
            "player_id": "player_2",
            "summon_type": "skeleton",
            "summon_time": "2025-12-22T15:01:00Z",
            "location": {"x": 101.0, "y": 64.0, "z": -201.0}
        }
    ]
}
print("\n--- Batch Sync Success ---")
resp = requests.post(BATCH_URL, json=batch_payload)
print_response(resp)

# --- Batch Error (invalid summon_type) ---
batch_error_payload = {
    "summons": [
        single_payload,
        {
            "token_id": "ghi789",
            "player_id": "player_3",
            "summon_type": "dragon",
            "summon_time": "2025-12-22T15:02:00Z",
            "location": {"x": 102.0, "y": 64.0, "z": -202.0}
        }
    ]
}
print("\n--- Batch Sync Error (invalid summon_type) ---")
resp = requests.post(BATCH_URL, json=batch_error_payload)
print_response(resp)

# --- Batch Error (missing player_id) ---
batch_error_payload2 = {
    "summons": [
        single_payload,
        {
            "token_id": "jkl012",
            "summon_type": "zombie",
            "summon_time": "2025-12-22T15:03:00Z",
            "location": {"x": 103.0, "y": 64.0, "z": -203.0}
        }
    ]
}
print("\n--- Batch Sync Error (missing player_id) ---")
resp = requests.post(BATCH_URL, json=batch_error_payload2)
print_response(resp)
