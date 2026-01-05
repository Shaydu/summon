from utils.mc_send import send_command_to_minecraft
from summon_db import insert_give_operation
from datetime import datetime

def handle_give(data):
    # Validate required fields
    if not isinstance(data, dict):
        return {"status": "error", "error": "Request body must be a JSON object."}
    if "player" not in data or not isinstance(data["player"], str) or not data["player"].strip():
        return {"status": "error", "error": "Missing or invalid 'player' field"}
    
    player = data["player"].strip()
    if len(player) > 64:
        return {"status": "error", "error": "player must not exceed 64 characters"}
    
    if "item" not in data or not isinstance(data["item"], str) or not data["item"].strip():
        return {"status": "error", "error": "Missing or invalid 'item' field"}
    
    item = data["item"].strip()
    if len(item) > 64:
        return {"status": "error", "error": "item must not exceed 64 characters"}
    
    amount = data.get("amount", 1)
    try:
        amount = int(amount)
        if amount < 1 or amount > 64:
            raise ValueError()
    except Exception:
        return {"status": "error", "error": "'amount' must be an integer between 1 and 64"}
    
    # Validate optional GPS coordinates
    gps_lat = data.get("gps_lat")
    gps_lon = data.get("gps_lon")
    
    if gps_lat is not None:
        try:
            gps_lat = float(gps_lat)
            if gps_lat < -90 or gps_lat > 90:
                return {"status": "error", "error": "gps_lat must be between -90 and 90"}
        except (ValueError, TypeError):
            return {"status": "error", "error": "gps_lat must be a number"}
    
    if gps_lon is not None:
        try:
            gps_lon = float(gps_lon)
            if gps_lon < -180 or gps_lon > 180:
                return {"status": "error", "error": "gps_lon must be between -180 and 180"}
        except (ValueError, TypeError):
            return {"status": "error", "error": "gps_lon must be a number"}
    
    # Build the give command
    give_cmd = f"give {player} {item} {amount}"
    
    # Send the command to the Minecraft server
    sent = send_command_to_minecraft(give_cmd)
    if not sent:
        return {"status": "error", "error": "Failed to send command to Minecraft server."}
    
    # Log the operation to database with GPS coordinates if provided
    timestamp = data.get("timestamp", datetime.utcnow().isoformat() + "Z")
    device_id = data.get("device_id")
    
    try:
        insert_give_operation(
            player=player,
            item=item,
            amount=amount,
            timestamp=timestamp,
            gps_lat=gps_lat,
            gps_lon=gps_lon,
            device_id=device_id
        )
    except Exception as e:
        # Log error but don't fail the operation since command was already sent
        print(f"Warning: Failed to log give operation to database: {e}")
    
    return {"status": "ok", "executed": give_cmd}
