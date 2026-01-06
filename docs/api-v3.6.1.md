# Summon API Documentation (v3.6.1)

**Version**: 3.6.1  
**Previous Version**: [v3.6](./api-v3.6.md)  
**Status**: ✅ Implemented  
**Date**: January 5, 2026  
**NFC Token Format**: [v1.1.1](nfc-token-v1.1.1.md)

## Changes from v3.6

### New Features

- **NFC Token v1.1.1 Support**: GPS-enabled tokens with `gps_lat` and `gps_lon` fields
- **Versioned NFC Endpoint**: `POST /api/v1.1.1/nfc-event` for explicit version support
- **Nearby Tokens Query**: `GET /api/tokens/nearby` - Find tokens near GPS coordinates for navigation
  - Returns up to 50 closest tokens sorted by distance
  - Includes distance in meters and bearing in degrees
  - Filters by action type (summon_entity, give_item) and mob type (hostile, neutral, passive)
  - Enables ESP32 navigation UI to guide users to physical NFC tokens
- **Token Discovery Database**: All tokens with GPS coordinates stored for nearby discovery
- **Enhanced Validation**: Required field validation with clear error messages

### Use Case

The nearby tokens endpoint enables ESP32 NFC scanners to implement a navigation feature:
1. User requests nearby tokens from their current GPS position
2. API returns N closest tokens with distance and bearing
3. User selects a token from the list
4. Device shows directional arrow, bearing, and distance to guide user to token
5. User walks to token location and scans NFC tag

---

## Table of Contents

