# Minecraft Summon System API & Sync Specification (v3)

## Overview
This document defines the production-ready API and sync contract for the Minecraft summon system, supporting both single and atomic batch operations. It specifies all endpoints, payloads, validation, error handling, business rules, migration steps, and testing requirements.

---

## Table of Contents
1. API Endpoints
2. Field Definitions & Validation
3. Atomic Batch Sync
4. Sample Payloads
5. Error Handling
6. Migration Checklist
7. Business Rules & Use Cases
8. Testing Requirements

---

## API Endpoints

### 1. Single Summon Sync
- **POST** `/api/summon/sync`
- Sync a single summon record.

#### Request Body
```json
{
  "token_id": "string",           // required, unique identifier
  "player_id": "string",          // required
  "summon_type": "string",        // required, e.g., "zombie", "skeleton"
  "summon_time": "string",        // required, ISO 8601 UTC timestamp
  "location": {                   // required
    "x": "float",
    "y": "float",
    "z": "float"
  },
  "metadata": {                   // optional, object
    "custom_name": "string",
    "level": "integer"
  }
}
```

#### Response
- **200 OK** (success)
- **4xx/5xx** (error, see Error Handling)

---

### 2. Atomic Batch Summon Sync
- **POST** `/api/summon/sync/batch`
- Sync multiple summon records atomically (all succeed or all fail).

#### Request Body
```json
{
  "summons": [
    {
      "token_id": "string",       // required
      "player_id": "string",      // required
      "summon_type": "string",    // required
      "summon_time": "string",    // required, ISO 8601 UTC
      "location": {               // required
        "x": "float",
        "y": "float",
        "z": "float"
      },
      "metadata": {               // optional
        "custom_name": "string",
        "level": "integer"
      }
    }
    // ... more summon objects
  ]
}
```

#### Response
- **200 OK** (all records succeeded)
- **400 Bad Request** (any record failed; see Error Handling)

---

## Field Definitions & Validation
| Field         | Type     | Required | Validation Rules                                 |
|---------------|----------|----------|--------------------------------------------------|
| token_id      | string   | Yes      | Unique, non-empty, max 64 chars                  |
| player_id     | string   | Yes      | Non-empty, max 64 chars                          |
| summon_type   | string   | Yes      | Enum: "zombie", "skeleton", "creeper", etc.      |
| summon_time   | string   | Yes      | ISO 8601 UTC timestamp                           |
| location      | object   | Yes      | x, y, z: float, within world bounds              |
| metadata      | object   | No       | Optional fields: custom_name (string), level (int)|
| custom_name   | string   | No       | Max 32 chars                                     |
| level         | integer  | No       | 1 <= level <= 100                                |

---

## Atomic Batch Sync
- **Atomicity:** All records in a batch must pass validation and be processed successfully. If any record fails, the entire batch is rejected.
- **Error Reporting:** On failure, the response includes the `token_id` and field(s) causing the error for each failed record.

---

## Sample Payloads

### Single Sync Success
```json
  "token_id": "abc123",
  "player_id": "player_1",
  "summon_type": "zombie",
  "summon_time": "2025-12-22T15:00:00Z",
  "location": { "x": 100.5, "y": 64.0, "z": -200.0 },
  "metadata": { "custom_name": "Bob", "level": 5 }
```
**Response:**
```json
{
  "status": "success"
}
```

---

### Batch Sync Success
```json
{
  "summons": [
    {
      "token_id": "abc123",
      "player_id": "player_1",
      "summon_type": "zombie",
      "summon_time": "2025-12-22T15:00:00Z",
      "location": { "x": 100.5, "y": 64.0, "z": -200.0 },
      "metadata": { "custom_name": "Bob", "level": 5 }
    },
    {
      "token_id": "def456",
      "player_id": "player_2",
      "summon_type": "skeleton",
      "summon_time": "2025-12-22T15:01:00Z",
      "location": { "x": 101.0, "y": 64.0, "z": -201.0 }
    }
  ]
}
```
**Response:**
```json
{
  "status": "success"
}
```

---

### Batch Sync Failure
**Request:**
```json
{
  "summons": [
    {
      "token_id": "abc123",
      "player_id": "player_1",
      "summon_type": "zombie",
      "summon_time": "2025-12-22T15:00:00Z",
      "location": { "x": 100.5, "y": 64.0, "z": -200.0 }
    },
    {
      "token_id": "def456",
      "player_id": "",
      "summon_type": "skeleton",
      "summon_time": "2025-12-22T15:01:00Z",
      "location": { "x": 101.0, "y": 64.0, "z": -201.0 }
    }
  ]
}
```
**Response:**
```json
{
  "status": "error",
  "errors": [
    {
      "token_id": "def456",
      "field": "player_id",
      "message": "player_id is required and cannot be empty"
    }
  ]
}
```

---

## Error Handling
- **Single Sync:** Returns 400 with error details if validation fails.
- **Batch Sync:** Returns 400 with an array of errors, each including:
  - `token_id`: The record causing the error
  - `field`: The field with the error
  - `message`: Human-readable error message

**Example:**
```json
{
  "status": "error",
  "errors": [
    {
      "token_id": "ghi789",
      "field": "summon_type",
      "message": "summon_type must be one of: zombie, skeleton, creeper, myname:dewb"
    }
  ]
}
```

---

## Migration Checklist

### API Changes
- [ ] Update all endpoints to use snake_case fields.
- [ ] Implement `/api/summon/sync/batch` with atomicity.
- [ ] Ensure error responses include `token_id` and `field`.

### Database Changes
- [ ] Update all column names to snake_case.
- [ ] Add/validate unique constraint on `token_id`.
- [ ] Ensure all new fields (e.g., `metadata`) are present and nullable as specified.

### Client Changes
- [ ] Update payloads to use snake_case.
- [ ] Handle new error response format.
- [ ] Support batch sync and error reporting.

---

## Business Rules & Use Cases
- Each summon is uniquely identified by `token_id`.
- Summons must be associated with a valid `player_id`.
- Only allowed `summon_type` values are accepted.
- All batch syncs are atomic: partial success is not allowed.
- Summons can include optional metadata (e.g., custom name, level).
- Use cases:
  - Syncing a single summon from client to server.
  - Syncing multiple summons in a single atomic operation.
  - Handling and reporting validation errors for both single and batch syncs.

---

## Testing Requirements
- Validate all required and optional fields.
- Test single and batch sync endpoints for:
  - Success with valid data.
  - Failure with invalid data (missing fields, invalid types, out-of-range values).
  - Atomicity: ensure no partial updates on batch failure.
  - Error response structure and content.
- Test migration scripts for data integrity and backward compatibility.
- Test client integration for new error handling and batch sync support.

---

**End of Specification**
