# Summon API v3.1 Documentation (Unified)

This document consolidates the legacy Summon API and the current sync-enabled API, reflecting the latest implementation and data model.

---

## Overview
The Summon API enables atomic, auditable, and offline-first summoning of entities and items in Minecraft Bedrock. It supports both single and batch sync, and tracks all operations for audit and retry.

---

## Endpoints

### POST `/api/summon/sync`
Synchronize a single summon operation.

#### Request Body
```
{
  "token_id": "string",           // Required, unique operation ID
  "player_id": "string",          // Required, target Minecraft player
  "summon_type": "zombie",        // Required, entity/item type (e.g., zombie, diamond_sword)
  "summon_time": "2025-12-22T12:00:00Z", // Required, ISO8601 UTC
  "location": {"x": -95.49, "y": 69.62, "z": -485.60}, // Required, spawn coordinates
  "metadata": {                    // Optional, extra info
    "custom_name": "BossZombie",
    "level": 10
  }
}
```

#### Response
- Success:
```
{"status": "success"}
```
- Error:
```
{"status": "error", "errors": [{"field": "player_id", "message": "player_id is required"}]}
```

---

### POST `/api/summon/sync/batch`
Synchronize a batch of summon operations atomically.

#### Request Body
```
{
  "summons": [ ...single summon objects as above... ]
}
```

#### Response
- Success:
```
{"status": "success"}
```
- Error:
```
{"status": "error", "errors": [{"token_id": "...", "field": "player_id", "message": "player_id is required"}]}
```

---

## Data Model (Superset)
- `token_id`: Unique operation ID (string, required)
- `player_id`: Target Minecraft player (string, required)
- `summon_type`: Entity/item type (string, required)
- `summon_time`: ISO8601 UTC timestamp (string, required)
- `location`: Object with x, y, z (required)
- `metadata`: Optional object (custom_name, level, etc.)

Additional fields for future/compatibility:
- `gps_lat`, `gps_lon`: Optional, float
- `client_device_id`: Optional, string
- `syncStatus`: Optional, string (pending, synced, error)

---

## Operation Flow
1. Client creates summon operation (with all fields above)
2. API validates and logs operation (single or batch)
3. If offline, client retries when online
4. All operations are auditable and atomic

---

## Notes
- All summon requests are logged in the local database
- Only valid Minecraft entities/items are accepted
- player_id must be online for summon to succeed
- For more, see the implementation or contact the API maintainer

---

## Example curl
```
curl -X POST "http://<server-ip>:8000/api/summon/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": "abc123",
    "player_id": "WiryHealer4014",
    "summon_type": "piglin",
    "summon_time": "2025-12-22T12:00:00Z",
    "location": {"x": -95.49, "y": 69.62, "z": -485.60},
    "metadata": {"custom_name": "PiglinBoss"}
  }'
```

---

## Sources
- [Original Summon API](archive/summon_api.md)
- [Sync Implementation](summon_api_synced.md)
- [API Implementation](../api_sync_v3.py)