1. [Write Token Endpoint](#write-token-endpoint) **NEW - Register programmed NFC tags**
2. [Scan Token Endpoint](#scan-token-endpoint) **Read NFC tags and execute actions**
3. [Nearby Tokens Endpoint](#nearby-tokens-endpoint) **NEW in v3.6.1**
4. [Summon Endpoint](#summon-endpoint)
5. [Give Endpoint](#give-endpoint)
6. [Chat Endpoint](#chat-endpoint)
7. [Say Endpoint](#say-endpoint)
8. [Time Endpoint](#time-endpoint)
9. [Device Location Endpoint](#device-location-endpoint)
10. [Query Endpoints](#query-endpoints)

---

## Write Token Endpoint

### POST `/api/tokens/register`

**📝 Register a newly programmed NFC token.**

**USE WHEN:** You just wrote data to a physical NFC tag and want to register it in the database.

**DOES NOT:** Execute any game commands. Only stores token metadata for discovery.

#### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | Mob or item name (e.g., `"sniffer"`, `"give_diamond_sword"`) |
| `written_by` | string | Player name or device that wrote the token |

#### Optional Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `gps_lat` | float | -90 to 90 | Latitude where token was written |
| `gps_lon` | float | -180 to 180 | Longitude where token was written |
| `device_id` | string | Max 128 chars | Device identifier |
| `nfc_tag_uid` | string | Max 64 chars | NFC tag hardware UID |
| `timestamp` | string | ISO8601 | When token was written |

#### Example Request

```bash
curl -X POST "http://10.0.0.19:8000/api/tokens/register" \
  -H "x-api-key: super-secret-test-key22" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "sniffer",
    "written_by": "WiryHealer4014",
    "gps_lat": 40.7580,
    "gps_lon": -105.3009,
    "device_id": "ios-device-C3039504"
  }'
```

#### Response (Success)

```json
{
  "status": "ok",
  "token_id": "a1b2c3d4-e5f6-4789-a012-3456789abcde",
  "action_type": "summon_entity",
  "entity": "sniffer",
  "gps": {
    "lat": 40.7580,
    "lon": -105.3009
  }
}
```

**Status Code**: 200 OK

---

## Scan Token Endpoint

### POST `/api/v1.1.1/nfc-event`

**📱 Scan/read an NFC token and execute the action.**

**USE WHEN:** User scans a physical NFC tag and you want to execute the action in-game.

**DOES:** Execute game command AND optionally store token metadata.

#### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `action` | string | Mob or item name read from tag (e.g., `"piglin"`, `"give_emerald"`) |
| `player` | string | Player who will receive the action |

#### Optional Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `gps_lat` | float | -90 to 90 | Latitude where token was scanned |
| `gps_lon` | float | -180 to 180 | Longitude where token was scanned |
| `device_id` | string | Max 128 chars | Device identifier |
| `timestamp` | string | ISO8601 | When token was scanned |

#### Example Request

```bash
curl -X POST "http://10.0.0.19:8000/api/v1.1.1/nfc-event" \
  -H "x-api-key: super-secret-test-key22" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "piglin",
    "player": "WiryHealer4014",
    "gps_lat": 40.7580,
    "gps_lon": -105.3009,
    "device_id": "ios-device-123"
  }'
```

#### Response (Success)

```json
{
  "status": "ok",
  "action_type": "summon_entity",
  "entity": "piglin",
  "executed": "execute as @a[name=WiryHealer4014] at @s run summon piglin ~ ~5 ~4",
  "sent": true,
  "token_id": "a1b2c3d4-e5f6-4789-a012-3456789abcde",
  "gps": {
    "lat": 40.7580,
    "lon": -105.3009
  }
}
```

**Status Code**: 200 OK

#### Response (Error - Missing Field)

```json
{
  "status": "error",
  "error": "Missing required field: action"
}
```

**Status Code**: 400 Bad Request

### Endpoint Comparison

| Action | Endpoint | Required Fields | Executes Command? | Stores Token? |
|--------|----------|----------------|-------------------|---------------|
| **Write NFC Tag** | `POST /api/tokens/register` | `action`, `written_by` | ❌ No | ✅ Yes |
| **Scan NFC Tag** | `POST /api/v1.1.1/nfc-event` | `action`, `player` | ✅ Yes | ✅ Yes (if GPS) |

---
        payload["device_id"] = deviceId
    }
    
    if let uid = nfcTagUid {
        payload["nfc_tag_uid"] = uid
    }
    
    request.httpBody = try JSONSerialization.data(withJSONObject: payload)
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw TokenRegistrationError.serverError
    }
    
    return try JSONDecoder().decode(TokenRegistrationResponse.self, from: data)
}
```

#### ESP32 Example

```cpp
bool registerTokenWrite(String action, String writtenBy, float gpsLat, float gpsLon) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[TOKEN] WiFi not connected");
    return false;
  }

  HTTPClient http;
  String url = String(serverIP) + ":8000/api/tokens/register";
  
  http.begin(url);
  http.addHeader("x-api-key", API_KEY);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);

  // Build JSON payload
  StaticJsonDocument<512> doc;
  doc["action"] = action;
  doc["written_by"] = writtenBy;
  doc["gps_lat"] = gpsLat;
  doc["gps_lon"] = gpsLon;
  doc["device_id"] = deviceId;
  doc["timestamp"] = getISO8601Timestamp();

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  Serial.printf("[TOKEN] Registering: %s\n", jsonPayload.c_str());

  int httpCode = http.POST(jsonPayload);
  Serial.printf("[TOKEN] Response code: %d\n", httpCode);

  if (httpCode == 200) {
    String response = http.getString();
    Serial.printf("[TOKEN] Registered: %s\n", response.c_str());
    http.end();
    return true;
  }

  http.end();
  return false;
}
```

### Workflow Summary

**🔵 WORKFLOW 1: Writing/Programming NFC Tags (Token Registration)**
1. User writes "sniffer" to NFC tag using iOS/ESP32
2. App calls `POST /api/tokens/register` with:
   - `action: "sniffer"`
   - `written_by: "WiryHealer4014"`
   - `gps_lat/gps_lon` (if available)
3. Server stores token in database
4. Token becomes discoverable via `/api/tokens/nearby`
5. ❌ **NO game command is executed**

**🟢 WORKFLOW 2: Scanning NFC Tags (Execute Action)**
1. User scans NFC tag with iOS/ESP32
2. Device reads "sniffer" from tag
3. App calls `POST /api/v1.1.1/nfc-event` with:
   - `action: "sniffer"`
   - `player: "WiryHealer4014"`
   - `gps_lat/gps_lon` (if available)
4. ✅ **Server executes game command** (summons sniffer)
5. Server ALSO stores token in database (if GPS provided)

**🟡 WORKFLOW 3: Direct Summon (No NFC Tag)**
1. App/script calls `POST /summon` with:
   - `summoning_player: "WiryHealer4014"`
   - `summoned_player: "WiryHealer4014"`
   - `entity_summoned: "sniffer"`
   - `server_ip`, `server_port`, etc.
   - `gps_lat/gps_lon` (if available)
2. ✅ **Server executes game command** (summons sniffer)
3. Server ALSO stores token in database (if GPS provided)

---

## Nearby Tokens Endpoint

GET `/api/tokens/nearby`

Query for nearby NFC tokens within a search radius, sorted by distance from current GPS position. Returns token metadata including mob/item details, distance in meters, and bearing in degrees.

### Headers
- `x-api-key: <API_KEY>` (required)

### Query Parameters

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `lat` | float | Yes | - | -90 to 90 | Current latitude |
| `lon` | float | Yes | - | -180 to 180 | Current longitude |
| `radius_km` | float | No | 5.0 | 0.1 to 50.0 | Search radius in kilometers |
| `limit` | integer | No | 10 | 1 to 50 | Maximum number of results to return |
| `action_type` | string | No | all | "summon_entity", "give_item", "set_time" | Filter by action type |
| `mob_type` | string | No | all | "hostile", "neutral", "passive" | Filter by mob type (only applies to summon_entity) |

### Request Body Example (ESP32 HTTPClient)

```cpp
HTTPClient http;

// Build query URL with current GPS position
String url = "http://10.0.0.19:8000/api/tokens/nearby?";
url += "lat=" + String(gps.location.lat(), 6);
url += "&lon=" + String(gps.location.lng(), 6);
url += "&limit=10";

http.begin(url);
http.addHeader("x-api-key", "super-secret-test-key22");
http.setTimeout(5000);

int httpCode = http.GET();

if (httpCode == 200) {
  String response = http.getString();

  // Parse with ArduinoJson
  StaticJsonDocument<8192> doc;
  DeserializationError error = deserializeJson(doc, response);

  if (!error) {
    int count = doc["count"];
    JsonArray tokens = doc["tokens"];

    for (JsonObject token : tokens) {
      String name = token["name"];
      float distance_m = token["distance_m"];
      float bearing = token["bearing"];
      // ... display in UI
    }
  }
}

http.end();
```

### Curl Example

```bash
curl -X GET "http://10.0.0.19:8000/api/tokens/nearby?lat=40.7580&lon=-105.3009&limit=10" \
  -H "x-api-key: super-secret-test-key22"
```

### Response (Success)

```json
{
  "status": "ok",
  "current_position": {
    "lat": 40.7580,
    "lon": -105.3009
  },
  "search_radius_km": 5.0,
  "count": 3,
  "tokens": [
    {
      "token_id": "550e8400-e29b-41d4-a716-446655440000",
      "action_type": "summon_entity",
      "entity": "piglin",
      "mob_type": "hostile",
      "name": "Piglin",
      "rarity": "common",
      "position": {
        "lat": 40.7590,
        "lon": -105.3020
      },
      "distance_m": 142.5,
      "bearing": 315.7,
      "written_by": "Steve",
      "written_at": "2025-12-25T12:00:00Z"
    },
    {
      "token_id": "550e8400-e29b-41d4-a716-446655440001",
      "action_type": "summon_entity",
      "entity": "zombie",
      "mob_type": "hostile",
      "name": "Zombie",
      "rarity": "common",
      "position": {
        "lat": 40.7585,
        "lon": -105.3015
      },
      "distance_m": 87.3,
      "bearing": 45.2,
      "written_by": "Alex",
      "written_at": "2025-12-25T13:30:00Z"
    },
    {
      "token_id": "550e8400-e29b-41d4-a716-446655440002",
      "action_type": "give_item",
      "item": "diamond_sword",
      "name": "Diamond Sword",
      "rarity": "rare",
      "position": {
        "lat": 40.7575,
        "lon": -105.3005
      },
      "distance_m": 256.8,
      "bearing": 135.9,
      "written_by": "Bob",
      "written_at": "2025-12-24T18:00:00Z"
    }
  ]
}
```

**Status Code**: 200 OK

### Response Fields

#### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always "ok" for successful responses |
| `current_position` | object | Echo of the query lat/lon |
| `search_radius_km` | float | Echo of the search radius used |
| `count` | integer | Number of tokens returned (0 to limit) |
| `tokens` | array | Array of token objects, sorted by distance (closest first) |

#### Token Object Fields

| Field | Type | Optional | Description |
|-------|------|----------|-------------|
| `token_id` | string | No | Unique token identifier (UUID) |
| `action_type` | string | No | "summon_entity", "give_item", or "set_time" |
| `entity` | string | Yes | Minecraft entity ID (only for summon_entity) |
| `item` | string | Yes | Minecraft item ID (only for give_item) |
| `mob_type` | string | Yes | "hostile", "neutral", or "passive" (only for summon_entity) |
| `name` | string | No | Display name (mob name or item name) |
| `rarity` | string | No | "common", "uncommon", "rare", "epic", "legendary" |
| `position` | object | No | Token GPS coordinates (`lat`, `lon`) |
| `distance_m` | float | No | Distance in meters from query position (rounded to 1 decimal) |
| `bearing` | float | No | Bearing in degrees 0-360 from query position to token (rounded to 1 decimal) |
| `written_by` | string | No | Player/device that wrote the token |
| `written_at` | string | No | ISO8601 timestamp when token was written |

### Response (No Results)

When no tokens are found within the search radius:

```json
{
  "status": "ok",
  "current_position": {
    "lat": 40.7580,
    "lon": -105.3009
  },
  "search_radius_km": 5.0,
  "count": 0,
  "tokens": []
}
```

**Status Code**: 200 OK

### Response (Error - Invalid Coordinates)

```json
{
  "status": "error",
  "error": "Invalid latitude: must be between -90 and 90"
}
```

**Status Code**: 400 Bad Request

### Response (Error - Missing API Key)

```json
{
  "status": "error",
  "error": "Unauthorized"
}
```

**Status Code**: 401 Unauthorized

### Common Error Cases

| Error | Status | Response |
|-------|--------|----------|
| Missing `lat` parameter | 400 | `{"status":"error","error":"lat is required"}` |
| Missing `lon` parameter | 400 | `{"status":"error","error":"lon is required"}` |
| Invalid latitude (< -90 or > 90) | 400 | `{"status":"error","error":"Invalid latitude: must be between -90 and 90"}` |
| Invalid longitude (< -180 or > 180) | 400 | `{"status":"error","error":"Invalid longitude: must be between -180 and 180"}` |
| Invalid radius (< 0.1 or > 50) | 400 | `{"status":"error","error":"radius_km must be between 0.1 and 50.0"}` |
| Invalid limit (< 1 or > 50) | 400 | `{"status":"error","error":"limit must be between 1 and 50"}` |
| Invalid action_type | 400 | `{"status":"error","error":"Invalid action_type"}` |
| Invalid mob_type | 400 | `{"status":"error","error":"Invalid mob_type"}` |
| Missing API key header | 401 | `{"status":"error","error":"Unauthorized"}` |
| Invalid API key | 401 | `{"status":"error","error":"Unauthorized"}` |

---

## Distance & Bearing Calculations

The endpoint performs two calculations for each token:

### 1. Haversine Distance

Calculates the great-circle distance in meters between two GPS coordinates using the Haversine formula:

```
a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
c = 2 ⋅ atan2(√a, √(1−a))
d = R ⋅ c

where:
  φ = latitude in radians
  λ = longitude in radians
  R = Earth radius = 6,371,000 meters
  Δφ = φ2 − φ1
  Δλ = λ2 − λ1
```

**Accuracy**: ±0.5% for distances < 1000km (more than sufficient for this use case)

### 2. Bearing Calculation

Calculates the initial bearing (forward azimuth) from query position to token position:

```
y = sin(Δλ) ⋅ cos(φ2)
x = cos(φ1) ⋅ sin(φ2) − sin(φ1) ⋅ cos(φ2) ⋅ cos(Δλ)
θ = atan2(y, x)
bearing = (θ × 180/π + 360) % 360

where:
  bearing = 0° = North
  bearing = 90° = East
  bearing = 180° = South
  bearing = 270° = West
```

**Note**: This is the initial bearing. For long distances, the bearing changes along the great circle path, but for distances < 10km this is negligible.

### Cardinal Direction Mapping

For UI display, bearings can be mapped to cardinal directions:

| Bearing Range | Direction | Abbreviation |
|---------------|-----------|--------------|
| 337.5° - 22.5° | North | N |
| 22.5° - 67.5° | Northeast | NE |
| 67.5° - 112.5° | East | E |
| 112.5° - 157.5° | Southeast | SE |
| 157.5° - 202.5° | South | S |
| 202.5° - 247.5° | Southwest | SW |
| 247.5° - 292.5° | West | W |
| 292.5° - 337.5° | Northwest | NW |

---

## Backend Implementation

### Database Requirements

The backend must have access to:

1. **tokens table** with columns:
   - `token_id` (UUID/string, primary key)
   - `action_type` (string: "summon_entity", "give_item", "set_time")
   - `entity` (string, nullable: Minecraft entity ID like "piglin")
   - `item` (string, nullable: Minecraft item ID like "diamond_sword")
   - `gps_write_lat` (float, nullable: latitude where token was written)
   - `gps_write_lon` (float, nullable: longitude where token was written)
   - `written_by` (string: player/device that wrote token)
   - `written_at` (timestamp: when token was created)

2. **mobs table** (for entity metadata):
   - `minecraft_id` (string, primary key: e.g., "piglin")
   - `name` (string: display name "Piglin")
   - `mob_type` (string: "hostile", "neutral", "passive")
   - `rarity` (string: "common", "uncommon", "rare", etc.)
   - `health`, `damage`, `armor` (integers)
   - `description` (text)

3. **items table** (for item metadata):
   - `minecraft_id` (string, primary key: e.g., "diamond_sword")
   - `name` (string: display name "Diamond Sword")
   - `item_category` (string: "weapon", "tool", "food", etc.)
   - `rarity` (string)
   - `durability`, `armor_value`, `food_value` (integers, nullable)

### SQL Query Example (PostgreSQL)

```sql
WITH token_distances AS (
  SELECT
    t.token_id,
    t.action_type,
    t.entity,
    t.item,
    t.gps_write_lat AS lat,
    t.gps_write_lon AS lon,
    t.written_by,
    t.written_at,

    -- Haversine distance in meters
    6371000 * 2 * ASIN(SQRT(
      POWER(SIN(RADIANS(t.gps_write_lat - $1) / 2), 2) +
      COS(RADIANS($1)) * COS(RADIANS(t.gps_write_lat)) *
      POWER(SIN(RADIANS(t.gps_write_lon - $2) / 2), 2)
    )) AS distance_m,

    -- Bearing in degrees (0-360)
    MOD(
      CAST(
        DEGREES(
          ATAN2(
            SIN(RADIANS(t.gps_write_lon - $2)) * COS(RADIANS(t.gps_write_lat)),
            COS(RADIANS($1)) * SIN(RADIANS(t.gps_write_lat)) -
            SIN(RADIANS($1)) * COS(RADIANS(t.gps_write_lat)) * COS(RADIANS(t.gps_write_lon - $2))
          )
        ) + 360 AS NUMERIC
      ),
      360
    ) AS bearing,

    -- Join mob metadata
    m.name AS mob_name,
    m.mob_type,
    m.rarity AS mob_rarity,

    -- Join item metadata
    i.name AS item_name,
    i.rarity AS item_rarity

  FROM tokens t
  LEFT JOIN mobs m ON t.entity = m.minecraft_id
  LEFT JOIN items i ON t.item = i.minecraft_id

  WHERE
    t.gps_write_lat IS NOT NULL
    AND t.gps_write_lon IS NOT NULL
)

SELECT
  token_id,
  action_type,
  entity,
  item,
  mob_type,
  COALESCE(mob_name, item_name) AS name,
  COALESCE(mob_rarity, item_rarity) AS rarity,
  lat,
  lon,
  ROUND(distance_m::numeric, 1) AS distance_m,
  ROUND(bearing::numeric, 1) AS bearing,
  written_by,
  written_at

FROM token_distances

WHERE
  distance_m <= $3 * 1000  -- radius in km converted to meters
  AND ($4 IS NULL OR action_type = $4)  -- optional action_type filter
  AND ($5 IS NULL OR mob_type = $5)     -- optional mob_type filter

ORDER BY distance_m ASC

LIMIT $6;

-- Query parameters:
-- $1 = lat (query latitude)
-- $2 = lon (query longitude)
-- $3 = radius_km
-- $4 = action_type filter (nullable)
-- $5 = mob_type filter (nullable)
-- $6 = limit
```

### Python Implementation (FastAPI)

Create file: `summon/services/token_service.py`

```python
from fastapi import APIRouter, Header, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import math

router = APIRouter()

# Response models
class TokenPosition(BaseModel):
    lat: float
    lon: float

class NearbyToken(BaseModel):
    token_id: str
    action_type: str
    entity: Optional[str] = None
    item: Optional[str] = None
    mob_type: Optional[str] = None
    name: str
    rarity: str
    position: TokenPosition
    distance_m: float
    bearing: float
    written_by: str
    written_at: str

class NearbyTokensResponse(BaseModel):
    status: str = "ok"
    current_position: TokenPosition
    search_radius_km: float
    count: int
    tokens: List[NearbyToken]

# Haversine distance calculation
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two GPS coordinates."""
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# Bearing calculation
def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing in degrees (0-360) from point 1 to point 2."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda))

    theta = math.atan2(y, x)
    bearing = (math.degrees(theta) + 360) % 360

    return bearing

@router.get("/api/tokens/nearby", response_model=NearbyTokensResponse)
async def get_nearby_tokens(
    lat: float = Query(..., ge=-90, le=90, description="Current latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Current longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=50.0, description="Search radius in km"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    mob_type: Optional[str] = Query(None, description="Filter by mob type"),
    x_api_key: str = Header(..., alias="x-api-key")
):
    """Get nearby tokens sorted by distance."""

    # Verify API key
    from auth import verify_api_key  # Your auth module
    if not verify_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Query database for tokens with GPS coordinates
    # Replace this with your actual database query using the SQL example above
    from database import get_db  # Your database connection

    db = get_db()
    all_tokens = db.execute("""
        SELECT * FROM tokens
        WHERE gps_write_lat IS NOT NULL
        AND gps_write_lon IS NOT NULL
    """).fetchall()

    # Filter by distance and calculate bearing
    nearby_tokens = []
    for token in all_tokens:
        distance_m = haversine_distance(
            lat, lon,
            token.gps_write_lat, token.gps_write_lon
        )

        # Filter by radius
        if distance_m > radius_km * 1000:
            continue

        # Apply action_type filter
        if action_type and token.action_type != action_type:
            continue

        # Apply mob_type filter (only for summon_entity)
        if mob_type and token.mob_type != mob_type:
            continue

        bearing = calculate_bearing(
            lat, lon,
            token.gps_write_lat, token.gps_write_lon
        )

        # Get mob/item name from joined tables
        name = token.mob_name if token.mob_name else token.item_name
        rarity = token.mob_rarity if token.mob_rarity else token.item_rarity

        nearby_token = NearbyToken(
            token_id=token.token_id,
            action_type=token.action_type,
            entity=token.entity,
            item=token.item,
            mob_type=token.mob_type,
            name=name,
            rarity=rarity,
            position=TokenPosition(
                lat=token.gps_write_lat,
                lon=token.gps_write_lon
            ),
            distance_m=round(distance_m, 1),
            bearing=round(bearing, 1),
            written_by=token.written_by,
            written_at=token.written_at.isoformat()
        )
        nearby_tokens.append(nearby_token)

    # Sort by distance and limit results
    nearby_tokens.sort(key=lambda t: t.distance_m)
    nearby_tokens = nearby_tokens[:limit]

    return NearbyTokensResponse(
        current_position=TokenPosition(lat=lat, lon=lon),
        search_radius_km=radius_km,
        count=len(nearby_tokens),
        tokens=nearby_tokens
    )
```

### Register Router in Main API

Edit `nfc_api.py` (or your main API file):

```python
from fastapi import FastAPI
from services import token_service  # NEW IMPORT

app = FastAPI()

# ... existing routers ...

# Add token navigation routes
app.include_router(token_service.router)
```

---

## ESP32 Client Implementation

### Data Structures

```cpp
// Store nearby tokens from API response
struct NearbyToken {
  String tokenId;
  String actionType;
  String entityOrItem;  // entity for mobs, item for items
  String name;          // Display name
  String mobType;       // hostile/neutral/passive (or empty for items)
  String rarity;        // common/uncommon/rare/epic/legendary
  float lat;
  float lon;
  float distanceM;
  float bearing;
  String writtenBy;
  String writtenAt;
};

NearbyToken nearbyTokens[10];
int nearbyTokenCount = 0;
int selectedTokenIndex = -1;
```

### API Call Function

```cpp
bool fetchNearbyTokens() {
  // Check GPS validity
  if (!gps.location.isValid()) {
    Serial.println("[NAV] No GPS fix");
    return false;
  }

  // Check WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[NAV] WiFi not connected");
    return false;
  }

  HTTPClient http;

  // Build query URL
  String url = String(serverIP) + ":8000/api/tokens/nearby?";
  url += "lat=" + String(gps.location.lat(), 6);
  url += "&lon=" + String(gps.location.lng(), 6);
  url += "&limit=10";

  http.begin(url);
  http.addHeader("x-api-key", API_KEY);
  http.setTimeout(5000);

  int httpCode = http.GET();
  Serial.printf("[NAV] Response code: %d\n", httpCode);

  if (httpCode != 200) {
    http.end();
    return false;
  }

  String response = http.getString();
  http.end();

  // Parse JSON response
  StaticJsonDocument<8192> doc;
  DeserializationError error = deserializeJson(doc, response);

  if (error) {
    Serial.printf("[NAV] JSON parse error: %s\n", error.c_str());
    return false;
  }

  nearbyTokenCount = doc["count"];
  Serial.printf("[NAV] Found %d nearby tokens\n", nearbyTokenCount);

  JsonArray tokens = doc["tokens"];
  int idx = 0;

  for (JsonObject token : tokens) {
    if (idx >= 10) break;

    nearbyTokens[idx].tokenId = token["token_id"].as<String>();
    nearbyTokens[idx].actionType = token["action_type"].as<String>();
    nearbyTokens[idx].name = token["name"].as<String>();
    nearbyTokens[idx].rarity = token["rarity"].as<String>();
    nearbyTokens[idx].lat = token["position"]["lat"];
    nearbyTokens[idx].lon = token["position"]["lon"];
    nearbyTokens[idx].distanceM = token["distance_m"];
    nearbyTokens[idx].bearing = token["bearing"];
    nearbyTokens[idx].writtenBy = token["written_by"].as<String>();
    nearbyTokens[idx].writtenAt = token["written_at"].as<String>();

    // Optional fields
    if (token.containsKey("entity")) {
      nearbyTokens[idx].entityOrItem = token["entity"].as<String>();
      nearbyTokens[idx].mobType = token["mob_type"].as<String>();
    } else if (token.containsKey("item")) {
      nearbyTokens[idx].entityOrItem = token["item"].as<String>();
    }

    idx++;
  }

  return true;
}
```

### Distance Formatting

```cpp
String formatDistance(float distanceM) {
  if (distanceM < 1000) {
    return String((int)distanceM) + "m";
  } else {
    return String(distanceM / 1000.0, 1) + "km";
  }
}
```

### Cardinal Direction Helper

```cpp
String bearingToCardinal(float bearing) {
  if (bearing >= 337.5 || bearing < 22.5) return "N";
  if (bearing >= 22.5 && bearing < 67.5) return "NE";
  if (bearing >= 67.5 && bearing < 112.5) return "E";
  if (bearing >= 112.5 && bearing < 157.5) return "SE";
  if (bearing >= 157.5 && bearing < 202.5) return "S";
  if (bearing >= 202.5 && bearing < 247.5) return "SW";
  if (bearing >= 247.5 && bearing < 292.5) return "W";
  if (bearing >= 292.5 && bearing < 337.5) return "NW";
  return "?";
}
```

---

## Testing

### Test with Curl

```bash
# Test with valid coordinates
curl -X GET "http://10.0.0.19:8000/api/tokens/nearby?lat=40.7580&lon=-105.3009&limit=10" \
  -H "x-api-key: super-secret-test-key22"

# Test with filters
curl -X GET "http://10.0.0.19:8000/api/tokens/nearby?lat=40.7580&lon=-105.3009&action_type=summon_entity&mob_type=hostile" \
  -H "x-api-key: super-secret-test-key22"

# Test error: invalid latitude
curl -X GET "http://10.0.0.19:8000/api/tokens/nearby?lat=999&lon=-105.3009" \
  -H "x-api-key: super-secret-test-key22"

# Test error: missing API key
curl -X GET "http://10.0.0.19:8000/api/tokens/nearby?lat=40.7580&lon=-105.3009"
```

### Expected Response Validation

- ✅ `status` field is "ok"
- ✅ `current_position` matches query lat/lon
- ✅ `count` field matches length of `tokens` array
- ✅ `tokens` array is sorted by `distance_m` (ascending)
- ✅ All `distance_m` values are ≤ `search_radius_km * 1000`
- ✅ All `bearing` values are 0-360
- ✅ All `position.lat` values are -90 to 90
- ✅ All `position.lon` values are -180 to 180

---

## Summary

### Key Features

1. **GPS-based proximity search** - Find tokens within configurable radius
2. **Distance calculation** - Haversine formula with ±0.5% accuracy
3. **Bearing calculation** - Initial bearing for navigation arrow
4. **Filtering** - By action type (mobs vs items) and mob type (hostile vs neutral vs passive)
5. **Sorting** - Closest tokens first
6. **Rich metadata** - Mob/item names, rarity, GPS coordinates
7. **ESP32-friendly** - JSON response optimized for ArduinoJson parsing

### Use Cases

- **Navigation UI** - Guide users to physical NFC token locations
- **Token discovery** - "What's nearby?" feature
- **Mob hunting** - Filter to hostile mobs only
- **Treasure hunting** - Filter to rare items
- **Admin dashboard** - Map view of token distribution

---

## Summon Endpoint

### POST `/summon`

**Execute immediate summon action on game server with optional token writing.**

Summons an entity or gives an item to a player. When GPS coordinates are provided, writes a token to the database for nearby discovery.

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Request Body

#### Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `token_id` | string | Max 64 chars | Unique token identifier (UUID) |
| `server_ip` | string | Valid IP | Game server IP address |
| `server_port` | integer | 1-65535 | Game server port |
| `summoning_player` | string | Max 64 chars | Player who initiated the action |
| `summoned_player` | string | Max 64 chars | Player receiving the action |
| `action_type` | string | Max 64 chars | "summon_entity", "give_item", etc. |
| `timestamp` | string | ISO8601 | UTC timestamp |

#### Optional Fields (for Token Writing)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `gps_lat` | float | -90 to 90 | Latitude where token was scanned |
| `gps_lon` | float | -180 to 180 | Longitude where token was scanned |
| `client_device_id` | string | Max 128 chars | Device identifier |
| `summoned_object_type` | string | Max 64 chars | Entity/item type (legacy) |
| `minecraft_id` | string | Max 64 chars | Entity ID (legacy fallback) |
| `entity_summoned` | string | Max 64 chars | Entity name (preferred) |

### Example Request (Entity Summon with GPS)

```bash
curl -X POST "http://10.0.0.19:8000/summon" \
  -H "x-api-key: super-secret-test-key22" \
  -H "Content-Type: application/json" \
  -d '{
    "token_id": "550e8400-e29b-41d4-a716-446655440000",
    "server_ip": "10.0.0.19",
    "server_port": 19132,
    "summoning_player": "WiryHealer4014",
    "summoned_player": "WiryHealer4014",
    "action_type": "summon_entity",
    "summoned_object_type": "zombie",
    "minecraft_id": "zombie",
    "entity_summoned": "zombie",
    "timestamp": "2026-01-05T12:00:00Z",
    "gps_lat": 40.7580,
    "gps_lon": -105.3009,
    "client_device_id": "esp32-001"
  }'
```

### Response (Success)

```json
{
  "status": "ok",
  "executed": "execute as @a[name=WiryHealer4014] at @s run summon zombie ~ ~5 ~4",
  "operation_id": "api-op-a1b2c3d4",
  "sent": true
}
```

**Status Code**: 200 OK

### Response (Success with Token Written)

When GPS coordinates are provided, the response includes token information:

```json
{
  "status": "ok",
  "executed": "execute as @a[name=WiryHealer4014] at @s run summon zombie ~ ~5 ~4",
  "operation_id": "api-op-a1b2c3d4",
  "sent": true,
  "token_id": "550e8400-e29b-41d4-a716-446655440000",
  "token_written": true
}
```

**Status Code**: 200 OK

### Response (Error - Missing Required Field)

```json
{
  "status": "error",
  "error": "Missing required fields: summoning_player, summoned_player"
}
```

**Status Code**: 400 Bad Request

### Response (Error - Invalid Field Value)

```json
{
  "status": "error",
  "error": "Invalid server_port: must be between 1 and 65535"
}
```

**Status Code**: 400 Bad Request

### Response (Error - GPS Coordinates Invalid)

```json
{
  "status": "error",
  "error": "Invalid gps_lat: must be between -90 and 90"
}
```

**Status Code**: 400 Bad Request

### Response (Error - Unauthorized)

```json
{
  "status": "error",
  "error": "Unauthorized"
}
```

**Status Code**: 401 Unauthorized

### Common Error Cases

| Error | Status | Response |
|-------|--------|----------|
| Missing `token_id` | 400 | `{"status":"error","error":"Missing required fields: token_id"}` |
| Missing `summoning_player` | 400 | `{"status":"error","error":"Missing required fields: summoning_player"}` |
| Missing `summoned_player` | 400 | `{"status":"error","error":"Missing required fields: summoned_player"}` |
| Missing `timestamp` | 400 | `{"status":"error","error":"Missing required fields: timestamp"}` |
| Empty `summoning_player` | 400 | `{"status":"error","error":"summoning_player cannot be empty"}` |
| Invalid `server_port` | 400 | `{"status":"error","error":"Invalid server_port: must be between 1 and 65535"}` |
| `token_id` too long (> 64) | 400 | `{"status":"error","error":"token_id must not exceed 64 characters"}` |
| Invalid `gps_lat` | 400 | `{"status":"error","error":"Invalid gps_lat: must be between -90 and 90"}` |
| Invalid `gps_lon` | 400 | `{"status":"error","error":"Invalid gps_lon: must be between -180 and 180"}` |
| Missing API key | 401 | `{"status":"error","error":"Unauthorized"}` |
| Invalid API key | 401 | `{"status":"error","error":"Unauthorized"}` |

### Field Validation Rules

#### String Fields
- All string fields are trimmed of leading/trailing whitespace
- Empty strings (after trimming) are rejected for required fields
- Maximum length constraints are enforced

#### Numeric Fields
- `server_port`: Must be integer between 1 and 65535
- `gps_lat`: Must be float between -90 and 90 (if provided)
- `gps_lon`: Must be float between -180 and 180 (if provided)

#### Timestamp Format
- Must be valid ISO8601 format
- Example: `2026-01-05T12:00:00Z`
- Timezone suffix (`Z` or `+00:00`) required

### Token Writing Behavior

The endpoint automatically writes tokens to the database when **both** `gps_lat` and `gps_lon` are provided:

**Token Written** ✅
```json
{
  "gps_lat": 40.7580,
  "gps_lon": -105.3009
}
```

**Token NOT Written** ❌
```json
{
  "gps_lat": 40.7580
  // Missing gps_lon
}
```

**Token NOT Written** ❌
```json
{
  // Both missing
}
```

### Implementation Notes

The backend implementation should:

1. **Validate all required fields** before processing
2. **Return 400 Bad Request** with clear error messages for missing/invalid fields
3. **Validate GPS coordinates** if provided (even though optional)
4. **Write token atomically** - if token write fails, return error
5. **Execute game command** regardless of token write status (unless token write was required)
6. **Log warnings** if token write fails but game command succeeds

---

## Give Endpoint

### POST `/give`

**Give items to players.**

Works similarly to `/summon` but for item distribution. See [Summon Endpoint](#summon-endpoint) for detailed field specifications.

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Required Fields
- `player` (string): Player receiving the item
- `item` (string): Minecraft item ID
- `quantity` (integer): Number of items (1-64)

### Response (Error - Missing Required Field)

```json
{
  "status": "error",
  "error": "Missing required field: player"
}
```

**Status Code**: 400 Bad Request

---

## Chat Endpoint

### POST `/chat`

**Send chat messages to game server.**

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Required Fields
- `message` (string): Chat message content (max 256 chars)

### Response (Error - Missing Required Field)

```json
{
  "status": "error",
  "error": "Missing required field: message"
}
```

**Status Code**: 400 Bad Request

---

## Say Endpoint

### POST `/say`

**Broadcast messages to all players.**

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Required Fields
- `message` (string): Message content (max 256 chars)

### Response (Error - Missing Required Field)

```json
{
  "status": "error",
  "error": "Missing required field: message"
}
```

**Status Code**: 400 Bad Request

---

## Time Endpoint

### POST `/time`

**Set game time.**

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Required Fields
- `time` (string): Time value ("day", "night", "noon", "midnight", or tick value)

### Response (Error - Invalid Time)

```json
{
  "status": "error",
  "error": "Invalid time value: must be 'day', 'night', 'noon', 'midnight', or a tick number"
}
```

**Status Code**: 400 Bad Request

---

## Device Location Endpoint

### POST `/device-location`

**Track device GPS locations.**

### Headers
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

### Required Fields
- `device_id` (string): Device identifier
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)
- `timestamp` (string): ISO8601 timestamp

### Response (Error - Missing Required Field)

```json
{
  "status": "error",
  "error": "Missing required fields: device_id, lat, lon"
}
```

**Status Code**: 400 Bad Request

### Response (Error - Invalid Coordinates)

```json
{
  "status": "error",
  "error": "Invalid lat: must be between -90 and 90"
}
```

**Status Code**: 400 Bad Request

---

## Query Endpoints

### GET `/players`

**Get list of online players.**

### Headers
- `x-api-key: <API_KEY>` (required)

### Response (Success)

```json
{
  "status": "ok",
  "players": ["WiryHealer4014", "Steve", "Alex"]
}
```

**Status Code**: 200 OK

### GET `/tokens`

**Get all tokens with GPS coordinates.**

### Headers
- `x-api-key: <API_KEY>` (required)

### Response (Success)

```json
{
  "status": "ok",
  "count": 42,
  "tokens": [
    {
      "token_id": "550e8400-e29b-41d4-a716-446655440000",
      "action_type": "summon_entity",
      "entity": "zombie",
      "position": {
        "lat": 40.7580,
        "lon": -105.3009
      },
      "written_by": "WiryHealer4014",
      "written_at": "2026-01-05T12:00:00Z"
    }
  ]
}
```

**Status Code**: 200 OK

---

**Document Status**: v3.6.1 Proposed - January 5, 2026
**Maintained by**: Summon Project
**Related Documents**:
- [API v3.6 (Current)](./api-v3.6.md)
- [NFC Token Spec v1.1.1](../nfc/nfc-token-spec-v1.1.1.md)
- [Backend Integration Guide](./BACKEND-INTEGRATION.md)
