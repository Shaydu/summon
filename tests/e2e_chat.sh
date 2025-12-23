#!/bin/bash
# E2E test for /chat endpoint
set -e
API_KEY="super-secret-test-key22"
SERVER_URL="http://localhost:8000"

# Test valid chat
resp=$(curl -s -X POST "$SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"sender": "Steve", "message": "Hello from E2E!"}')
echo "$resp" | grep '"status":"ok"' && echo "[E2E] /chat success test passed"

echo "$resp"

# Test missing sender
resp=$(curl -s -X POST "$SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"message": "No sender!"}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /chat missing sender test passed"

echo "$resp"

# Test missing message
resp=$(curl -s -X POST "$SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"sender": "Alex"}')
echo "$resp" | grep '"status":"error"' && echo "[E2E] /chat missing message test passed"

echo "$resp"

# Test invalid API key
resp=$(curl -s -X POST "$SERVER_URL/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: wrong-key" \
  -d '{"sender": "Alex", "message": "Hi"}')
echo "$resp" | grep 'Invalid API key' && echo "[E2E] /chat invalid API key test passed"

echo "$resp"
