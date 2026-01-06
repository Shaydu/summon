#!/usr/bin/env python3
"""Query database directly to check precision."""

import psycopg2
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'summon_db')
DB_USER = os.getenv('DB_USER', 'summon_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'summon_pass123')

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cur = conn.cursor()

print("=" * 80)
print("DIRECT DATABASE QUERY - SUMMONS TABLE")
print("=" * 80)

cur.execute("""
    SELECT id, summoned_object_type, summoning_player,  
           gps_lat, gps_lon, timestamp_utc
    FROM summons 
    WHERE gps_lat IS NOT NULL 
    ORDER BY timestamp_utc DESC 
    LIMIT 3
""")

rows = cur.fetchall()
for row in rows:
    id, mob, player, lat, lon, ts = row
    print(f"\nID: {id}")
    print(f"Mob: {mob}")
    print(f"Player: {player}")
    print(f"Timestamp: {ts}")
    print(f"GPS Lat: {lat} (type: {type(lat).__name__})")
    print(f"GPS Lon: {lon} (type: {type(lon).__name__})")
    print(f"GPS Lat (15 decimals): {lat:.15f}")
    print(f"GPS Lon (15 decimals): {lon:.15f}")

print("\n" + "=" * 80)
print("DIRECT DATABASE QUERY - TOKENS TABLE")
print("=" * 80)

cur.execute("""
    SELECT token_id, entity, written_by,
           gps_write_lat, gps_write_lon, written_at
    FROM tokens 
    WHERE gps_write_lat IS NOT NULL 
    ORDER BY written_at DESC 
    LIMIT 3
""")

rows = cur.fetchall()
for row in rows:
    token_id, entity, written_by, lat, lon, ts = row
    print(f"\nToken ID: {token_id}")
    print(f"Entity: {entity}")
    print(f"Written By: {written_by}")
    print(f"Timestamp: {ts}")
    print(f"GPS Lat: {lat} (type: {type(lat).__name__})")
    print(f"GPS Lon: {lon} (type: {type(lon).__name__})")
    print(f"GPS Lat (15 decimals): {lat:.15f}")
    print(f"GPS Lon (15 decimals): {lon:.15f}")

cur.close()
conn.close()
