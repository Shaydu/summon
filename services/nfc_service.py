# nfc_service.py
"""
Handles all /nfc-event logic for the API (v3.4+).
Supports NFC Token v1.1.1 format with GPS coordinates.
"""
from typing import Dict, Any, Optional, Tuple
import summon_db
from datetime import datetime


def parse_token_v1_1_1(data: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse v1.1.1 token format and extract action_type, entity, item.
    
    v1.1.1 format uses an "action" string field:
    - "give_<item_name>" for items (e.g., "give_diamond_sword")
    - "<entity_name>" for mobs (e.g., "zombie", "piglin")
    
    Args:
        data: Token data with "action" field
        
    Returns:
        Tuple of (action_type, entity, item)
    """
    action = data.get("action", "")
    
    if action.startswith("give_"):
        # It's a give_item action
        item_name = action[5:]  # Remove "give_" prefix
        return ("give_item", None, item_name)
    else:
        # It's a summon_entity action
        return ("summon_entity", action, None)


def handle_nfc_event(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process NFC token scan event.
    
    Supports v1.1.1 token format:
    {
      "action": "piglin" or "give_diamond_sword",
      "gps_lat": 40.7580,
      "gps_lon": -105.3009,
      "player": "WiryHealer4014",
      "device_id": "ios-device-123",
      "timestamp": "2026-01-05T12:00:00Z"
    }
    
    Writes token to database for nearby discovery and executes the action.
    """
    # Validate required fields
    if "action" not in data or not data["action"]:
        return {"status": "error", "error": "Missing required field: action"}
    
    if "player" not in data or not data["player"]:
        return {"status": "error", "error": "Missing required field: player"}
    
    # Validate action is not empty after stripping whitespace
    action = str(data["action"]).strip()
    if not action:
        return {"status": "error", "error": "Field 'action' cannot be empty"}
    
    # Parse v1.1.1 token format
    action_type, entity, item = parse_token_v1_1_1(data)
    
    # Additional validation: ensure we have entity or item
    if action_type == "summon_entity" and not entity:
        return {"status": "error", "error": "Invalid action: entity name is empty"}
    
    if action_type == "give_item" and not item:
        return {"status": "error", "error": "Invalid action: item name is empty after 'give_' prefix"}
    
    # Get optional GPS coordinates
    gps_lat = data.get("gps_lat")
    gps_lon = data.get("gps_lon")
    
    # Get other optional fields
    player = data["player"]
    device_id = data.get("device_id")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat() + "Z")
    
    # Write token to database if GPS coordinates present
    token_id = None
    token_write_error = None
    if gps_lat is not None and gps_lon is not None:
        try:
            token_id = summon_db.insert_token(
                action_type=action_type,
                entity=entity,
                item=item,
                gps_lat=gps_lat,
                gps_lon=gps_lon,
                written_by=player,
                device_id=device_id,
                written_at=timestamp
            )
            print(f"[NFC] Successfully wrote token {token_id} at ({gps_lat}, {gps_lon}) - Entity: {entity}, Item: {item}")
        except Exception as e:
            token_write_error = str(e)
            print(f"[NFC] ERROR: Failed to write token: {e}")
            import traceback
            traceback.print_exc()
            # Return error since GPS was provided but token write failed
            return {
                "status": "error",
                "error": f"Failed to write token to database: {token_write_error}",
                "action_type": action_type,
                "entity": entity,
                "item": item
            }
    
    # Execute the action based on type
    response = {"status": "ok", "action_type": action_type}
    
    if action_type == "summon_entity":
        # Execute summon command
        from utils.mc_send import send_command_to_minecraft
        cmd = f"execute as @a[name={player}] at @s run summon {entity} ~ ~5 ~4"
        sent = send_command_to_minecraft(cmd)
        response["executed"] = cmd
        response["sent"] = bool(sent)
        response["entity"] = entity
        
    elif action_type == "give_item":
        # Execute give command
        from utils.mc_send import send_command_to_minecraft
        cmd = f"give {player} {item} 1"
        sent = send_command_to_minecraft(cmd)
        response["executed"] = cmd
        response["sent"] = bool(sent)
        response["item"] = item
    
    if token_id:
        response["token_id"] = token_id
        response["gps"] = {"lat": gps_lat, "lon": gps_lon}
    
    return response
