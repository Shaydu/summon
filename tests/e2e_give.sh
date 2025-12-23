#!/bin/bash
# E2E test for /give endpoint
set -e
API_KEY="super-secret-test-key22"
SERVER_URL="http://localhost:8000"

# Test valid give
resp=$(curl -s -X POST "$SERVER_URL/give" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"player": "WiryHealer4014", "item": "diamond_sword", "amount": 1}')
echo "$resp" | grep '"status":"ok"' && echo "[E2E] /give success test passed"

echo "$resp"

# Test missing player
resp=$(curl -s -X POST "$SERVER_URL/give" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"item": "diamond_sword", "amount": 1}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /give missing player test passed"

echo "$resp"

# Test missing item
resp=$(curl -s -X POST "$SERVER_URL/give" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"player": "WiryHealer4014", "amount": 1}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /give missing item test passed"

echo "$resp"

# Test invalid amount
resp=$(curl -s -X POST "$SERVER_URL/give" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"player": "WiryHealer4014", "item": "diamond_sword", "amount": 0}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /give invalid amount test passed"

echo "$resp"

# Test invalid API key
resp=$(curl -s -X POST "$SERVER_URL/give" \
  -H "Content-Type: application/json" \
  -H "x-api-key: wrong-key" \
  -d '{"player": "WiryHealer4014", "item": "diamond_sword", "amount": 1}')
echo "$resp" | grep 'Invalid API key' && echo "[E2E] /give invalid API key test passed"

echo "$resp"
