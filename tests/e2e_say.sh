#!/bin/bash
# E2E test for /say endpoint
set -e
API_KEY="super-secret-test-key22"
SERVER_URL="http://localhost:8000"

# Test valid say
resp=$(curl -s -X POST "$SERVER_URL/say" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"message": "Hello from E2E!"}')
echo "$resp" | grep '"status":"ok"' && echo "[E2E] /say success test passed"

echo "$resp"

# Test missing message
resp=$(curl -s -X POST "$SERVER_URL/say" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /say missing message test passed"

echo "$resp"

# Test invalid API key
resp=$(curl -s -X POST "$SERVER_URL/say" \
  -H "Content-Type: application/json" \
  -H "x-api-key: wrong-key" \
  -d '{"message": "Hi"}')
echo "$resp" | grep 'Invalid API key' && echo "[E2E] /say invalid API key test passed"

echo "$resp"
