# Sync Implementation Summary

## Overview
This document describes the implementation of offline-first NFC operation tracking with automatic synchronization to the API server.

## Architecture

### 1. Core Data Schema Changes
**File**: `summon.xcdatamodeld/summon.xcdatamodel/contents`

Added `syncStatus` field to `NFCOperation` entity:
- **Type**: String
- **Default**: "pending"
- **Values**:
  - `pending`: Operation not yet synced to API
  - `synced`: Successfully synced to API
  - `error`: Failed to sync, will retry

### 2. Data Model (Superset Design)
The implementation uses a **superset approach** where the iOS app tracks more data than required by any single API endpoint. This allows for:
- Complete audit trails
- Flexible API evolution
- Offline operation queue management

**Tracked Fields**:
- `token_id`: UUID of NFC token
- `server_ip` / `server_port`: Target Minecraft server
- `summoned_object_type`: Type of object to summon. This can represent either:
   - a non-player character (NPC), such as an ender dragon, or
   - an item/object to be added to a player's inventory (e.g., diamond_sword).
- `summoning_user`: iOS app username
- `summoned_user`: Target player (for inventory objects, this is the player who will receive the item; for NPCs, this may be the player who triggers the summon or left blank if not player-specific)
- `action_type`: Operation type, e.g., "SummonNPC" or "SummonItem" (or "Read"/"Write")
- `minecraft_id`: Entity/item ID
- `entity_summoned`: For NPCs, the specific entity name/type summoned (e.g., "ender_dragon"). Leave blank for item summons.
- `timestamp`: ISO8601 UTC timestamp
- `gps_lat` / `gps_lon`: GPS coordinates (optional)
- `client_device_id`: iOS device identifier
- `syncStatus`: Sync state tracking

### 3. API Documentation Updates
**File**: `docs/api.md`

Updated `/summon` endpoint to accept comprehensive payload with all tracked fields. The API now receives:
- Full NFC operation context
- User information
- GPS coordinates
- Device tracking information

### 4. Core Components

#### SyncService (`SyncService.swift`)
**Purpose**: Background service for syncing pending operations to API

**Features**:
- Network connectivity monitoring via `NWPathMonitor`
- Automatic sync on connection restore
- Periodic sync timer (every 30 seconds)
- Batch processing of pending operations
- Retry logic with error tracking

**Key Methods**:
- `syncPendingOperations()`: Process all pending operations
- `updatePendingCount()`: Refresh count of pending operations
- `setupNetworkMonitoring()`: Monitor network state changes

#### MinecraftAPIService Updates
**File**: `MinecraftAPIService.swift`

**Changes**:
- Updated `summon()` method to send comprehensive payload
- Added GPS coordinates support
- Added device identifier tracking
- Improved logging for debugging

#### Persistence Layer Updates
**File**: `Persistence.swift`

**New Methods**:
- `fetchPendingSyncOperations()`: Get all operations with pending/error status
- `updateOperationSyncStatus()`: Update sync status of an operation

**Updated Methods**:
- `saveNFCOperation()`: Now accepts `syncStatus` parameter

#### NFCManager Updates
**File**: `NFCManager.swift`

**Changes**:
- All `saveNFCOperation` calls now include `syncStatus`
- Write operations: `syncStatus = "synced"` (no API sync needed)
- Read operations (successful): `syncStatus = "pending"` (needs API sync)
- Read operations (failed validation): `syncStatus = "synced"` (no retry needed)

#### SummonSheet Updates
**File**: `SummonSheet.swift`

**Changes**:
- Integrated SyncService
- On successful summon: save with `syncStatus = "synced"`
- On failed summon: save with `syncStatus = "pending"` for retry
- Update sync service pending count after operations

### 5. App Lifecycle Integration
**File**: `summonApp.swift`

**Changes**:
- Added SyncService to app state
- Inject SyncService into environment
- Initial sync on app launch
- Automatic sync when connectivity returns

## Operation Flow

### Summon Flow (NPCs and Inventory Objects)
1. User scans NFC token
2. Token validated and saved to Core Data with `syncStatus = "pending"`
3. User selects summon type:
   - **Summon NPC**: User specifies an entity (e.g., ender_dragon) to be spawned in the world. `entity_summoned` is set, and `summoned_object_type` describes the NPC type. `summoned_user` may be left blank or set to the triggering player.
   - **Summon Item/Object**: User specifies an item entity_summoned: For NPCs only to be added to a player's inventory. `summoned_object_type` is set to the item (e.g., diamond_sword), and `summoned_user` is the player who will receive the item. `entity_summoned` is left blank.
