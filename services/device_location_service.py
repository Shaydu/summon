import logging
from pathlib import Path
from typing import Dict, Any
from summon_db import insert_device_location

# Set up logging
_LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "device_location.log"
_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_logger = logging.getLogger("summon.device_location_service")

if not _logger.handlers:
    fh = logging.FileHandler(_LOG_PATH)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh.setFormatter(formatter)
    _logger.addHandler(fh)
    _logger.setLevel(logging.INFO)


def handle_device_location(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle device location tracking for ESP32 NFC scanners.
    
    Validates and stores GPS position data for display on admin panel map.
    
    Required fields:
    - device_id: string (max 64 chars)
    - gps_lat: number (-90 to 90)
    - gps_lon: number (-180 to 180)
    - timestamp: string (ISO8601)
    
    Optional fields:
    - player: string (max 64 chars)
    - gps_alt: number (altitude in meters)
    - gps_speed: number (speed in km/h)
    - satellites: integer (number of satellites)
    - hdop: number (horizontal dilution of precision)
    """
    _logger.info("Received device location request: %s", repr(data))
    
    # Validate data is a dict
    if not isinstance(data, dict):
        _logger.error("Request body is not a JSON object")
        return {"status": "error", "error": "Request body must be a JSON object"}
    
    # Validate required fields: device_id
    if "device_id" not in data or not isinstance(data["device_id"], str) or not data["device_id"].strip():
        _logger.error("Missing or invalid device_id")
        return {"status": "error", "error": "device_id is required"}
    
    device_id = data["device_id"].strip()
    if len(device_id) > 64:
        _logger.error("device_id exceeds max length: %d", len(device_id))
        return {"status": "error", "error": "device_id must not exceed 64 characters"}
    
    # Validate required fields: gps_lat
    if "gps_lat" not in data:
        _logger.error("Missing gps_lat")
        return {"status": "error", "error": "gps_lat is required"}
    
    try:
        gps_lat = float(data["gps_lat"])
        if gps_lat < -90 or gps_lat > 90:
            _logger.error("Invalid gps_lat: %f (must be between -90 and 90)", gps_lat)
            return {"status": "error", "error": "gps_lat must be between -90 and 90"}
    except (ValueError, TypeError):
        _logger.error("gps_lat is not a valid number: %s", data.get("gps_lat"))
        return {"status": "error", "error": "gps_lat must be a number"}
    
    # Validate required fields: gps_lon
    if "gps_lon" not in data:
        _logger.error("Missing gps_lon")
        return {"status": "error", "error": "gps_lon is required"}
    
    try:
        gps_lon = float(data["gps_lon"])
        if gps_lon < -180 or gps_lon > 180:
            _logger.error("Invalid gps_lon: %f (must be between -180 and 180)", gps_lon)
            return {"status": "error", "error": "gps_lon must be between -180 and 180"}
    except (ValueError, TypeError):
        _logger.error("gps_lon is not a valid number: %s", data.get("gps_lon"))
        return {"status": "error", "error": "gps_lon must be a number"}
    
    # Validate required fields: timestamp
    if "timestamp" not in data or not isinstance(data["timestamp"], str) or not data["timestamp"].strip():
        _logger.error("Missing or invalid timestamp")
        return {"status": "error", "error": "timestamp is required"}
    
    timestamp = data["timestamp"].strip()
    
    # Validate optional field: player
    player = None
    if "player" in data and data["player"]:
        if not isinstance(data["player"], str):
            _logger.error("Invalid player type")
            return {"status": "error", "error": "player must be a string"}
        player = data["player"].strip()
        if len(player) > 64:
            _logger.error("player exceeds max length: %d", len(player))
            return {"status": "error", "error": "player must not exceed 64 characters"}
    
    # Validate optional field: gps_alt
    gps_alt = None
    if "gps_alt" in data and data["gps_alt"] is not None:
        try:
            gps_alt = float(data["gps_alt"])
        except (ValueError, TypeError):
            _logger.error("gps_alt is not a valid number: %s", data.get("gps_alt"))
            return {"status": "error", "error": "gps_alt must be a number"}
    
    # Validate optional field: gps_speed
    gps_speed = None
    if "gps_speed" in data and data["gps_speed"] is not None:
        try:
            gps_speed = float(data["gps_speed"])
        except (ValueError, TypeError):
            _logger.error("gps_speed is not a valid number: %s", data.get("gps_speed"))
            return {"status": "error", "error": "gps_speed must be a number"}
    
    # Validate optional field: satellites
    satellites = None
    if "satellites" in data and data["satellites"] is not None:
        try:
            satellites = int(data["satellites"])
        except (ValueError, TypeError):
            _logger.error("satellites is not a valid integer: %s", data.get("satellites"))
            return {"status": "error", "error": "satellites must be an integer"}
    
    # Validate optional field: hdop
    hdop = None
    if "hdop" in data and data["hdop"] is not None:
        try:
            hdop = float(data["hdop"])
        except (ValueError, TypeError):
            _logger.error("hdop is not a valid number: %s", data.get("hdop"))
            return {"status": "error", "error": "hdop must be a number"}
    
    # Store in database
    try:
        insert_device_location(
            device_id=device_id,
            gps_lat=gps_lat,
            gps_lon=gps_lon,
            timestamp=timestamp,
            player=player,
            gps_alt=gps_alt,
            gps_speed=gps_speed,
            satellites=satellites,
            hdop=hdop
        )
        _logger.info("Device location logged: device_id=%s, lat=%f, lon=%f", device_id, gps_lat, gps_lon)
        return {"status": "ok", "message": "Device location logged"}
    except Exception as e:
        _logger.error("Failed to insert device location: %s", str(e))
        return {"status": "error", "error": f"Failed to log device location: {str(e)}"}
