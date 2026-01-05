# Summon API Documentation (v3.2)

This document describes the Summon API (revision v3.2). It consolidates all current server contracts, client implementation details, validation rules, batch sync semantics, and NFC operations.

## Terminology
- **Actor**: the player/account who initiates the action (causes an item to be given or an entity to be spawned). Maps to `summoning_user` in the immediate `/summon` endpoint and to `player_id` in v3.2 sync payloads.
- **Target**: the player who receives the action (the item is given to, or the entity is spawned nearby). Maps to `summoned_user` on the immediate `/summon` endpoint. The v3.2 sync payload captures the actor; server-side logic may map to target context when executing.

## Authentication
All endpoints require an `x-api-key` (or `X-API-Key`) header with the configured API key.

## Client Configuration
Default settings (configurable in app):
- `serverIP`: "10.0.0.19"
- `serverPort`: "8000"
- `apiKey`: "super-secret-test-key22"
- `player`: "Player" (actor name)

---

## Immediate Summon Endpoint (game server target)

POST `/summon`

Used by the client to instruct a configured Minecraft server to execute a summon immediately (not part of the sync batch). Fields are accepted as described below.

Request Body (example):

```json
{
  "token_id": "550e8400-e29b-41d4-a716-446655440000",
  "server_ip": "10.0.0.19",
  "server_port": 19132,
  "summoned_object_type": "piglin",
  "summoning_user": "ActorPlayer",   // actor — who caused the action
  "summoned_user": "TargetPlayer",   // target — who receives the item / spawn
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
- `summoning_user` is the actor; `summoned_user` is the target. The server will execute the command in the appropriate context.
- This endpoint is mostly used for immediate on-device summons where the app can talk directly to the server in the token payload.

---

## Sync Endpoints (v3.2)

The API provides a concise sync payload used by the client to reliably record and batch-send scan operations to the server. The server exposes both single and atomic batch sync endpoints.

### SummonPayload (v3.2)

Fields (JSON keys / types):

- `token_id` (string) — required. UUID or unique token identifier for the NFC token.
- `player_id` (string) — required. The actor (player who caused the action). Trimmed on the client; must be non-empty. Client fallbacks to "unknown" if empty.
- `summon_type` (string) — required. Non-empty string describing the entity/item type. Accepts any non-empty type up to 64 chars. The server may validate against known game types.
- `summon_time` (string) — required. ISO 8601 UTC timestamp.
- `location` (object) — required. Coordinates with `x`, `y`, `z` (float / number).
- `metadata` (object, optional) — optional structured metadata. Common fields:
  - `custom_name` (string, optional) — max 32 chars
  - `level` (integer, optional) — 1..100

Example SummonPayload (single):

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
- On 400: the server MUST return a structured `BatchErrorResponse` describing per-record validation errors (see below).

BatchErrorResponse schema (v3.2):

```json
{
  "status": "error",
  "errors": [
    { "token_id": "abc123", "field": "player_id", "message": "player_id is required" },
    { "token_id": "def456", "field": "summon_time", "message": "invalid ISO timestamp" }
  ]
}
```

Behavior for clients (recommended):
- If the server returns a `BatchErrorResponse`, the client should map each `token_id` back to its local operation record and surface or record the per-record message.
- Unreferenced operations in the batch should be marked with a generic batch failure message.

---

## Validation Rules (server-side canonical)
- `token_id`: non-empty, max 64 chars.
- `player_id`: non-empty, trimmed, max 64 chars. Clients must not send empty strings; client implementations trim and fallback to a sentinel (`unknown`) when necessary.
- `summon_type`: non-empty, trimmed, max 64 chars. Accepts the full universe of entity/item names; server-side may validate against known values.
- `summon_time`: valid ISO 8601 UTC timestamp.
- `location`: `x`, `y`, `z` each numeric, within server world bounds if applicable.
- `metadata.custom_name`: optional, max 32 chars.
- `metadata.level`: optional int, 1..100.

---

## Client-side guarantees and behavior (v3.2)

### Player/Actor Handling
- The iOS client trims `player` input and persists it in UserDefaults as `player`
- When creating sync payloads, the client ensures `player_id` is not empty (trim + fallback to "unknown")
- Core Data stores this value in the `username` field

### Summon Type Validation
- The client no longer restricts `summon_type` to a small whitelist
- Any non-empty type is accepted (length limits apply: max 64 chars)
- Server-side may validate against known Minecraft entity/item types

### Batch Sync Behavior
- Client collects pending `NFCOperation` records (syncStatus = "pending" or "error")
- Only **Read operations** are synced; Write operations are marked "synced" immediately (no API call)
- Client pre-validates all payloads before posting to `/api/summon/sync/batch`
- Posts operations sorted by `createdAt` (oldest first)
- Automatic sync every 30 seconds when online and pending operations exist
- Network reconnection triggers immediate sync attempt

### Batch Error Handling
- If server returns `BatchErrorResponse` (400), client maps errors back to local operations
- For each error entry: updates corresponding `NFCOperation.syncStatus` = "error" with server message
- Operations not referenced in `errors` array receive generic batch error message
- Failed operations retain "error" status and will retry on next sync cycle

### NFC Operations

#### NFC Read (Tag Scanning)
- Prevents concurrent read/write operations
- Uses NFCNDEFReaderSession with invalidateAfterFirstRead
- Parses NFCToken structure from NDEF payload
- Validates required fields (tokenId, player, action, server, port, timestamp)
- Saves to Core Data with syncStatus = "pending" and GPS coordinates
- Provides audio/haptic feedback on success/error

#### NFC Write (Tag Creation)
- Prevents concurrent read/write operations
- Uses NFCTagReaderSession for write capability
- Checks tag queryNDEFStatus and capacity before writing
- **REPLACES entire NDEF message** on the tag (not append)
- Writes NFCToken JSON structure as NDEF record
- Saves to Core Data with syncStatus = "synced" (no API sync needed)
- Provides audio/haptic feedback on success/error

### Location & Coordinates
- GPS coordinates captured at scan/create time (latitude, longitude)
- Minecraft coordinates default to y=64.0 (ground level) in sync payloads
- GPS data included in payloads only if non-zero

### Device Identification
- Optional `client_device_id` field uses UIDevice.identifierForVendor (UUID)
- Included in immediate `/summon` requests for tracking
- Helps server identify client device for analytics

### Caching Strategy
- Player list (/users endpoint) cached for 5 minutes
- Reduces redundant API calls during active sessions

---

## Examples

Batch success example request:

```json
{
  "summons": [
    {
      "token_id": "abc123",
      "player_id": "ActorOne",
      "summon_type": "zombie",
      "summon_time": "2025-12-22T15:00:00Z",
      "location": { "x": 100.5, "y": 64.0, "z": -200.0 }
    },
    {
      "token_id": "def456",
      "player_id": "ActorTwo",
      "summon_type": "skeleton",
      "summon_time": "2025-12-22T15:01:00Z",
      "location": { "x": 101.0, "y": 64.0, "z": -201.0 }
    }
  ]
}
```

Batch failure example (server returns per-token errors):

```json
{
  "status": "error",
  "errors": [
    { "token_id": "def456", "field": "player_id", "message": "player_id is required and cannot be blank" }
  ]
}
```

Client mapping note: the client maps `token_id` back to its local `NFCOperation.tokenId` and updates `syncStatus`/`errorMessage` accordingly.

---

## Data Structures

### Core Data Models (iOS Client)

#### NFCOperation
Stores NFC read/write operations for sync tracking:
```
- id: UUID
- createdAt: Date
- actionType: String ("Read" or "Write")
- success: Boolean
- data: String (JSON payload)
- tokenId: String (optional)
- minecraftId: String (optional)
- entitySummoned: String (optional)
- server: String (optional)
- port: Int32 (optional)
- username: String (optional) — actor/player field
- latitude: Double
- longitude: Double
- errorMessage: String (optional)
- syncStatus: String ("pending", "synced", "error")
```

#### SummonEntity
Stores created summons (Write operations):
```
- id: UUID
- createdAt: Date
- tokenId: String
- kind: String ("item" or "character")
- minecraftId: String (e.g., "piglin", "diamond_sword")
- createdBy: String
- serverURL: String
- placementPlayerID: String
- position: String (Minecraft coords)
- handItems: String (optional, JSON)
- latitude: Double
- longitude: Double
```

### NFCToken Structure
Written to NFC tags via NDEF encoding:
```json
{
  "tokenId": "uuid-string",
  "player": "ActorName",
  "action": "action-type",
  "server": "server-ip",
  "port": 19132,
  "timestamp": "2025-12-22T12:00:00Z"
}
```

Validation:
- `tokenId`, `player`, `action`, `server`: required, non-empty
- `port`: 1-65535
- `timestamp`: ISO8601 UTC format

---

## Implementation Notes

### Entity Summoned Logic
- Only added for character/NPC actions (not items)
- Excluded for commands with `give_` prefix
- Based on `minecraftId` in immediate `/summon` endpoint

---

## Testing Requirements

### Unit Tests
- Validate `validateSummonPayload` for all field types and edge cases
- Test empty/trimming behavior for `player_id`
- Test various `summon_type` strings (no whitelist restriction)
- Test timestamp parsing (ISO8601 format)
- Test metadata limits (custom_name max 32 chars, level 1-100)

### Integration Tests
- Test `syncBatchSummons` decoding `BatchErrorResponse`
- Verify error mapping back to local `NFCOperation` records
- Test batch atomicity (all succeed or all fail)
- Test unreferenced token handling in batch errors

### End-to-End Tests
- Run server locally and post representative batch requests
- Verify 200 success response and local record updates
- Verify 400 error response with structured `errors` array
- Confirm client updates `NFCOperation.syncStatus` correctly
- Test automatic retry on network reconnection

### NFC Operation Tests
- Test NFC read with valid/invalid NDEF payloads
- Test NFC write capacity and writeability checks
- Verify NDEF message replacement behavior
- Test concurrent operation prevention
- Verify audio/haptic feedback on success/error

---

## Appendix A: Complete Flow Examples

### Example 1: NFC Tag Creation (Write)
1. User taps "Create New Tag" in app
2. User selects entity type (e.g., "piglin") and configures metadata
3. User taps physical NFC tag to write
4. App checks tag capacity and writeability
5. App creates NFCToken JSON payload with current settings
6. App **replaces** tag's NDEF message with new payload
7. App saves SummonEntity to Core Data
8. App creates NFCOperation with syncStatus = "synced" (no API call)
9. Success feedback provided to user

### Example 2: NFC Tag Scan (Read) with Online Sync
1. User sets `Player` name in settings → saved to UserDefaults
2. User scans NFC tag with device
3. App parses NFCToken from NDEF payload
4. App validates token structure (required fields)
5. App saves NFCOperation with username = settings.player, syncStatus = "pending"
6. SyncService collects pending Read operations
7. Client constructs SummonPayload with player_id = trimmed username (or "unknown")
8. Client pre-validates all payloads
9. Client POSTs `{ "summons": [...] }` to `/api/summon/sync/batch`
10. Server responds 200 → client marks operations syncStatus = "synced"

### Example 3: Batch Sync with Validation Error
1. Client has 3 pending Read operations
2. Client constructs 3 SummonPayload objects
3. One payload has empty player_id due to missing username
4. Client POSTs batch to `/api/summon/sync/batch`
5. Server validates and finds player_id violation
6. Server responds 400 with BatchErrorResponse:
```json
{
  "status": "error",
  "errors": [
    { "token_id": "abc123", "field": "player_id", "message": "player_id is required" }
  ]
}
```
7. Client parses response and maps token_id to local NFCOperation
8. Client sets operation.syncStatus = "error", operation.errorMessage = server message
9. Other 2 operations in batch get generic error message
10. All 3 operations remain in error/pending state for next sync cycle

### Example 4: Immediate Summon (Direct to Game Server)
1. User scans NFC tag containing server info
2. App reads token and extracts server_ip, server_port
3. App constructs full payload with GPS, device ID, entity metadata
4. App adds entity_summoned field (only if not a `give_` command)
5. App POSTs to `http://{server_ip}:{server_port}/summon`
6. Server executes Minecraft command immediately
7. Server responds with executed command and operation_id
8. App displays success to user

---

## Appendix B: Error Code Reference

### HTTP Status Codes
- **200 OK**: Successful operation (sync or immediate summon)
- **400 Bad Request**: Validation error (see BatchErrorResponse for details)
- **401 Unauthorized**: Invalid or missing API key
- **4xx/5xx**: Other HTTP errors (network, server issues)

### NFC Error Codes (iOS)
- **200**: User cancelled operation
- **201**: Session timeout (60 seconds)
- **203**: First NDEF read (system behavior, can be ignored)

### Validation Errors
- `missing(field)`: Required field is empty or not provided
- `invalid(field)`: Field value doesn't match expected format/range
- `invalidPort`: Port number outside 1-65535 range
- `invalidTimestamp`: Timestamp not in ISO8601 UTC format

### Sync Errors
- `missingRequiredFields`: Payload missing required data
- `invalidURL`: Server URL malformed
- `invalidResponse`: Server response not parseable
- `httpError(code)`: HTTP status code error

---

## Contact
For questions about the API, to request changes to allowed `summon_type` values, or to report issues, contact the API maintainer.

