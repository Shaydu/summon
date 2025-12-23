def handle_chat(data):
    # Validate required fields
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")
    if "message" not in data or not isinstance(data["message"], str) or not data["message"].strip():
        return {"status": "error", "error": "Missing or invalid 'message' field"}
    if "sender" not in data or not isinstance(data["sender"], str) or not data["sender"].strip():
        return {"status": "error", "error": "Missing or invalid 'sender' field"}
    # Simulate sending chat to Minecraft server (replace with actual integration)
    chat_cmd = f'say <{data["sender"]}> {data["message"]}'
    # TODO: Actually send chat_cmd to Bedrock server
    return {"status": "ok", "executed": chat_cmd}
