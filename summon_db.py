import sqlite3
from datetime import datetime

DB_PATH = "summon.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS summons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_ip TEXT,
    server_port INTEGER,
    summoned_object_type TEXT,
    summoning_user TEXT,
    summoned_user TEXT,
    timestamp_utc TEXT,
    gps_lat REAL,
    gps_lon REAL
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()

def insert_summon(
    server_ip, server_port, summoned_object_type,
    summoning_user, summoned_user, timestamp_utc,
    gps_lat=None, gps_lon=None
):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO summons (server_ip, server_port, summoned_object_type, summoning_user, summoned_user, timestamp_utc, gps_lat, gps_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (server_ip, server_port, summoned_object_type, summoning_user, summoned_user, timestamp_utc, gps_lat, gps_lon)
    )
    conn.commit()
    conn.close()

init_db()
