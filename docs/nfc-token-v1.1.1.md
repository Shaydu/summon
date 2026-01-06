# NFC Token v1.1.1 Format Support

**Status**: ✅ Implemented  
**Date**: January 5, 2026  
**API Version**: v3.6+

## Overview

The system now supports **NFC Token v1.1.1 format** with GPS coordinates. This format is backward-compatible with existing iOS/Arduino NFC token writers while adding location tracking for nearby token discovery.

## Token Format v1.1.1

### Structure

```json
{
  "action": "<action_string>",
  "player": "<player_name>",
  "gps_lat": <latitude>,
  "gps_lon": <longitude>,
  "device_id": "<device_identifier>",
  "timestamp": "<ISO8601_timestamp>"
}
```

### Action Field Format

**For Items** (give commands):
- Format: `"give_<item_name>"`
- Examples: `"give_diamond_sword"`, `"give_emerald"`, `"give_iron_pickaxe"`

**For Entities** (summon commands):
- Format: `"<entity_name>"`  (no prefix)
- Examples: `"zombie"`, `"piglin"`, `"creeper"`, `"ender_dragon"`

### GPS Coordinates (v1.1.1 Addition)

- `gps_lat`: Latitude where token was written (-90 to 90)
- `gps_lon`: Longitude where token was written (-180 to 180)
- **Optional**: Tokens work without GPS (legacy mode)
- **Purpose**: Enable nearby token discovery and navigation

## Examples

### Example 1: Summon Entity with GPS

```json
{
  "action": "piglin",
  "player": "WiryHealer4014",
  "gps_lat": 40.0150,
  "gps_lon": -105.2705,
  "device_id": "ios-device-123",
  "timestamp": "2026-01-05T12:00:00Z"
}
```

**Result**:
- Executes: `execute as @a[name=WiryHealer4014] at @s run summon piglin ~ ~5 ~4`
- Writes token to database with GPS coordinates
- Token appears in `/api/tokens/nearby` queries

### Example 2: Give Item with GPS

```json
{
  "action": "give_diamond_sword",
  "player": "WiryHealer4014",
  "gps_lat": 40.0151,
  "gps_lon": -105.2706,
  "device_id": "ios-device-123",
  "timestamp": "2026-01-05T12:01:00Z"
}
```

**Result**:
- Executes: `give WiryHealer4014 diamond_sword 1`
- Writes token to database with GPS coordinates
- Token appears in `/api/tokens/nearby` queries

### Example 3: Legacy Token (No GPS)

```json
{
  "action": "zombie",
  "player": "TestPlayer",
  "timestamp": "2026-01-05T12:00:00Z"
}
```

**Result**:
- Executes: `execute as @a[name=TestPlayer] at @s run summon zombie ~ ~5 ~4`
- No token written to database (no GPS)
- Works exactly like pre-v1.1.1 tokens

## API Endpoints

### POST `/api/v1.1.1/nfc-event` (Recommended)

**Version-specific endpoint for NFC Token v1.1.1 format.**

**Headers**:
- `x-api-key: <API_KEY>` (required)
- `Content-Type: application/json`

**Request Body**: See token format above

**Response** (with GPS):
```json
{
  "status": "ok",
  "action_type": "summon_entity",
  "entity": "piglin",
  "executed": "execute as @a[name=WiryHealer4014] at @s run summon piglin ~ ~5 ~4",
  "sent": true,
  "token_id": "a1b2c3d4-e5f6-4789-a012-3456789abcde",
  "gps": {
    "lat": 40.0150,
    "lon": -105.2705
  }
}
```

**Response** (without GPS):
```json
{
  "status": "ok",
  "action_type": "summon_entity",
  "entity": "zombie",
  "executed": "execute as @a[name=TestPlayer] at @s run summon zombie ~ ~5 ~4",
  "sent": true
}
```

### POST `/nfc-event` (Legacy)

**Legacy endpoint - automatically uses v1.1.1 format.**

Same behavior as `/api/v1.1.1/nfc-event`. Provided for backward compatibility with existing clients.

## Database Storage

When GPS coordinates are present, tokens are written to the `tokens` table:

