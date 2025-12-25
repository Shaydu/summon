import logging
from pathlib import Path
from typing import Any, Dict

from utils.mc_send import send_command_to_minecraft

# Configure logger
_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "time.log"
_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_logger = logging.getLogger("summon.time")
if not _logger.handlers:
    fh = logging.FileHandler(_LOG_PATH)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    _logger.addHandler(fh)
    _logger.setLevel(logging.INFO)


NAMED_TIMES = {
    "day": "day",
    "night": "night",
}


def handle_time(data: Any) -> Dict[str, Any]:
    _logger.info("Received time request: %s", repr(data))
    if not isinstance(data, dict):
        err = "Request body must be a JSON object."
        _logger.error("Time error: %s", err)
        return {"status": "error", "error": err}

    if "time" not in data:
        err = "Missing 'time' field"
        _logger.error("Time error: %s", err)
        return {"status": "error", "error": err}

    t = data["time"]
    if isinstance(t, str):
        t_lower = t.strip().lower()
        if t_lower not in NAMED_TIMES:
            err = "Invalid named time; allowed: day, night"
            _logger.error("Time error: %s", err)
            return {"status": "error", "error": err}
        value = NAMED_TIMES[t_lower]
    elif isinstance(t, int):
        # tick value
        value = str(t)
    else:
        err = "Invalid 'time' field type"
        _logger.error("Time error: %s", err)
        return {"status": "error", "error": err}

    cmd = f"time set {value}"
    sent = send_command_to_minecraft(cmd)
    if not sent:
        err = "Failed to send command to Minecraft server."
        _logger.error("Time send failed: %s", cmd)
        return {"status": "error", "error": err}

    _logger.info("Time executed: %s", cmd)
    return {"status": "ok", "executed": cmd, "sent": bool(sent)}
