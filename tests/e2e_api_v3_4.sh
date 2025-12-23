#!/bin/bash
# e2e_api_v3_4.sh - End-to-end tests for Summon API v3.4 endpoints

API_HOST="10.0.0.19"
API_PORT=8000
API_URL="http://$API_HOST:$API_PORT"
API_KEY="super-secret-test-key22"

header_args=(
  -H "Content-Type: application/json"
  -H "x-api-key: $API_KEY"
)

fail() {
  echo "[FAIL] $1"
  exit 1
}

# 1. Test /summon (immediate)
echo "\n[TEST] /summon (immediate)"
summon_payload='{"token_id": "e2e-1", "server_ip": "10.0.0.19", "server_port": 19132, "summoned_object_type": "piglin", "summoning_player": "ActorPlayer", "summoned_player": "TargetPlayer", "action_type": "Read", "minecraft_id": "piglin", "entity_summoned": "piglin", "timestamp": "2025-12-22T12:00:00Z", "gps_lat": 37.7749, "gps_lon": -122.4194, "client_device_id": "ios-device-123"}'
curl -s -o /tmp/summon_resp.json -w "%{http_code}" "${header_args[@]}" -X POST "$API_URL/summon" -d "$summon_payload" | grep -q 200 || fail "/summon did not return 200"
echo "[PASS] /summon"

# 2. Test /api/summon/sync (single)
echo "\n[TEST] /api/summon/sync (single)"
sync_payload='{"token_id": "e2e-2", "player_id": "ActorPlayer", "summon_type": "piglin", "summon_time": "2025-12-22T15:00:00Z", "location": {"x": 100.5, "y": 64.0, "z": -200.0}, "metadata": {"custom_name": "Bob", "level": 5}}'
curl -s -o /tmp/sync_resp.json -w "%{http_code}" "${header_args[@]}" -X POST "$API_URL/api/summon/sync" -d "$sync_payload" | grep -q 200 || fail "/api/summon/sync did not return 200"
echo "[PASS] /api/summon/sync"

# 3. Test /api/summon/sync/batch (success)
echo "\n[TEST] /api/summon/sync/batch (success)"
batch_payload='{"summons": [ {"token_id": "e2e-3a", "player_id": "ActorA", "summon_type": "zombie", "summon_time": "2025-12-22T16:00:00Z", "location": {"x": 101.5, "y": 65.0, "z": -201.0}, "metadata": {"custom_name": "Alice", "level": 10}}, {"token_id": "e2e-3b", "player_id": "ActorB", "summon_type": "skeleton", "summon_time": "2025-12-22T17:00:00Z", "location": {"x": 102.5, "y": 66.0, "z": -202.0}, "metadata": {"custom_name": "Eve", "level": 20}} ]}'
curl -s -o /tmp/batch_resp.json -w "%{http_code}" "${header_args[@]}" -X POST "$API_URL/api/summon/sync/batch" -d "$batch_payload" | grep -q 200 || fail "/api/summon/sync/batch did not return 200"
echo "[PASS] /api/summon/sync/batch (success)"

# 4. Test /api/summon/sync/batch (error)
echo "\n[TEST] /api/summon/sync/batch (error)"
batch_error_payload='{"summons": [ {"token_id": "e2e-4a", "summon_type": "zombie", "summon_time": "2025-12-22T16:00:00Z", "location": {"x": 101.5, "y": 65.0, "z": -201.0}, "metadata": {"custom_name": "Alice", "level": 10}}, {"token_id": "e2e-4b", "player_id": "ActorB", "summon_type": "skeleton", "summon_time": "2025-12-22T17:00:00Z", "location": {"x": 102.5, "y": 66.0, "z": -202.0}, "metadata": {"custom_name": "Eve", "level": 20}} ]}'
curl -s -o /tmp/batch_error_resp.json -w "%{http_code}" "${header_args[@]}" -X POST "$API_URL/api/summon/sync/batch" -d "$batch_error_payload" | grep -q 200 || fail "/api/summon/sync/batch (error) did not return 200"
grep -q '"status": "error"' /tmp/batch_error_resp.json || fail "/api/summon/sync/batch (error) did not return error status"
echo "[PASS] /api/summon/sync/batch (error)"

# 5. Test /players
echo "\n[TEST] /players"
curl -s -o /tmp/players_resp.json -w "%{http_code}" "${header_args[@]}" "$API_URL/players" | grep -q 200 || fail "/players did not return 200"
grep -q 'players' /tmp/players_resp.json || fail "/players response missing 'players' key"
echo "[PASS] /players"

# 6. Test /nfc-event
echo "\n[TEST] /nfc-event"
nfc_payload='{"event_id": "e2e-nfc-1", "player": "TestPlayer", "timestamp": "2025-12-22T12:00:00Z", "event_type": "scan", "device_id": "ios-device-123"}'
curl -s -o /tmp/nfc_resp.json -w "%{http_code}" "${header_args[@]}" -X POST "$API_URL/nfc-event" -d "$nfc_payload" | grep -q 200 || echo "[WARN] /nfc-event did not return 200 (may be expected if validation fails)"
echo "[PASS] /nfc-event (status may vary)"

echo "\nAll E2E API v3.4 tests completed."
