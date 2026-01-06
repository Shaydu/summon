#!/usr/bin/env python3
"""Check if recent summons and tokens have GPS coordinates."""

import summon_db

print("=" * 80)
print("RECENT SUMMONS (Last 10)")
print("=" * 80)

summons = summon_db.get_all_summons()
if summons:
    for i, summon in enumerate(summons[:10], 1):
        print(f"\n{i}. {summon.get('summoned_object_type', 'unknown')}")
        print(f"   Player: {summon.get('summoning_player', 'unknown')}")
        print(f"   Timestamp: {summon.get('timestamp_utc', 'unknown')}")
        print(f"   GPS Lat: {summon.get('gps_lat', 'NULL')}")
        print(f"   GPS Lon: {summon.get('gps_lon', 'NULL')}")
        has_gps = summon.get('gps_lat') is not None and summon.get('gps_lon') is not None
        print(f"   Has GPS: {'✅ YES' if has_gps else '❌ NO'}")
else:
    print("No summons found")

print("\n" + "=" * 80)
print("RECENT TOKENS (Last 10)")
print("=" * 80)

tokens = summon_db.get_all_tokens()
if tokens:
    for i, token in enumerate(tokens[:10], 1):
        print(f"\n{i}. Token ID: {token.get('token_id', 'unknown')}")
        print(f"   Action: {token.get('action_type', 'unknown')}")
        print(f"   Entity/Item: {token.get('entity') or token.get('item', 'unknown')}")
        print(f"   GPS Write Lat: {token.get('gps_write_lat', 'NULL')}")
        print(f"   GPS Write Lon: {token.get('gps_write_lon', 'NULL')}")
        has_gps = token.get('gps_write_lat') is not None and token.get('gps_write_lon') is not None
        print(f"   Has GPS: {'✅ YES' if has_gps else '❌ NO'}")
        print(f"   Written By: {token.get('written_by', 'unknown')}")
else:
    print("No tokens found")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

summons_with_gps = sum(1 for s in summons if s.get('gps_lat') is not None and s.get('gps_lon') is not None) if summons else 0
total_summons = len(summons) if summons else 0
print(f"Summons with GPS: {summons_with_gps}/{total_summons}")

tokens_with_gps = sum(1 for t in tokens if t.get('gps_write_lat') is not None and t.get('gps_write_lon') is not None) if tokens else 0
total_tokens = len(tokens) if tokens else 0
print(f"Tokens with GPS: {tokens_with_gps}/{total_tokens}")

if summons_with_gps == 0 and total_summons > 0:
    print("\n⚠️  WARNING: No summons have GPS coordinates!")
if tokens_with_gps == 0 and total_tokens > 0:
    print("⚠️  WARNING: No tokens have GPS coordinates!")
