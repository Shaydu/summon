from utils.mc_send import send_command_to_minecraft

def handle_say(data):
    if not isinstance(data, dict):
        return {"status": "error", "error": "Request body must be a JSON object."}
    if "message" not in data or not isinstance(data["message"], str) or not data["message"].strip():
        return {"status": "error", "error": "Missing or invalid 'message' field"}
    say_cmd = f"say {data['message']}"
    sent = send_command_to_minecraft(say_cmd)
    if not sent:
        return {"status": "error", "error": "Failed to send command to Minecraft server."}
    return {"status": "ok", "executed": say_cmd}
