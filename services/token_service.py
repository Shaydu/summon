"""
Token Service - GPS-based token discovery for navigation.

This service provides the /api/tokens/nearby endpoint that enables
ESP32 devices to discover nearby NFC tokens and navigate to them.

Spec: docs/api/api-v3.6.1-proposed.md
"""

from fastapi import APIRouter, HTTPException, Header, Query, Request
from typing import Optional
import math
import summon_db

router = APIRouter()

# Expected API key (should match nfc_api.py)
EXPECTED_API_KEY = "super-secret-test-key22"

# Earth radius in meters (for haversine calculations)
EARTH_RADIUS_M = 6371000


def validate_api_key(x_api_key: str = Header(...)):
    """Validate the API key from request headers."""
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


def parse_action(action: str) -> tuple[str, Optional[str], Optional[str]]:
    """
    Parse action string into (action_type, entity, item).
    
    Examples:
        "sniffer" → ("summon_entity", "sniffer", None)
        "give_diamond_sword" → ("give_item", None, "diamond_sword")
    
    Returns:
        Tuple of (action_type, entity, item)
    """
    if action.startswith("give_"):
        # It's a give_item action
        item_name = action[5:]  # Remove "give_" prefix
        return ("give_item", None, item_name)
    else:
        # It's a summon_entity action
        return ("summon_entity", action, None)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates using Haversine formula.
    
    Args:
        lat1, lon1: Origin coordinates
        lat2, lon2: Destination coordinates
    
    Returns:
        Distance in meters
    
    Formula:
        a = sin²(Δφ/2) + cos φ1 ⋅ cos φ2 ⋅ sin²(Δλ/2)
        c = 2 ⋅ atan2(√a, √(1−a))
        d = R ⋅ c
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = EARTH_RADIUS_M * c
    
    return distance


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the initial bearing from origin to destination.
    
    Args:
        lat1, lon1: Origin coordinates
        lat2, lon2: Destination coordinates
    
    Returns:
        Bearing in degrees (0-360), where:
        - 0° = North
        - 90° = East
        - 180° = South
        - 270° = West
    
    Formula:
        y = sin(Δλ) ⋅ cos(φ2)
        x = cos(φ1) ⋅ sin(φ2) − sin(φ1) ⋅ cos(φ2) ⋅ cos(Δλ)
        θ = atan2(y, x)
        bearing = (θ × 180/π + 360) % 360
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    # Calculate bearing
    y = math.sin(delta_lon) * math.cos(lat2_rad)
    x = (
        math.cos(lat1_rad) * math.sin(lat2_rad) -
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    )
    
    bearing_rad = math.atan2(y, x)
    bearing = (math.degrees(bearing_rad) + 360) % 360
    
    return bearing


@router.post("/api/tokens/register")
async def register_token(
    request: Request,
    x_api_key: str = Header(...)
):
    """
    Register a newly written NFC token in the database.
    
    This endpoint is used when programming/writing NFC tags.
    It stores the token metadata for nearby discovery but does NOT execute game commands.
    
    Required fields:
        - action (string): Mob or item name (e.g., "sniffer", "give_diamond_sword")
        - written_by (string): Player name or device that wrote the token
    
    Optional fields:
        - gps_lat (float): Latitude where token was written (-90 to 90)
        - gps_lon (float): Longitude where token was written (-180 to 180)
        - device_id (string): Device identifier
        - nfc_tag_uid (string): NFC tag hardware UID
        - timestamp (string): ISO8601 timestamp when token was written
    
    Spec: docs/api-v3.6.1.md
    """
    # Validate API key
    validate_api_key(x_api_key)
    
    # Parse request body
    data = await request.json()
    
    # Validate required fields
    if "action" not in data or not data["action"]:
        raise HTTPException(status_code=400, detail={"status": "error", "error": "Missing required field: action"})
    
    if "written_by" not in data or not data["written_by"]:
        raise HTTPException(status_code=400, detail={"status": "error", "error": "Missing required field: written_by"})
    
    action = str(data["action"]).strip()
    written_by = str(data["written_by"]).strip()
    
    if not action:
        raise HTTPException(status_code=400, detail={"status": "error", "error": "Field 'action' cannot be empty"})
    
    if not written_by:
        raise HTTPException(status_code=400, detail={"status": "error", "error": "Field 'written_by' cannot be empty"})
    
    # Validate optional GPS coordinates if provided
    gps_lat = data.get("gps_lat")
    gps_lon = data.get("gps_lon")
    
    if gps_lat is not None:
        try:
            gps_lat = float(gps_lat)
            if gps_lat < -90 or gps_lat > 90:
                raise HTTPException(
                    status_code=400,
                    detail={"status": "error", "error": "Invalid gps_lat: must be between -90 and 90"}
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "error": "Invalid gps_lat: must be a number"}
            )
    
    if gps_lon is not None:
        try:
            gps_lon = float(gps_lon)
            if gps_lon < -180 or gps_lon > 180:
                raise HTTPException(
                    status_code=400,
                    detail={"status": "error", "error": "Invalid gps_lon: must be between -180 and 180"}
                )
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail={"status": "error", "error": "Invalid gps_lon: must be a number"}
            )
    
    # Parse action to determine action_type, entity, item
    action_type, entity, item = parse_action(action)
    
    # Get optional fields
    device_id = data.get("device_id")
    nfc_tag_uid = data.get("nfc_tag_uid")
    timestamp = data.get("timestamp")
    
    try:
        # Insert token into database
        token_id = summon_db.insert_token(
            action_type=action_type,
            entity=entity,
            item=item,
            gps_lat=gps_lat,
            gps_lon=gps_lon,
            written_by=written_by,
            device_id=device_id,
            nfc_tag_uid=nfc_tag_uid,
            written_at=timestamp
        )
        
        print(f"[TOKEN_SERVICE] Registered token {token_id}: action={action}, type={action_type}, entity={entity}, item={item}")
        
        # Build response
        response = {
            "status": "ok",
            "token_id": token_id,
            "action_type": action_type
        }
        
        if entity:
            response["entity"] = entity
        
        if item:
            response["item"] = item
        
        if gps_lat is not None and gps_lon is not None:
            response["gps"] = {
                "lat": gps_lat,
                "lon": gps_lon
            }
        else:
            response["message"] = "Token registered without GPS coordinates"
        
        return response
        
    except Exception as e:
        print(f"[TOKEN_SERVICE] ERROR: Failed to register token: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "error": f"Failed to write token to database: {str(e)}"}
        )


