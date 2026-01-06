#!/usr/bin/env python3
"""Quick script to check the latest token write."""

import summon_db

# Get the latest token
tokens = summon_db.get_all_tokens(limit=5)

if not tokens:
    print("No tokens found in database")
else:
    print("=" * 70)
    print("LATEST TOKENS")
    print("=" * 70)
    for i, token in enumerate(tokens, 1):
        print(f"\n{i}. Token ID: {token['token_id']}")
        print(f"   Action: {token['action_type']}")
        
        if token.get('entity'):
            print(f"   Entity/Mob: {token['entity']}")
        if token.get('item'):
            print(f"   Item: {token['item']}")
        
        print(f"   GPS Coordinates:")
        print(f"     Latitude:  {token['gps_write_lat']}")
        print(f"     Longitude: {token['gps_write_lon']}")
        print(f"   Written by: {token['written_by']}")
        print(f"   Device ID: {token.get('device_id', 'N/A')}")
        print(f"   Written at: {token['written_at']}")
        
        # Boulder, CO reference: ~40.01°N, 105.27°W
        if token['gps_write_lat'] and token['gps_write_lon']:
            print(f"   Google Maps: https://www.google.com/maps?q={token['gps_write_lat']},{token['gps_write_lon']}")
