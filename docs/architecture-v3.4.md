# Architecture Overview (v3.4)

## Goals
- Strictly follow api-v3.4.md spec
- Single Responsibility Principle (SRP): each service handles one domain
- Remove all legacy endpoints and code
- Centralize validation and error handling in utils/

## Directory Structure

```
summon/
├── nfc_api.py           # FastAPI app, routing only
├── services/
│   ├── summon_service.py
│   ├── player_service.py
│   └── nfc_service.py
├── utils/
│   ├── validation.py
│   └── error_handling.py
├── docs/
│   ├── api-v3.4.md
│   └── architecture-v3.4.md
... (other files)
```

## Module Responsibilities

- **nfc_api.py**: FastAPI app, imports and routes to service modules only.
- **services/summon_service.py**: All summon-related endpoints:
  - `POST /summon` — immediate game server execution
  - `POST /api/summon/sync` — single summon sync
  - `POST /api/summon/sync/batch` — batch summon sync
- **services/player_service.py**: All /players logic.
- **services/nfc_service.py**: All /nfc-event logic (legacy endpoint).
- **utils/validation.py**: Shared request/response validation for all payloads.
- **utils/error_handling.py**: Shared error formatting and logging.

## Example Request Flow

1. Request hits nfc_api.py endpoint.
2. Endpoint calls appropriate service function.
3. Service uses utils for validation and error handling.
4. Service returns response to nfc_api.py, which returns to client.

## Notes
- All endpoints and models must match api-v3.4.md.
- No legacy endpoints or code remain.
- Easy to extend and maintain.

---

*Update this doc as the implementation evolves.*
