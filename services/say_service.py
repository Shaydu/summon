import logging
from pathlib import Path
from utils.mc_send import send_command_to_minecraft

# Ensure logs directory exists and configure a file logger for say operations.
_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "say.log"
_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_logger = logging.getLogger("summon.say")
if not _logger.handlers:
    fh = logging.FileHandler(_LOG_PATH)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    _logger.addHandler(fh)
    _logger.setLevel(logging.INFO)


def handle_say(data):
    _logger.info("Received say request: %s", repr(data))
    if not isinstance(data, dict):
        err = "Request body must be a JSON object."
        _logger.error("Say error: %s", err)
        return {"status": "error", "error": err}
    if "message" not in data or not isinstance(data["message"], str) or not data["message"].strip():
        err = "Missing or invalid 'message' field"
        _logger.error("Say error: %s", err)
        return {"status": "error", "error": err}
    say_cmd = f"say {data['message']}"
    sent = send_command_to_minecraft(say_cmd)
    if not sent:
        err = "Failed to send command to Minecraft server."
        _logger.error("Say failed to send command: %s", say_cmd)
        return {"status": "error", "error": err}
    _logger.info("Say executed: %s", say_cmd)
    return {"status": "ok", "executed": say_cmd, "sent": bool(sent)}
