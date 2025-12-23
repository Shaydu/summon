# Say (Broadcast) Endpoint

POST `/say`

Broadcasts a message to all players in-game using the Minecraft `say` command.

Headers:
- `Content-Type: application/json`
- `x-api-key: <API_KEY>` (required)

Request Body (example):

```json
{
  "message": "Hello, world!"
}
```

Curl example:

```bash
curl -X POST http://YOUR_SERVER:8000/say \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{"message":"Server restarting soon!"}'
```

Swift (URLSession) example:

```swift
let url = URL(string: "http://YOUR_SERVER:8000/say")!
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

Response (success):

```json
{ "status": "ok", "executed": "say Hello, world!" }
```

Response (error):

```json
{ "status": "error", "error": "<message>" }
```

Notes:
- `message`: The message to broadcast (string, required)

# Time Endpoint

POST `/time`

Set the in-game time to a named value or numeric ticks.

Headers:
- `Content-Type: application/json`
- `x-api-key: <API_KEY>` (required)

Request Body (examples):

```json
{ "time": "day" }
```

or

```json
{ "time": "night" }
```

or (ticks):

```json
{ "time": 6000 }
```

Curl example:

```bash
curl -X POST http://YOUR_SERVER:8000/time \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{"time":"day"}'
```

Swift (URLSession) example:

```swift
let url = URL(string: "http://YOUR_SERVER:8000/time")!
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

Response (success):

```json
{ "status": "ok", "executed": "time set day" }
```

Response (error):

```json
{ "status": "error", "error": "<message>" }
```

Notes:
- `time`: Accepts `day`, `night`, or numeric tick values (integer). The server will translate named values to ticks (`day` => 1000, `night` => 13000) when executing.

# Summon API Documentation (v3.4)

## Give Item Endpoint

POST `/give`

Allows giving an item to a player in-game.

Request Body (example):

```json
{
  "player": "WiryHealer4014",
  "item": "diamond_sword",
  "amount": 1
}
```

Response (success):

```json
{ "status": "ok", "executed": "give WiryHealer4014 diamond_sword 1" }
```

Response (error):

```json
{ "status": "error", "error": "<message>" }
```

Notes:
- `player`: The target player's name (string, required)
- `item`: The Minecraft item ID (string, required)
- `amount`: Number of items to give (integer, optional, default 1, max 64)


This document describes the Summon API (revision v3.4), which uses the field names expected by the iOS app.

## Terminology
- **Actor**: the player/account who initiates the action (causes an item to be given or an entity to be spawned). Maps to `summoning_player` in the `/summon` endpoint.
- **Target**: the player who receives the action (the item is given to, or the entity is spawned nearby). Maps to `summoned_player` in the `/summon` endpoint.

## Authentication
All endpoints require an `x-api-key` (or `X-API-Key`) header with the configured API key.

## Immediate Summon Endpoint (game server target)

POST `/summon`

Request Body (example):

```json
{
  "token_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_ip": "10.0.0.19",
  "server_port": 19132,
  "summoned_object_type": "piglin",
  "summoning_player": "ActorPlayer",   // actor — who caused the action
  "summoned_player": "TargetPlayer",   // target — who receives the item / spawn
  "action_type": "Read",
  "minecraft_id": "piglin",
  "entity_summoned": "piglin",
  "timestamp": "2025-12-22T12:00:00Z",
  "gps_lat": 37.7749,
  "gps_lon": -122.4194,
  "client_device_id": "ios-device-123"
}
```

Response (success):

```json
{ "status": "ok", "executed": "...summon command...", "operation_id": "api-op-123" }
```

Response (error):

```json
{ "detail": "<message>", "code": "<optional-code>" }
```

Notes:
- `summoning_player` is the actor; `summoned_player` is the target. The server will execute the command in the appropriate context.

## Command Execution Syntax

The game server executes a Minecraft Bedrock console command using the following pattern when handling a `/summon` request:

```
execute as @a[name=<summoned_player>] at @s run summon <entity> <x> <y> <z>
```

Example (matches user-reported working syntax):

```
execute as @a[name=WiryHealer4014] at @s run summon ender_dragon ~ ~5 ~4
```

The API's `executed` response field will contain the concrete command string that was sent to the server.

## Sync Endpoints (Central API)

The API provides sync endpoints for reliable batch processing of summon operations when immediate execution to game servers is not possible.

### SummonPayload

Fields (JSON keys / types):

- `token_id` (string) — required. UUID or unique token identifier for the NFC token.
- `player_id` (string) — required. The actor (player who caused the action). Trimmed on the client; must be non-empty.
- `summon_type` (string) — required. Non-empty string describing the entity/item type (e.g., "piglin", "give_diamond_sword").
- `summon_time` (string) — required. ISO 8601 UTC timestamp.
- `location` (object) — required. Coordinates with `x`, `y`, `z` (float / number).
- `metadata` (object, required) — structured metadata. Common fields:
  - `custom_name` (string, optional) — max 32 chars
  - `level` (integer, optional) — 1..100

Example SummonPayload:

```json
{
  "token_id": "abc123",
  "player_id": "ActorPlayer",
  "summon_type": "piglin",
  "summon_time": "2025-12-22T15:00:00Z",
  "location": { "x": 100.5, "y": 64.0, "z": -200.0 },
  "metadata": { "custom_name": "Bob", "level": 5 }
}
```

### POST `/api/summon/sync` (single)

- Request: single `SummonPayload` as JSON.
- On success: 200 OK.
- On validation failure: 400 Bad Request with an error description.

### POST `/api/summon/sync/batch` (atomic batch)

- Request body:

```json
{ "summons": [ /* array of SummonPayload objects */ ] }
```

- Atomicity: The batch is all-or-nothing. If any record fails validation or processing, the entire request returns 400 and no records are applied.
- On success: 200 OK.
- On 400: the server MUST return a structured `BatchErrorResponse` describing per-record validation errors.

BatchErrorResponse schema:

```json
{
  "status": "error",
  "errors": [
    { "token_id": "abc123", "field": "player_id", "message": "player_id is required" },
    { "token_id": "def456", "field": "summon_time", "message": "invalid ISO timestamp" }
  ]
}
```

### POST `/summon` (central API immediate)

Alternative to direct game server summon - posts to central API which may forward to configured Minecraft server.

Request body: Same as immediate game server endpoint.

Response: Same as immediate game server endpoint.

## Validation Rules

- `token_id`: non-empty, max 64 chars.
- `player_id`: non-empty, trimmed, max 64 chars.
- `summon_type`: non-empty, trimmed, max 64 chars.
- `summon_time`: valid ISO 8601 UTC timestamp.
- `location`: `x`, `y`, `z` each numeric.
- `metadata`: required object. `custom_name` (max 32 chars) and `level` (int, 1..100) validated if provided.

# Minecraft Server Console Commands Reference

For a comprehensive list of Minecraft Bedrock server console commands, see:

- [bedrock_commands.md](bedrock_commands.md)

This includes commands for player management, server management, and debugging, such as:
- `list` — List all players currently online
- `kick <player>` — Kick a player from the server
- `summon <entity> [x y z]` — Spawn an entity at a specific location
- `give <player> <item> [amount]` — Give an item to a player
- `stop` — Stop the server
- ...and many more

Refer to the linked document for full details, usage, and notes.

Manual give command via console
give WiryHealer4014 diamond_sword 1