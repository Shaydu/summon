# Summon API Documentation (v3.4)

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
