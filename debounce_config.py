"""
Debounce Configuration for Summon System

Controls how duplicate summons are handled. Options:
  NEVER: Allow unlimited summons of any mob by any player
  ONCE: Only allow one summon of a specific token ever
  TIME_WINDOW: Only allow one summon per player per mob within a time window

Example configurations:
  # Prevent the same player from summoning the same mob more than once per minute
  DEBOUNCE_MODE = "TIME_WINDOW"
  DEBOUNCE_WINDOW_SECONDS = 60
  
  # Allow each token to be summoned only once ever
  DEBOUNCE_MODE = "ONCE"
  
  # Allow unlimited duplicate summons
  DEBOUNCE_MODE = "NEVER"
"""

import os

# Debounce mode: "NEVER", "ONCE", or "TIME_WINDOW"
DEBOUNCE_MODE = os.getenv('SUMMON_DEBOUNCE_MODE', 'TIME_WINDOW')

# Time window in seconds (only used when DEBOUNCE_MODE is "TIME_WINDOW")
# Common values:
#   60 = 1 minute
#   300 = 5 minutes
#   600 = 10 minutes
#   3600 = 1 hour
#   86400 = 1 day
DEBOUNCE_WINDOW_SECONDS = int(os.getenv('SUMMON_DEBOUNCE_WINDOW_SECONDS', '60'))

# Whether to return error or silently ignore duplicate summons
# True = return 400 error (client knows it was rejected)
# False = return 200 success (client thinks it worked, but we don't record it)
DEBOUNCE_STRICT_MODE = os.getenv('SUMMON_DEBOUNCE_STRICT_MODE', 'true').lower() in ('true', '1', 'yes')

# Validation
VALID_MODES = ['NEVER', 'ONCE', 'TIME_WINDOW']
if DEBOUNCE_MODE not in VALID_MODES:
    raise ValueError(f"Invalid DEBOUNCE_MODE: {DEBOUNCE_MODE}. Must be one of {VALID_MODES}")

if DEBOUNCE_WINDOW_SECONDS < 1:
    raise ValueError(f"DEBOUNCE_WINDOW_SECONDS must be >= 1, got {DEBOUNCE_WINDOW_SECONDS}")


def get_config_summary():
    """Return human-readable config summary."""
    if DEBOUNCE_MODE == 'NEVER':
        return "Debouncing disabled - all summons allowed"
    elif DEBOUNCE_MODE == 'ONCE':
        return "One-time only - each token can only be summoned once ever"
    elif DEBOUNCE_MODE == 'TIME_WINDOW':
        minutes = DEBOUNCE_WINDOW_SECONDS // 60
        seconds = DEBOUNCE_WINDOW_SECONDS % 60
        time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        strict = " (strict mode - returns error)" if DEBOUNCE_STRICT_MODE else " (silent mode - fakes success)"
        return f"Time window - {time_str} per player per mob{strict}"
    return "Unknown mode"


if __name__ == '__main__':
    print("Summon Debounce Configuration")
    print("=" * 50)
    print(f"Mode: {DEBOUNCE_MODE}")
    print(f"Window: {DEBOUNCE_WINDOW_SECONDS} seconds")
    print(f"Strict Mode: {DEBOUNCE_STRICT_MODE}")
    print()
    print(get_config_summary())
