from fastapi import HTTPException
from typing import Dict, Any
import uuid
from summon_db import insert_summon

# summon_service.py
"""
Handles all /summon and sync logic for the API (v3.4).
"""

def handle_sync(data: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: Implement sync logic per API spec
    # For now, just echo the data and return a fake operation_id
    operation_id = f"api-sync-{uuid.uuid4().hex[:8]}"
    return {"status": "ok", "synced": data, "operation_id": operation_id}

def handle_sync_batch(data: Any) -> Dict[str, Any]:
    # Accepts {"summons": [ ... ]} per v3.4 spec
    if not isinstance(data, dict) or "summons" not in data or not isinstance(data["summons"], list):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object with a 'summons' array.")
    summons = data["summons"]
    errors = []
    for summon in summons:
        # Minimal validation: check required fields for SummonPayload
        for field in ["token_id", "player_id", "summon_type", "summon_time", "location", "metadata"]:
            if field not in summon or summon[field] in (None, ""):
                errors.append({
                    "token_id": summon.get("token_id", "<unknown>"),
                    "field": field,
                    "message": f"{field} is required"
                })
        # location must be an object with x, y, z
        if "location" in summon and isinstance(summon["location"], dict):
            for coord in ["x", "y", "z"]:
                if coord not in summon["location"] or not isinstance(summon["location"][coord], (int, float)):
                    errors.append({
                        "token_id": summon.get("token_id", "<unknown>"),
                        "field": f"location.{coord}",
                        "message": f"location.{coord} must be a number"
                    })
        else:
            errors.append({
                "token_id": summon.get("token_id", "<unknown>"),
                "field": "location",
                "message": "location must be an object with x, y, z"
            })
        # metadata must be an object
        if "metadata" not in summon or not isinstance(summon["metadata"], dict):
            errors.append({
                "token_id": summon.get("token_id", "<unknown>"),
                "field": "metadata",
                "message": "metadata must be an object"
            })
    if errors:
        return {"status": "error", "errors": errors}
    # If all valid, return success
    operation_id = f"api-sync-batch-{uuid.uuid4().hex[:8]}"
    return {"status": "ok", "operation_id": operation_id}

REQUIRED_FIELDS = [
    "token_id", "server_ip", "server_port", "summoned_object_type",
    "summoning_player", "summoned_player", "action_type", "minecraft_id",
    "entity_summoned", "timestamp", "client_device_id"
]

def handle_summon(data: Dict[str, Any]) -> Dict[str, Any]:
    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    # Store summon request in DB
    insert_summon(
        data["server_ip"],
        data["server_port"],
        data["summoned_object_type"],
        data["summoning_player"],
        data["summoned_player"],
        data["timestamp"],
        data.get("gps_lat"),
        data.get("gps_lon")
    )

    # Build summon command (example, adjust as needed)
    cmd = f"execute as @a[name={data['summoned_player']}] at @s run summon {data['summoned_object_type']} ~ ~ ~2"
    # TODO: Actually send command to Bedrock server if needed

    operation_id = f"api-op-{uuid.uuid4().hex[:8]}"
    response = {
        "status": "ok",
        "executed": cmd,
        "operation_id": operation_id
    }
    return response
