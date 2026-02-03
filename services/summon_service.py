from fastapi import HTTPException
from typing import Dict, Any
import uuid
from summon_db import insert_summon, insert_token
from utils.mc_send import send_command_to_minecraft
from debounce_service import check_summon_debounce, format_debounce_error
from debounce_config import DEBOUNCE_STRICT_MODE, get_config_summary

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
        
        # Validate max lengths per v3.6 spec
        if "token_id" in summon and isinstance(summon["token_id"], str) and len(summon["token_id"]) > 64:
            errors.append({
                "token_id": summon.get("token_id", "<unknown>"),
                "field": "token_id",
                "message": "token_id must not exceed 64 characters"
            })
        
        if "player_id" in summon and isinstance(summon["player_id"], str) and len(summon["player_id"].strip()) > 64:
            errors.append({
                "token_id": summon.get("token_id", "<unknown>"),
                "field": "player_id",
                "message": "player_id must not exceed 64 characters"
            })
        
        if "summon_type" in summon and isinstance(summon["summon_type"], str) and len(summon["summon_type"].strip()) > 64:
            errors.append({
                "token_id": summon.get("token_id", "<unknown>"),
                "field": "summon_type",
                "message": "summon_type must not exceed 64 characters"
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
        else:
            # Validate metadata fields per v3.6 spec
            metadata = summon["metadata"]
            if "custom_name" in metadata and isinstance(metadata["custom_name"], str) and len(metadata["custom_name"]) > 32:
                errors.append({
                    "token_id": summon.get("token_id", "<unknown>"),
                    "field": "metadata.custom_name",
                    "message": "custom_name must not exceed 32 characters"
                })
            
            if "level" in metadata:
                try:
                    level = int(metadata["level"])
                    if level < 1 or level > 100:
                        errors.append({
                            "token_id": summon.get("token_id", "<unknown>"),
                            "field": "metadata.level",
                            "message": "level must be between 1 and 100"
                        })
                except (ValueError, TypeError):
                    errors.append({
                        "token_id": summon.get("token_id", "<unknown>"),
                        "field": "metadata.level",
                        "message": "level must be an integer"
                    })
    
    if errors:
        return {"status": "error", "errors": errors}
    # If all valid, return success
    operation_id = f"api-sync-batch-{uuid.uuid4().hex[:8]}"
    return {"status": "ok", "operation_id": operation_id}

REQUIRED_FIELDS = [
    "token_id", "server_ip", "server_port", "summoned_object_type",
    "summoning_player", "summoned_player", "action_type", "minecraft_id",
    "entity_summoned", "timestamp", "client_device_id", "gps_lat", "gps_lon"
]

def handle_summon(data: Dict[str, Any]) -> Dict[str, Any]:
    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")
    
    print(f"DEBUG: Full data received: {data}")
    print(f"DEBUG: entity_summoned = {data.get('entity_summoned')}")
    print(f"DEBUG: minecraft_id = {data.get('minecraft_id')}")
    print(f"DEBUG: summoned_object_type = {data.get('summoned_object_type')}")
    
    # Validate GPS coordinates are within valid ranges
    gps_lat = data.get("gps_lat")
    gps_lon = data.get("gps_lon")
    
    if gps_lat is None or gps_lon is None:
        raise HTTPException(status_code=400, detail="Missing required fields: gps_lat, gps_lon")
    
    try:
        gps_lat = float(gps_lat)
        gps_lon = float(gps_lon)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid GPS coordinates: gps_lat and gps_lon must be valid numbers")
    
    if gps_lat < -90 or gps_lat > 90:
        raise HTTPException(status_code=400, detail="Invalid gps_lat: must be between -90 and 90")
    
    if gps_lon < -180 or gps_lon > 180:
        raise HTTPException(status_code=400, detail="Invalid gps_lon: must be between -180 and 180")

    # Store summon request in DB with GPS coordinates
    insert_summon(
        data["server_ip"],
        data["server_port"],
        data["summoned_object_type"],
        data["summoning_player"],
        data["summoned_player"],
        data["timestamp"],
        gps_lat,
        gps_lon
    )
    
    # Create token for nearby discovery - GPS coordinates are now required
    entity = data.get("entity_summoned") or data.get("minecraft_id") or data.get("summoned_object_type")
    try:
        token_id = insert_token(
            action_type="summon_entity",
            entity=entity,
            gps_lat=gps_lat,
            gps_lon=gps_lon,
            written_by=data["summoning_player"],
            device_id=data.get("device_id"),
            nfc_tag_uid=data.get("nfc_tag_uid"),
            written_at=data["timestamp"]
        )
    except Exception as e:
        # Since GPS is required, token write failure should fail the request
        print(f"ERROR: Failed to create discovery token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store token: {str(e)}")

    # Build summon command using the target player and the entity type fields.
    # Prefer `entity_summoned`, then `minecraft_id`, then `summoned_object_type` as fallbacks.
    entity = data.get("entity_summoned") or data.get("minecraft_id") or data.get("summoned_object_type")
    entity = str(entity).strip()  # Ensure it's a string and remove whitespace
    cmd = f"execute as @a[name={data['summoned_player']}] at @s run summon {entity} ~ ~5 ~4"
    print(f"DEBUG: Building summon command with entity='{entity}', full command: {cmd}")
    # Try to send the command to the running Minecraft server screen session.
    sent = send_command_to_minecraft(cmd)

    operation_id = f"api-op-{uuid.uuid4().hex[:8]}"
    response = {
        "status": "ok",
        "executed": cmd,
        "operation_id": operation_id,
        "sent": bool(sent),
        "token_id": token_id,
        "token_written": True,
        "gps": {
            "lat": gps_lat,
            "lon": gps_lon
        }
    }
    return response
