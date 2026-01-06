#!/bin/bash
# Test NFC Token v1.1.1 format with GPS coordinates

API_URL="http://localhost:8000"
API_KEY="super-secret-test-key22"

echo "============================================"
echo "Testing NFC Token v1.1.1 Format Support"
echo "============================================"
echo ""

# Test 1: Summon entity with GPS (v1.1.1 format) - Versioned endpoint
echo "Test 1: Summon zombie with GPS coordinates (Boulder, CO)"
echo "Token format: v1.1.1 (action: 'zombie')"
echo "Endpoint: /api/v1.1.1/nfc-event"
echo ""

curl -X POST "${API_URL}/api/v1.1.1/nfc-event" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "zombie",
    "player": "TestPlayer",
    "device_id": "test-device-001",
    "gps_lat": 40.0150,
    "gps_lon": -105.2705,
    "timestamp": "2026-01-05T12:00:00Z"
  }' | jq .

echo ""
echo "---"
echo ""

# Test 2: Give item with GPS (v1.1.1 format) - Versioned endpoint
echo "Test 2: Give diamond sword with GPS coordinates"
echo "Token format: v1.1.1 (action: 'give_diamond_sword')"
echo "Endpoint: /api/v1.1.1/nfc-event"
echo ""

curl -X POST "${API_URL}/api/v1.1.1/nfc-event" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "give_diamond_sword",
    "player": "TestPlayer",
    "device_id": "test-device-002",
    "gps_lat": 40.0151,
    "gps_lon": -105.2706,
    "timestamp": "2026-01-05T12:01:00Z"
  }' | jq .

echo ""
echo "---"
echo ""

# Test 3: Legacy endpoint compatibility
echo "Test 3: Test legacy /nfc-event endpoint (should work identically)"
echo ""

curl -X POST "${API_URL}/nfc-event" \
  -H "x-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "piglin",
    "player": "TestPlayer",
    "device_id": "test-device-003",
    "gps_lat": 40.0152,
    "gps_lon": -105.2707,
    "timestamp": "2026-01-05T12:02:00Z"
  }' | jq .

echo ""
echo "---"
echo ""

# Test 3: Query nearby tokens to verify they were written
echo "Test 3: Query nearby tokens (should show the 2 we just wrote)"
echo ""

curl -X GET "${API_URL}/api/tokens/nearby?lat=40.0150&lon=-105.2705&limit=10" \
  -H "x-api-key: ${API_KEY}" | jq .

echo ""
echo "---"
echo ""

# Test 4: Check database directly
echo "Test 4: Check latest tokens in database"
echo ""

PGPASSWORD="summon_pass123" psql -h localhost -U summon_user -d summon_db -c "
SELECT 
  token_id,
  action_type,
  entity,
  item,
  gps_write_lat,
  gps_write_lon,
  written_by,
  device_id,
  written_at
FROM tokens
ORDER BY written_at DESC
LIMIT 5;
"

echo ""
echo "============================================"
echo "Test Complete"
echo "============================================"
