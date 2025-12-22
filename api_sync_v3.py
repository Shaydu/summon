"""
API Sync v3 Implementation
- Implements /api/summon/sync (single)
- Implements /api/summon/sync/batch (atomic batch)
- Follows api_sync_v3.md spec
"""

from flask import Flask, request, jsonify
from typing import List, Dict, Any
from threading import Lock
import datetime
import re

app = Flask(__name__)

# In-memory DB simulation (replace with real DB in production)
DB = []
DB_LOCK = Lock()

ALLOWED_SUMMON_TYPES = {"zombie", "skeleton", "creeper"}

# --- Validation Helpers ---
def is_iso8601(s: str) -> bool:
    try:
        datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return True
    except Exception:
        return False

def validate_summon(data: Dict[str, Any]) -> List[Dict[str, str]]:
    errors = []
    # Required fields
    if not data.get("token_id") or not isinstance(data["token_id"], str) or len(data["token_id"]) > 64:
        errors.append({"field": "token_id", "message": "token_id is required, string, max 64 chars"})
    if not data.get("player_id") or not isinstance(data["player_id"], str) or len(data["player_id"]) > 64:
        errors.append({"field": "player_id", "message": "player_id is required, string, max 64 chars"})
    if not data.get("summon_type") or data["summon_type"] not in ALLOWED_SUMMON_TYPES:
        errors.append({"field": "summon_type", "message": f"summon_type must be one of: {', '.join(ALLOWED_SUMMON_TYPES)}"})
    if not data.get("summon_time") or not is_iso8601(data["summon_time"]):
        errors.append({"field": "summon_time", "message": "summon_time must be ISO 8601 UTC timestamp"})
    loc = data.get("location")
    if not isinstance(loc, dict) or not all(k in loc for k in ("x", "y", "z")):
        errors.append({"field": "location", "message": "location must be object with x, y, z"})
    # Optional metadata
    meta = data.get("metadata", {})
    if meta:
        if "custom_name" in meta and (not isinstance(meta["custom_name"], str) or len(meta["custom_name"]) > 32):
            errors.append({"field": "metadata.custom_name", "message": "custom_name max 32 chars"})
        if "level" in meta:
            if not isinstance(meta["level"], int) or not (1 <= meta["level"] <= 100):
                errors.append({"field": "metadata.level", "message": "level must be int 1-100"})
    return errors

# --- API Endpoints ---
@app.route("/api/summon/sync", methods=["POST"])
def sync_single():
    data = request.get_json(force=True)
    errors = validate_summon(data)
    if errors:
        return jsonify({"status": "error", "errors": [{"token_id": data.get("token_id", None), **e} for e in errors]}), 400
    with DB_LOCK:
        DB.append(data)
    return jsonify({"status": "success"})

@app.route("/api/summon/sync/batch", methods=["POST"])
def sync_batch():
    req = request.get_json(force=True)
    summons = req.get("summons", [])
    all_errors = []
    for summon in summons:
        errors = validate_summon(summon)
        for e in errors:
            all_errors.append({"token_id": summon.get("token_id", None), **e})
    if all_errors:
        return jsonify({"status": "error", "errors": all_errors}), 400
    with DB_LOCK:
        DB.extend(summons)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