```sql
INSERT INTO tokens (
  action_type,     -- 'summon_entity' or 'give_item'
  entity,          -- 'piglin' (for summons, NULL for items)
  item,            -- 'diamond_sword' (for items, NULL for summons)
  gps_write_lat,   -- 40.0150
  gps_write_lon,   -- -105.2705
  written_by,      -- 'WiryHealer4014'
  device_id,       -- 'ios-device-123'
  written_at       -- '2026-01-05T12:00:00Z'
) VALUES ...;
```

## Nearby Token Discovery

Tokens with GPS coordinates can be queried using:

```bash
GET /api/tokens/nearby?lat=40.0150&lon=-105.2705&limit=10
```

Returns tokens sorted by distance with navigation data (distance, bearing).

See [api-v3.6.1.md](api-v3.6.1.md) for full nearby tokens API documentation.

## Implementation Details

### Token Parsing

The `parse_token_v1_1_1()` function in `services/nfc_service.py` converts the v1.1.1 format to internal format:

```python
def parse_token_v1_1_1(data: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[str]]:
    action = data.get("action", "")
    
    if action.startswith("give_"):
        item_name = action[5:]  # Remove "give_" prefix
        return ("give_item", None, item_name)
    else:
        return ("summon_entity", action, None)
```

### Backward Compatibility

✅ **Full backward compatibility maintained**:
- Old tokens without GPS continue to work
- No changes required to existing token writers
- GPS coordinates are optional enhancements

## Testing

Run the test suite:

```bash
# Test NFC service parsing
python -m pytest tests/test_nfc_v1_1_1.py -v

# Test end-to-end with API server
./test_nfc_v1_1_1.sh
```

## iOS Client Updates

### Writing v1.1.1 Tokens with GPS

```swift
// Get current location
guard let location = locationManager.location else {
    print("No GPS location available")
    return
}

// Build token data
let tokenData: [String: Any] = [
    "action": action,  // "piglin" or "give_diamond_sword"
    "player": playerName,
    "gps_lat": location.coordinate.latitude,
    "gps_lon": location.coordinate.longitude,
    "device_id": UIDevice.current.identifierForVendor?.uuidString ?? "unknown",
    "timestamp": ISO8601DateFormatter().string(from: Date())
]

// Encode to JSON
let jsonData = try JSONSerialization.data(withJSONObject: tokenData)

// Write to NFC tag
let payload = NFCNDEFPayload(
    format: .nfcWellKnown,
    type: "T".data(using: .utf8)!,
    identifier: Data(),
    payload: jsonData
)
```

### Scanning v1.1.1 Tokens

Scanning works exactly the same as before - the API handles parsing automatically.

## Arduino/ESP32 Client Updates

### Writing v1.1.1 Tokens with GPS

```cpp
// Get GPS coordinates from GPS module
if (gps.location.isValid()) {
  float lat = gps.location.lat();
  float lon = gps.location.lng();
  
  // Build token JSON
  StaticJsonDocument<256> doc;
  doc["action"] = "piglin";  // or "give_diamond_sword"
  doc["player"] = playerName;
  doc["gps_lat"] = lat;
  doc["gps_lon"] = lon;
  doc["device_id"] = "esp32-001";
  doc["timestamp"] = getCurrentTimestamp();
  
  // Serialize and write to NFC
  String jsonStr;
  serializeJson(doc, jsonStr);
  nfc.writeNdefMessage(jsonStr);
}
```

## Migration from v1.0/v1.1

**No migration needed!** v1.1.1 is backward compatible:

- Tokens without GPS fields work exactly as before
- Add GPS fields to enable nearby discovery feature
- Update at your own pace - both formats work simultaneously

## Related Documentation

- [api-v3.6.1.md](api-v3.6.1.md) - Complete API v3.6.1 documentation
- [nfc/README.md](../nfc/README.md) - NFC token documentation
- [POSTGRES_MIGRATION.md](../POSTGRES_MIGRATION.md) - Database schema

## Changelog

### v1.1.1 (January 5, 2026)
- Added GPS coordinate support (`gps_lat`, `gps_lon`)
- Tokens with GPS are written to database for nearby discovery
- Tokens without GPS work in legacy mode (execute only)
- Full backward compatibility with v1.0/v1.1

### v1.1 (Previous)
- Original token format with `action` string field
- Support for give and summon actions
- No GPS tracking

### v1.0 (Original)
- Initial NFC token implementation
