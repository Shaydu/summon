# Summon API Documentation

This document describes the API endpoints for summoning in-game non-player characters (NPCs) and objects in Minecraft Bedrock via the FastAPI server.

## Authentication
All endpoints require an `x-api-key` header with the correct API key.

---

## POST `/summon`
Summon an NPC or object at a specific player's location.

### Request
- **URL:** `/summon`
- **Method:** `POST`
- **Headers:**
  - `x-api-key: <your-api-key>`
  - `Content-Type: application/json`
- **Body:**
```json
{
  "server_ip": "<server-ip>",
  "server_port": 19132,
  "summoned_object_type": "piglin", // e.g. "piglin", "creeper", "item_frame"
  "summoning_user": "<username>",   // user who initiated the summon
  "summoned_user": "<playername>",  // player at whose location the object/NPC will be summoned
  "timestamp": "2025-12-22T12:00:00Z", // (optional, UTC ISO8601)
  "gps_lat": 37.7749,                // (optional)
  "gps_lon": -122.4194               // (optional)
}
```

### Response
- **Success:**
```json
{
  "status": "ok",
  "executed": "execute as @a[name=WiryHealer4014] at @s run summon piglin ~ ~ ~2"
}
```
- **Error:**
```json
{
  "detail": "<error message>"
}
```

---

## Example curl
```
curl -X POST "http://<server-ip>:8000/summon" \
  -H "x-api-key: super-secret-test-key22" \
  -H "Content-Type: application/json" \
  -d '{
    "server_ip": "10.0.0.19",
    "server_port": 19132,
    "summoned_object_type": "piglin",
    "summoning_user": "AdminUser",
    "summoned_user": "WiryHealer4014",
    "timestamp": "2025-12-22T12:00:00Z"
  }'
```

---

## Notes
- The `summoned_object_type` must be a valid Minecraft entity or item type.
- The `summoned_user` must be an online player for the summon to succeed.
- All summon requests are logged in the local `summon.db` SQLite database.

---

For more endpoints and details, see the source code or contact the API maintainer.
