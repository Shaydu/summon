"""
Debounce Service - Prevents duplicate summons

Implements debouncing logic to prevent duplicate summons based on:
- Player + Mob combination
- Token ID
- Time window
"""

from datetime import datetime, timedelta
import summon_db
from debounce_config import DEBOUNCE_MODE, DEBOUNCE_WINDOW_SECONDS, DEBOUNCE_STRICT_MODE


def check_summon_debounce(
    summoning_player: str,
    summoned_object_type: str,
    token_id: str = None
) -> tuple:
    """
    Check if a summon should be debounced.
    
    Returns:
        (is_duplicate: bool, message: str)
        - is_duplicate=True means this summon should be blocked/skipped
        - message explains why if duplicate
    """
    
    if DEBOUNCE_MODE == 'NEVER':
        return False, None
    
    # Get all recent summons for this player
    try:
        all_player_summons = summon_db.get_summons_by_player(summoning_player)
    except Exception as e:
        print(f"Error checking debounce: {e}")
        return False, None  # On error, allow the summon
    
    if not all_player_summons:
        return False, None  # No previous summons, allow it
    
    # Filter to only this mob type
    recent_summons = [
        s for s in all_player_summons
        if s.get('summoned_object_type', '').lower() == summoned_object_type.lower()
    ]
    
    if not recent_summons:
        return False, None  # No previous summons of this mob, allow it
    
    # Get the most recent summon
    most_recent = recent_summons[0]
    most_recent_timestamp = most_recent.get('timestamp_utc')
    
    if not most_recent_timestamp:
        return False, None
    
    # Parse timestamp
    try:
        if isinstance(most_recent_timestamp, str):
            # Handle ISO format timestamp
            if 'T' in most_recent_timestamp:
                # Remove timezone info for comparison
                most_recent_time = datetime.fromisoformat(
                    most_recent_timestamp.replace('+00:00', '').split('.')[0]
                )
            else:
                most_recent_time = datetime.fromisoformat(most_recent_timestamp)
        else:
            most_recent_time = most_recent_timestamp
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return False, None
    
    now = datetime.utcnow()
    time_since = now - most_recent_time
    
    # Check debounce mode
    if DEBOUNCE_MODE == 'ONCE':
        # Never allow same player to summon same mob twice
        return True, f"Mob '{summoned_object_type}' can only be summoned once per player. Already summoned at {most_recent_timestamp}"
    
    elif DEBOUNCE_MODE == 'TIME_WINDOW':
        # Check if within time window
        if time_since < timedelta(seconds=DEBOUNCE_WINDOW_SECONDS):
            time_remaining = DEBOUNCE_WINDOW_SECONDS - int(time_since.total_seconds())
            return True, f"Please wait {time_remaining}s before summoning '{summoned_object_type}' again (window: {DEBOUNCE_WINDOW_SECONDS}s)"
    
    return False, None


def format_debounce_error(is_duplicate: bool, message: str, strict_mode: bool) -> dict:
    """Format debounce response based on mode."""
    if not is_duplicate:
        return None
    
    if strict_mode:
        # Return error response
        return {
            "status": "error",
            "reason": "duplicate_summon",
            "message": message
        }
    else:
        # Return success response to hide from client
        # (client thinks it worked, but we skip the DB insert)
        return {
            "status": "ok",
            "executed": "[debounced - silent mode]",
            "message": message,
            "debounced": True
        }
