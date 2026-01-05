from utils.mc_send import send_command_to_minecraft

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
    # Build the give command
    give_cmd = f"give {player} {item} {amount}"
    # Send the command to the Minecraft server
    sent = send_command_to_minecraft(give_cmd)
    if not sent:
        return {"status": "error", "error": "Failed to send command to Minecraft server."}
    return {"status": "ok", "executed": give_cmd}