@router.get("/api/tokens/nearby")
async def get_nearby_tokens(
    lat: float = Query(..., ge=-90, le=90, description="Current latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Current longitude"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    radius_km: float = Query(5.0, ge=0.1, le=50.0, description="Search radius in kilometers"),
    action_type: Optional[str] = Query(None, regex="^(summon_entity|give_item|set_time)$"),
    mob_type: Optional[str] = Query(None, regex="^(hostile|neutral|passive)$"),
    x_api_key: str = Header(...),
):
    """
    Find N nearest NFC tokens within radius_km sorted by distance.
    
    Returns token metadata with distance and bearing for navigation.
    
    Spec: docs/api-v3.6.1-proposed.md (updated)
    """
    # Validate API key
    validate_api_key(x_api_key)
    
    try:
        # Query database for N nearest tokens within radius
        tokens = summon_db.get_nearby_tokens(
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            limit=limit,
            action_type=action_type,
            mob_type=mob_type
        )
        
        # Process results: add bearing and format response
        result_tokens = []
        for token in tokens:
            token_lat = token.get('lat')
            token_lon = token.get('lon')
            
            if token_lat is None or token_lon is None:
                continue
            
            # Calculate bearing using Python (more precise than SQL for small distances)
            bearing = calculate_bearing(lat, lon, token_lat, token_lon)
            
            # Build response object based on action type
            token_response = {
                "token_id": str(token['token_id']),
                "action_type": token['action_type'],
                "position": {
                    "lat": token_lat,
                    "lon": token_lon
                },
                "distance_m": round(float(token['distance_m']), 1),
                "bearing": round(bearing, 1),
                "written_by": token.get('written_by'),
                "written_at": token.get('written_at').isoformat() if token.get('written_at') else None
            }
            
            # Add entity-specific fields
            if token['action_type'] == 'summon_entity' and token.get('entity'):
                token_response.update({
                    "entity": token['entity'],
                    "mob_type": token.get('mob_type'),
                    "name": token.get('mob_name', token['entity']),
                    "rarity": token.get('mob_rarity'),
                    "image_url": token.get('mob_image')
                })
            
            # Add item-specific fields
            elif token['action_type'] == 'give_item' and token.get('item'):
                token_response.update({
                    "item": token['item'],
                    "name": token.get('item_name', token['item']),
                    "rarity": token.get('item_rarity'),
                    "image_url": token.get('item_image')
                })
            
            # Add time-specific fields (if we have set_time actions)
            elif token['action_type'] == 'set_time':
                token_response["name"] = "Time Change"
            
            result_tokens.append(token_response)
        
        # Return response
        return {
            "status": "ok",
            "current_position": {
                "lat": lat,
                "lon": lon
            },
            "search_radius_km": radius_km,
            "count": len(result_tokens),
            "tokens": result_tokens
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/api/tokens")
async def get_all_tokens(
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(...)
):
    """
    Get all tokens (for debugging/testing).
    """
    validate_api_key(x_api_key)
    
    try:
        tokens = summon_db.get_all_tokens(limit=limit)
        return {
            "status": "ok",
            "count": len(tokens),
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
