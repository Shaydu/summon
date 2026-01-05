# Summon API Documentation (v3.5)

**Version**: 3.5
**Previous Version**: [v3.4](./api-v3.4.md)
**NFC Token Spec**: [v1.1](./nfc/nfc-token-spec-v1.1.md) (Current) | [v1.2](./nfc/nfc-token-spec-v1.2.md) (Future Roadmap)
**Status**: Current

## Changes from v3.4

### NFC Token Format
- **Currently using v1.1 token format** with `action` field (e.g., `"give_diamond_sword"`, `"zombie"`)
- **Future v1.2 format planned** with explicit `action_type`, `item`, `entity` fields (see [v1.2 spec](./nfc/nfc-token-spec-v1.2.md))

### Improvements
- Enhanced documentation with Arduino examples
- Comprehensive API endpoint documentation
- Improved error handling examples
- GPS tracking support in token format

## Table of Contents

1. [Authentication](#authentication)
2. [Give Item Endpoint](#give-item-endpoint)
3. [Time Endpoint](#time-endpoint)
4. [Say (Broadcast) Endpoint](#say-broadcast-endpoint)
5. [Summon Endpoints](#summon-endpoints)
   - [Immediate Summon (Game Server)](#immediate-summon-endpoint-game-server-target)
   - [Sync Endpoints (Central API)](#sync-endpoints-central-api)
6. [NFC Token Processing](#nfc-token-processing)
7. [Arduino Implementation Guide](#arduino-implementation-guide)
8. [Minecraft Console Commands Reference](#minecraft-server-console-commands-reference)

---

## Authentication

All endpoints require an `x-api-key` (or `X-API-Key`) header with the configured API key.

**Example:**
```
x-api-key: super-secret-test-key22
```

---

## Give Item Endpoint

POST `/give`

Gives an item to a player in-game using the Minecraft `give` command.

### Headers
- `Content-Type: application/json` (required)
- `x-api-key: <API_KEY>` (required)

### Request Body

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `player` | string | Yes | - | Max 64 chars, non-empty | Target player's Minecraft username |
| `item` | string | Yes | - | Max 64 chars, non-empty, valid Minecraft item ID | Item to give (e.g., "emerald", "diamond_sword") |
| `amount` | integer | No | 1 | 1-64 | Number of items to give |

### Request Body Example

```json
{
  "player": "WiryHealer4014",
  "item": "emerald",
  "amount": 1
}
```

### Curl Example

```bash
curl -X POST http://10.0.0.19:8000/give \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{"player":"WiryHealer4014","item":"emerald","amount":1}'
```

### Swift (URLSession) Example

```swift
let url = URL(string: "http://10.0.0.19:8000/give")!
var req = URLRequest(url: url)
req.httpMethod = "POST"
req.setValue("application/json", forHTTPHeaderField: "Content-Type")
req.setValue("super-secret-test-key22", forHTTPHeaderField: "x-api-key")

let payload = [
    "player": "WiryHealer4014",
    "item": "emerald",
    "amount": 1
] as [String : Any]

req.httpBody = try? JSONSerialization.data(withJSONObject: payload)

URLSession.shared.dataTask(with: req) { data, resp, err in
    if let data = data {
        let json = try? JSONSerialization.jsonObject(with: data)
        print("Response: \(json ?? [:])")
    }
}.resume()
```

### Response (Success)

```json
{
  "status": "ok",
  "executed": "give WiryHealer4014 emerald 1"
}
```

**Status Code**: 200 OK

### Response (Error)

```json
{
  "status": "error",
  "error": "Invalid item ID"
}
```

**Status Code**: 400 Bad Request (validation error) or 500 Internal Server Error

### Common Error Cases

| Error | Status | Response |
|-------|--------|----------|
| Missing `player` field | 400 | `{"status":"error","error":"player is required"}` |
| Missing `item` field | 400 | `{"status":"error","error":"item is required"}` |
| Invalid amount (< 1 or > 64) | 400 | `{"status":"error","error":"amount must be between 1 and 64"}` |
| Invalid item ID | 400 | `{"status":"error","error":"Invalid item ID"}` |
| Player not found | 400 | `{"status":"error","error":"Player not found"}` |
| Server connection error | 500 | `{"status":"error","error":"Failed to connect to game server"}` |

### Valid Item IDs

See [Minecraft Bedrock Item IDs](https://minecraft.wiki/w/Bedrock_Edition_data_values) for a complete list.

**Common Items:**
- **Resources**: `emerald`, `diamond`, `iron_ingot`, `gold_ingot`, `coal`, `redstone`
- **Tools**: `diamond_sword`, `diamond_pickaxe`, `iron_axe`, `bow`, `fishing_rod`
- **Food**: `apple`, `bread`, `cooked_beef`, `golden_apple`, `cookie`
- **Blocks**: `dirt`, `stone`, `oak_planks`, `glass`, `tnt`, `torch`
- **Misc**: `bucket`, `compass`, `map`, `saddle`, `name_tag`

**Format Notes:**
- Use underscores, not spaces: `diamond_sword` (not "diamond sword")
- Lowercase only: `emerald` (not "Emerald")
- Some items have variations: `oak_planks`, `birch_planks`, etc.

---

## Time Endpoint

POST `/time`

Sets the in-game time to a named value or numeric ticks.

### Headers
- `Content-Type: application/json` (required)
- `x-api-key: <API_KEY>` (required)

### Request Body

| Field | Type | Required | Valid Values | Description |
|-------|------|----------|--------------|-------------|
| `time` | string or integer | Yes | `"day"`, `"night"`, or tick value (0-24000) | Time to set |

### Request Body Examples

**Named time:**
```json
{ "time": "day" }
```

**Numeric ticks:**
```json
{ "time": 6000 }
```

### Time Values

| Value | Ticks | In-Game Time | Description |
|-------|-------|--------------|-------------|
| `"day"` | 1000 | ~7:00 AM | Early morning |
| `"night"` | 13000 | ~7:00 PM | Early evening |
| 0 | 0 | 6:00 AM | Sunrise |
| 6000 | 6000 | 12:00 PM | Noon |
| 12000 | 12000 | 6:00 PM | Sunset |
| 18000 | 18000 | 12:00 AM | Midnight |

### Curl Example

```bash
curl -X POST http://10.0.0.19:8000/time \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{"time":"day"}'
```

### Swift (URLSession) Example

```swift
let url = URL(string: "http://10.0.0.19:8000/time")!
var req = URLRequest(url: url)
req.httpMethod = "POST"
req.setValue("application/json", forHTTPHeaderField: "Content-Type")
req.setValue("super-secret-test-key22", forHTTPHeaderField: "x-api-key")

let json = ["time": "day"]
req.httpBody = try? JSONSerialization.data(withJSONObject: json)

URLSession.shared.dataTask(with: req) { data, resp, err in
    // handle response
}.resume()
```

### Response (Success)

```json
{
  "status": "ok",
  "executed": "time set day"
}
```

**Status Code**: 200 OK

### Response (Error)

```json
{
  "status": "error",
  "error": "Invalid time value"
}
```

**Status Code**: 400 Bad Request or 500 Internal Server Error

---

## Say (Broadcast) Endpoint

POST `/say`

Broadcasts a message to all players in-game using the Minecraft `say` command.

### Headers
- `Content-Type: application/json` (required)
- `x-api-key: <API_KEY>` (required)

### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `message` | string | Yes | Non-empty, max 256 chars | Message to broadcast |

### Request Body Example

```json
{
  "message": "Hello, world!"
}
```

### Curl Example

```bash
curl -X POST http://10.0.0.19:8000/say \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{"message":"Server restarting in 5 minutes!"}'
```

### Swift (URLSession) Example

```swift
let url = URL(string: "http://10.0.0.19:8000/say")!
var req = URLRequest(url: url)
req.httpMethod = "POST"
req.setValue("application/json", forHTTPHeaderField: "Content-Type")
req.setValue("super-secret-test-key22", forHTTPHeaderField: "x-api-key")

let json = ["message": "Hello from iOS"]
req.httpBody = try? JSONSerialization.data(withJSONObject: json)

URLSession.shared.dataTask(with: req) { data, resp, err in
    // handle response
}.resume()
```

### Response (Success)

```json
{
  "status": "ok",
  "executed": "say Hello, world!"
}
```

**Status Code**: 200 OK

### Response (Error)

```json
{
  "status": "error",
  "error": "message is required"
}
```

**Status Code**: 400 Bad Request

---

## Summon Endpoints

### Terminology
- **Actor**: the player/account who initiates the action (causes an item to be given or an entity to be spawned). Maps to `summoning_player` in the `/summon` endpoint.
- **Target**: the player who receives the action (the item is given to, or the entity is spawned nearby). Maps to `summoned_player` in the `/summon` endpoint.

### Immediate Summon Endpoint (Game Server Target)

POST `/summon`

Executes a summon action immediately on the game server. Can handle entity summons or item gives based on the token's `action_type` field.

### Headers
- `Content-Type: application/json` (required)
- `x-api-key: <API_KEY>` (required)

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `token_id` | string | Yes | Unique token identifier (UUID) |
| `server_ip` | string | Yes | Game server IP address |
| `server_port` | integer | Yes | Game server port (1-65535) |
| `summoning_player` | string | Yes | Actor - player who caused the action |
| `summoned_player` | string | Yes | Target - player who receives the action |
| `action_type` | string | Yes | Action type: "give_item", "summon_entity", "set_time", etc. |
| `summoned_object_type` | string | No | Legacy field for entity/item type |
| `minecraft_id` | string | No | Legacy field for entity/item ID |
| `entity_summoned` | string | No | Legacy field for entity name |
| `timestamp` | string | Yes | ISO8601 UTC timestamp |
| `gps_lat` | number | No | Latitude where token was scanned |
| `gps_lon` | number | No | Longitude where token was scanned |
| `client_device_id` | string | No | Device identifier |

### Request Body Example (Entity Summon)

```json
{
  "token_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_ip": "10.0.0.19",
  "server_port": 19132,
  "summoning_player": "Steve",
  "summoned_player": "Alex",
  "action_type": "summon_entity",
  "summoned_object_type": "piglin",
  "minecraft_id": "piglin",
  "entity_summoned": "piglin",
  "timestamp": "2025-12-25T12:00:00Z",
  "gps_lat": 37.7749,
  "gps_lon": -122.4194,
  "client_device_id": "ios-device-123"
}
```

### Response (Success)

```json
{
  "status": "ok",
  "executed": "summon piglin ~ ~ ~",
  "operation_id": "api-op-123"
}
```

**Status Code**: 200 OK

### Response (Error)

```json
{
  "detail": "Invalid entity type",
  "code": "INVALID_ENTITY"
}
```

**Status Code**: 400 Bad Request or 500 Internal Server Error

---

## Sync Endpoints (Central API)

The API provides sync endpoints for reliable batch processing of summon operations when immediate execution to game servers is not possible.

### SummonPayload

Fields (JSON keys / types):

- `token_id` (string) — required. UUID or unique token identifier for the NFC token.
- `player_id` (string) — required. The actor (player who caused the action). Trimmed on the client; must be non-empty.
- `summon_type` (string) — required. Non-empty string describing the entity/item type (e.g., "piglin", "emerald").
- `summon_time` (string) — required. ISO 8601 UTC timestamp.
- `location` (object) — required. Coordinates with `x`, `y`, `z` (float / number).
- `metadata` (object, required) — structured metadata. Common fields:
  - `custom_name` (string, optional) — max 32 chars
  - `level` (integer, optional) — 1..100
  - `action_type` (string, optional) — "give_item", "summon_entity", etc.
  - `item` (string, optional) — item ID for give_item actions
  - `entity` (string, optional) — entity ID for summon_entity actions

Example SummonPayload:

```json
{
  "token_id": "abc123",
  "player_id": "ActorPlayer",
  "summon_type": "piglin",
  "summon_time": "2025-12-25T15:00:00Z",
  "location": { "x": 100.5, "y": 64.0, "z": -200.0 },
  "metadata": {
    "custom_name": "Bob",
    "level": 5,
    "action_type": "summon_entity",
    "entity": "piglin"
  }
}
```

### POST `/api/summon/sync` (single)

- Request: single `SummonPayload` as JSON.
- On success: 200 OK.
- On validation failure: 400 Bad Request with an error description.

### POST `/api/summon/sync/batch` (atomic batch)

Request body:

```json
{
  "summons": [
    /* array of SummonPayload objects */
  ]
}
```

- **Atomicity**: The batch is all-or-nothing. If any record fails validation or processing, the entire request returns 400 and no records are applied.
- On success: 200 OK.
- On 400: the server MUST return a structured `BatchErrorResponse` describing per-record validation errors.

BatchErrorResponse schema:

```json
{
  "status": "error",
  "errors": [
    {
      "token_id": "abc123",
      "field": "player_id",
      "message": "player_id is required"
    },
    {
      "token_id": "def456",
      "field": "summon_time",
      "message": "invalid ISO timestamp"
    }
  ]
}
```

### Validation Rules

- `token_id`: non-empty, max 64 chars.
- `player_id`: non-empty, trimmed, max 64 chars.
- `summon_type`: non-empty, trimmed, max 64 chars.
- `summon_time`: valid ISO 8601 UTC timestamp.
- `location`: `x`, `y`, `z` each numeric.
- `metadata`: required object. `custom_name` (max 32 chars) and `level` (int, 1..100) validated if provided.

---

## NFC Token Processing

### How NFC Tokens Map to API Endpoints

When an NFC token is scanned, the iOS app processes it based on the `action` field (v1.1 format):

| action (v1.1) | Endpoint Called | Fields Used |
|-------------|----------------|-------------|
| `give_<item>` (e.g., `give_emerald`) | `POST /give` | `player`, item extracted from action |
| Entity name (e.g., `zombie`, `piglin`) | `POST /summon` | `player`, `action`, `position`, etc. |
| `set_time` | `POST /time` | `time` |
| Any action with `time` field | Primary action + `POST /time` | Action-specific + `time` |

### Processing Flow

1. **Scan NFC token** - Read JSON payload from NFC tag
2. **Parse and validate** - Decode JSON and validate required fields (v1.1 format)
3. **Check action field** - Determine action type from `action` string
   - If starts with `give_` → Extract item and call `/give` endpoint
   - If equals `set_time` → Call `/time` endpoint
   - Otherwise → Call `/summon` endpoint for entity
4. **Call API endpoint** - Make HTTP POST request with appropriate payload
5. **Handle time field** - If token has optional `time` field, call `/time` endpoint after primary action
6. **Log result** - Store result in local persistence with GPS coordinates

### Example: Give Item Token Processing (v1.1 format)

**Token scanned:**
```json
{
  "tokenId": "550e8400-e29b-41d4-a716-446655440001",
  "player": "WiryHealer4014",
  "action": "give_emerald",
  "server": "10.0.0.19",
  "port": 8000,
  "timestamp": "2025-12-25T22:17:27Z",
  "time": "day"
}
```

**Processing:**
1. App parses `action: "give_emerald"` → detects `give_` prefix
2. Extracts item: `"emerald"`

**API calls made:**
1. `POST http://10.0.0.19:8000/give` with body:
   ```json
   {"player":"WiryHealer4014","item":"emerald","amount":1}
   ```

2. `POST http://10.0.0.19:8000/time` with body:
   ```json
   {"time":"day"}
   ```

### Example: Summon Entity Token Processing (v1.1 format)

**Token scanned:**
```json
{
  "tokenId": "550e8400-e29b-41d4-a716-446655440002",
  "player": "Steve",
  "action": "zombie",
  "server": "minecraft.example.com",
  "port": 19132,
  "timestamp": "2025-12-25T21:00:00Z",
  "time": "night",
  "mob_type": "hostile"
}
```

**Processing:**
1. App parses `action: "zombie"` → no `give_` prefix, not `set_time`
2. Routes to `/summon` endpoint as entity summon

**API calls made:**
1. `POST http://minecraft.example.com:19132/summon` with body containing:
   ```json
   {
     "token_id": "550e8400-e29b-41d4-a716-446655440002",
     "summoning_player": "Steve",
     "summoned_player": "Steve",
     "action_type": "Read",
     "minecraft_id": "zombie",
     "entity_summoned": "zombie",
     ...
   }
   ```

2. `POST http://minecraft.example.com:19132/time` with body:
   ```json
   {"time":"night"}
   ```

### Swift Processing Example (v1.1 format)

```swift
func processNFCToken(_ token: NFCToken) async throws {
    let baseURL = "http://\(token.server):\(token.port)"

    // Parse action field to determine type
    if token.action.starts(with: "give_") {
        // Extract item from action (e.g., "give_emerald" -> "emerald")
        let item = String(token.action.dropFirst("give_".count))

        try await giveItem(
            baseURL: baseURL,
            player: token.player,
            item: item,
            amount: 1
        )
    } else if token.action == "set_time" {
        guard let time = token.time else {
            throw NFCError.missingRequiredField("time")
        }

        try await setTime(baseURL: baseURL, time: time)
    } else {
        // Summon entity (action contains entity name like "zombie", "piglin")
        try await summonEntity(
            baseURL: baseURL,
            token: token,
            entity: token.action
        )
    }

    // Optional: Set time after primary action (for non-set_time actions)
    if token.action != "set_time", let time = token.time {
        try await setTime(baseURL: baseURL, time: time)
    }
}
```

---

## Arduino Implementation Guide

### Overview

Arduino and other embedded clients can write NFC tokens and call API endpoints directly. This section provides complete examples.

### Required Libraries

```cpp
#include <ArduinoJson.h>   // For JSON serialization
#include <WiFi.h>           // For network connectivity
#include <HTTPClient.h>     // For HTTP requests
#include <PN532_HSU.h>      // For NFC operations
#include <PN532.h>
```

### Writing an NFC Token (Give Item) - v1.1 Format

```cpp
void writeGiveItemToken(const char* item) {
    // Create JSON document
    StaticJsonDocument<512> doc;

    // Required fields (v1.1)
    doc["tokenId"] = generateUUID();
    doc["player"] = "";  // Will be filled by iOS app at scan time

    // Build action string with "give_" prefix (v1.1 format)
    String actionStr = "give_";
    actionStr += item;
    doc["action"] = actionStr;

    doc["server"] = "10.0.0.19";
    doc["port"] = 8000;
    doc["timestamp"] = getISOTimestamp();

    // Optional: set time when item is given
    doc["time"] = "day";

    // Serialize to string
    String jsonString;
    serializeJson(doc, jsonString);

    Serial.println("Writing token:");
    Serial.println(jsonString);

    // Write to NFC tag
    bool success = writeNFCTag(jsonString);
    if (success) {
        Serial.println("Token written successfully!");
    } else {
        Serial.println("Failed to write token");
    }
}

// Usage:
writeGiveItemToken("emerald");
writeGiveItemToken("diamond_sword");
writeGiveItemToken("bread");
```

### Writing an NFC Token (Summon Entity) - v1.1 Format

```cpp
void writeSummonEntityToken(const char* entity, const char* mobType) {
    StaticJsonDocument<512> doc;

    // Required fields (v1.1)
    doc["tokenId"] = generateUUID();
    doc["player"] = "";

    // Action is just the entity name (v1.1 format - no prefix)
    doc["action"] = entity;

    doc["server"] = "minecraft.example.com";
    doc["port"] = 19132;
    doc["timestamp"] = getISOTimestamp();

    // Optional fields
    doc["time"] = "night";
    doc["mob_type"] = mobType;
    doc["position"] = "~1 ~ ~";

    String jsonString;
    serializeJson(doc, jsonString);

    Serial.println("Writing token:");
    Serial.println(jsonString);

    writeNFCTag(jsonString);
}

// Usage:
writeSummonEntityToken("zombie", "hostile");
writeSummonEntityToken("piglin", "hostile");
writeSummonEntityToken("sheep", "passive");
```

### Calling the /give Endpoint Directly

```cpp
void callGiveAPI(const char* player, const char* item, int amount) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected!");
        return;
    }

    HTTPClient http;

    // Configure endpoint
    String url = "http://10.0.0.19:8000/give";
    http.begin(url);

    // Set headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("x-api-key", "super-secret-test-key22");

    // Build JSON payload
    StaticJsonDocument<256> doc;
    doc["player"] = player;
    doc["item"] = item;
    doc["amount"] = amount;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    Serial.println("Calling /give endpoint:");
    Serial.println(jsonPayload);

    // Send POST request
    int httpResponseCode = http.POST(jsonPayload);

    // Handle response
    if (httpResponseCode > 0) {
        Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        String response = http.getString();
        Serial.println("Response:");
        Serial.println(response);

        // Parse response
        StaticJsonDocument<256> responseDoc;
        DeserializationError error = deserializeJson(responseDoc, response);

        if (!error) {
            const char* status = responseDoc["status"];
            const char* executed = responseDoc["executed"];

            if (strcmp(status, "ok") == 0) {
                Serial.printf("Success! Executed: %s\n", executed);
            } else {
                const char* errorMsg = responseDoc["error"];
                Serial.printf("Error: %s\n", errorMsg);
            }
        }
    } else {
        Serial.printf("Error on sending POST: %d\n", httpResponseCode);
    }

    http.end();
}

// Usage:
callGiveAPI("WiryHealer4014", "emerald", 1);
callGiveAPI("Steve", "diamond_sword", 1);
callGiveAPI("Alex", "bread", 64);
```

### Helper Functions

```cpp
// Generate a simple UUID v4
String generateUUID() {
    char uuid[37];
    sprintf(uuid, "%08x-%04x-%04x-%04x-%012llx",
        random(0xFFFFFFFF),
        random(0xFFFF),
        0x4000 | (random(0x0FFF)),  // Version 4
        0x8000 | (random(0x3FFF)),  // Variant 10
        ((uint64_t)random(0xFFFFFFFF) << 32) | random(0xFFFFFFFF)
    );
    return String(uuid);
}

// Get current timestamp in ISO8601 format
String getISOTimestamp() {
    // If you have RTC or NTP time:
    // struct tm timeinfo;
    // if (!getLocalTime(&timeinfo)) {
    //     return "2025-12-25T00:00:00Z";  // Fallback
    // }
    // char buffer[25];
    // strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
    // return String(buffer);

    // Simple fallback if no time source:
    return "2025-12-25T00:00:00Z";
}

// Write JSON string to NFC tag
bool writeNFCTag(const String& jsonString) {
    // Convert JSON string to byte array
    uint8_t payload[jsonString.length()];
    jsonString.getBytes(payload, jsonString.length() + 1);

    // Create NDEF message
    NdefMessage message = NdefMessage();
    message.addMimeMediaRecord("application/json", payload, jsonString.length());

    // Write to tag (pseudo-code, depends on your NFC library)
    // return nfc.write(message);

    // For now, just return true for demo
    return true;
}
```

### Complete Arduino Example

```cpp
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* apiKey = "super-secret-test-key22";
const char* serverIP = "10.0.0.19";
const int serverPort = 8000;

void setup() {
    Serial.begin(115200);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected!");

    // Write some example tokens
    writeGiveItemToken("emerald", 1);
    delay(2000);
    writeGiveItemToken("diamond_sword", 1);
    delay(2000);
    writeSummonEntityToken("zombie", "hostile");
    delay(2000);

    // Or call API directly
    callGiveAPI("WiryHealer4014", "emerald", 1);
}

void loop() {
    // Your main loop code
    delay(1000);
}
```

### Error Handling

```cpp
void callGiveAPIWithErrorHandling(const char* player, const char* item, int amount) {
    // Validate inputs
    if (strlen(player) == 0) {
        Serial.println("Error: player cannot be empty");
        return;
    }
    if (strlen(item) == 0) {
        Serial.println("Error: item cannot be empty");
        return;
    }
    if (amount < 1 || amount > 64) {
        Serial.println("Error: amount must be between 1 and 64");
        return;
    }

    // Check WiFi
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Error: WiFi not connected");
        return;
    }

    HTTPClient http;
    http.begin(String("http://") + serverIP + ":" + serverPort + "/give");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("x-api-key", apiKey);
    http.setTimeout(5000);  // 5 second timeout

    StaticJsonDocument<256> doc;
    doc["player"] = player;
    doc["item"] = item;
    doc["amount"] = amount;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpCode = http.POST(jsonPayload);

    if (httpCode > 0) {
        String response = http.getString();

        if (httpCode == 200) {
            Serial.println("✓ Success!");
            Serial.println(response);
        } else if (httpCode == 400) {
            Serial.println("✗ Bad Request (validation error)");
            Serial.println(response);
        } else if (httpCode == 401 || httpCode == 403) {
            Serial.println("✗ Authentication failed (check API key)");
        } else if (httpCode == 500) {
            Serial.println("✗ Server error");
            Serial.println(response);
        } else {
            Serial.printf("✗ Unexpected response code: %d\n", httpCode);
        }
    } else {
        Serial.printf("✗ HTTP request failed: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
}
```

---

## Minecraft Server Console Commands Reference

For a comprehensive list of Minecraft Bedrock server console commands, see:

- [bedrock_commands.md](bedrock_commands.md)

This includes commands for player management, server management, and debugging, such as:
- `list` — List all players currently online
- `kick <player>` — Kick a player from the server
- `summon <entity> [x y z]` — Spawn an entity at a specific location
- `give <player> <item> [amount]` — Give an item to a player
- `time set <value>` — Set the in-game time
- `stop` — Stop the server
- ...and many more

Refer to the linked document for full details, usage, and notes.

### Manual Commands via Console

**Give item:**
```
give WiryHealer4014 diamond_sword 1
give Steve emerald 64
give Alex bread 32
```

**Summon entity:**
```
summon zombie ~ ~ ~
summon piglin ~1 ~ ~
summon creeper 100 64 -200
```

**Set time:**
```
time set day
time set night
time set 6000
```

---

## Summary

### Key Features in v3.5

1. **NFC Token Support**: v1.1 format with `action` field (e.g., `"give_emerald"`, `"zombie"`)
2. **GPS Tracking**: Optional GPS coordinates for write and read locations
3. **Time Control**: Optional `time` field can be combined with any action
4. **Multiple Endpoints**: `/give`, `/time`, `/say`, `/summon` for different actions
5. **Arduino Friendly**: Simple JSON construction with well-documented examples
6. **Future Ready**: v1.2 format planned for enhanced type safety

### Current Token Format (v1.1)

| Action Type | Token Example |
|-------------|---------------|
| Give Item | `"action": "give_emerald"` |
| Summon Entity | `"action": "zombie"` |
| Set Time | `"action": "set_time", "time": "day"` |

### Future Token Format (v1.2 - Planned)

| Action Type | Planned Token Example |
|-------------|----------------------|
| Give Item | `"action_type": "give_item", "item": "emerald"` |
| Summon Entity | `"action_type": "summon_entity", "entity": "zombie"` |
| Set Time | `"action_type": "set_time", "time": "day"` |

---

**Document Status**: v3.5 - December 25, 2025
**Maintained by**: Summon Project
**Related Documents**:
- [NFC Token Spec v1.2](./nfc/nfc-token-spec-v1.2.md)
- [Architecture v3.4](./architecture-v3.4.md)
- [Previous API v3.4](./api-v3.4.md)