4. API call attempted:
   - **Success**: Save operation with `syncStatus = "synced"`
   - **Failure**: Save operation with `syncStatus = "pending"`
5. If offline/failed: SyncService will retry when connectivity returns

### Write (Create) Flow
1. User creates new token
2. Token written to NFC chip
3. Operation saved to Core Data with `syncStatus = "synced"`
4. Write operations are local-only (no API sync needed)

### Background Sync Flow
1. SyncService monitors network connectivity
2. When online and pending operations exist:
   - Fetch all pending/error operations
   - Attempt to sync each operation
   - Update status to "synced" on success
   - Update status to "error" on failure (will retry)
3. Periodic timer triggers sync every 30 seconds
4. Manual sync on app launch

## Sync Status State Machine

```
pending ─┬─> synced (API call successful)
         └─> error (API call failed, will retry)

error ───┬─> synced (Retry successful)
         └─> error (Retry failed, will retry again)

synced ──> [terminal state, no further action]
```

## Benefits

1. **Offline-First**: Users can scan/create tokens without connectivity
2. **Automatic Retry**: Failed operations automatically retry when online
3. **Audit Trail**: Complete history of all operations in Core Data
4. **Data Integrity**: No data loss due to network issues
5. **Scalability**: Superset model allows API evolution without app changes
6. **User Feedback**: Users see pending count and sync status

## Testing Recommendations

1. **Offline Mode**: Test scanning with airplane mode enabled
2. **Network Transitions**: Test connectivity loss/restore during operations
3. **Batch Sync**: Create multiple pending operations and verify batch sync
4. **Error Recovery**: Test API errors and verify retry logic
5. **Data Consistency**: Verify Core Data sync status matches actual API state

## Future Enhancements
---

## Compatibility & Migration: iOS, Current API/DB, and Future API/DB

### Field Comparison Table

| Field Name           | iOS Data Model | Current API/DB | Future API/DB | Notes/Action Needed                |
|----------------------|:--------------:|:--------------:|:-------------:|------------------------------------|
| token_id             |      Yes       |      No        |     Yes       | Add to API/DB                      |
| server_ip            |      Yes       |      Yes       |     Yes       |                                    |
| server_port          |      Yes       |      Yes       |     Yes       |                                    |
| summoned_object_type |      Yes       |      Yes       |     Yes       | Used for both NPCs and items       |
| summoning_user       |      Yes       |      Yes       |     Yes       |                                    |
| summoned_user        |      Yes       |      Yes       |     Yes       | For items: recipient; for NPCs: optional |
| action_type          |      Yes       |      No        |     Yes       | Add to API/DB                      |
| minecraft_id         |      Yes       |      No        |     Yes       | Add to API/DB                      |
| entity_summoned      |      Yes       |      No        |     Yes       | Add to API/DB                      |
| timestamp            |      Yes       |      Yes*      |     Yes       | Rename from timestamp_utc          |
| gps_lat/gps_lon      |      Yes       |      Yes       |     Yes       |                                    |
| client_device_id     |      Yes       |      No        |     Yes       | Add to API/DB                      |
| syncStatus           |      Yes       |      No        |     Yes       | Add to API/DB (for audit/troubleshooting) |

*Current API/DB uses timestamp_utc, should be renamed to timestamp.

---

### Required iOS Changes

- iOS must send all new fields (token_id, action_type, minecraft_id, entity_summoned, client_device_id, syncStatus) in the payload.
- iOS should use the new conventions for distinguishing NPC vs. item summons (see tracked fields and operation flow above).
- iOS should expect the API to accept and store all fields in the future.

---

### Required API/DB Changes

- Add missing fields to the DB and API models.
- Rename timestamp_utc to timestamp.
- Ensure the API can distinguish between NPC and item summons using the new field conventions.
- Document which fields are required/optional for each summon type.

---

### Migration Plan

- Migrate existing summon records to the new schema, setting new fields to NULL/default as needed.
- Do not migrate logs/history tables.

---

1. **Exponential Backoff**: Implement progressive retry delays
2. **Conflict Resolution**: Handle server-side conflicts
3. **Selective Sync**: Allow users to choose which operations to sync
4. **Sync Indicators**: Visual feedback for sync progress
5. **Background App Refresh**: Sync even when app is backgrounded
6. **GPS Integration**: Automatically capture GPS coordinates on scan
