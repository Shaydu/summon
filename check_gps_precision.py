#!/usr/bin/env python3
"""Check exact GPS precision stored in database."""

import summon_db

print("=" * 80)
print("CHECKING GPS COORDINATE PRECISION")
print("=" * 80)

summons = summon_db.get_all_summons()

if summons:
    latest = summons[0]
    print(f"\nLatest Summon:")
    print(f"  Mob: {latest.get('summoned_object_type')}")
    print(f"  Player: {latest.get('summoning_player')}")
    print(f"  Timestamp: {latest.get('timestamp_utc')}")
    print(f"\n  GPS Lat (raw): {repr(latest.get('gps_lat'))}")
    print(f"  GPS Lon (raw): {repr(latest.get('gps_lon'))}")
    
    if latest.get('gps_lat') and latest.get('gps_lon'):
        # Show full precision
        lat = latest.get('gps_lat')
        lon = latest.get('gps_lon')
        print(f"\n  GPS Lat (full): {lat:.10f}")
        print(f"  GPS Lon (full): {lon:.10f}")
        
        # Count decimal places
        lat_str = f"{lat:.10f}".rstrip('0').rstrip('.')
        lon_str = f"{lon:.10f}".rstrip('0').rstrip('.')
        lat_decimals = len(lat_str.split('.')[-1]) if '.' in lat_str else 0
        lon_decimals = len(lon_str.split('.')[-1]) if '.' in lon_str else 0
        
        print(f"\n  Lat decimal places: {lat_decimals}")
        print(f"  Lon decimal places: {lon_decimals}")
        
        if lat_decimals >= 6 and lon_decimals >= 6:
            print(f"\n  ✅ GPS precision: PASS (≥6 decimals)")
        else:
            print(f"\n  ❌ GPS precision: FAIL (<6 decimals)")

tokens = summon_db.get_all_tokens()
if tokens and tokens[0].get('gps_write_lat'):
    latest_token = tokens[0]
    print(f"\n" + "=" * 80)
    print("Latest Token:")
    print(f"  Entity: {latest_token.get('entity')}")
    print(f"  Written By: {latest_token.get('written_by')}")
    print(f"\n  GPS Write Lat (raw): {repr(latest_token.get('gps_write_lat'))}")
    print(f"  GPS Write Lon (raw): {repr(latest_token.get('gps_write_lon'))}")
    
    lat = latest_token.get('gps_write_lat')
    lon = latest_token.get('gps_write_lon')
    print(f"\n  GPS Write Lat (full): {lat:.10f}")
    print(f"  GPS Write Lon (full): {lon:.10f}")
