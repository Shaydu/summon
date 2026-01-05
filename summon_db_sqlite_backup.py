def get_summons_by_player(player_name: str):
    """Return summons filtered by summoning_player (case-insensitive), most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon FROM summons WHERE LOWER(summoning_player)=? ORDER BY id DESC",
        (player_name.lower(),)
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result
import sqlite3
from datetime import datetime

DB_PATH = "summon.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS summons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_ip TEXT,
    server_port INTEGER,
    summoned_object_type TEXT,
    summoning_player TEXT,
    summoned_player TEXT,
    timestamp_utc TEXT,
    gps_lat REAL,
    gps_lon REAL
);
"""

CREATE_DEVICE_LOCATIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS device_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    player TEXT,
    gps_lat REAL NOT NULL,
    gps_lon REAL NOT NULL,
    gps_alt REAL,
    gps_speed REAL,
    satellites INTEGER,
    hdop REAL,
    timestamp TEXT NOT NULL,
    CONSTRAINT valid_lat CHECK (gps_lat >= -90 AND gps_lat <= 90),
    CONSTRAINT valid_lon CHECK (gps_lon >= -180 AND gps_lon <= 180)
);
"""

CREATE_DEVICE_LOCATIONS_INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_device_id ON device_locations(device_id);",
    "CREATE INDEX IF NOT EXISTS idx_timestamp ON device_locations(timestamp);"
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    conn.execute(CREATE_DEVICE_LOCATIONS_TABLE_SQL)
    for index_sql in CREATE_DEVICE_LOCATIONS_INDEXES_SQL:
        conn.execute(index_sql)
    conn.commit()
    conn.close()

def insert_summon(
    server_ip, server_port, summoned_object_type,
    summoning_player, summoned_player, timestamp_utc,
    gps_lat=None, gps_lon=None
):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO summons (server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon)
    )
    conn.commit()
    conn.close()

init_db()


def get_all_summons():
    """Return all summons as a list of dicts (most recent first)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon FROM summons ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result


def get_summon_by_id(summon_id):
    """Return a single summon by id as a dict, or None if not found."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon FROM summons WHERE id = ?",
        (summon_id,)
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def get_summons_by_mob(mob_name: str):
    """Return summons filtered by summoned_object_type (case-insensitive), most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon FROM summons WHERE LOWER(summoned_object_type)=? ORDER BY id DESC",
        (mob_name.lower(),)
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result


# ==================== Device Location Functions ====================

def insert_device_location(
    device_id: str,
    gps_lat: float,
    gps_lon: float,
    timestamp: str,
    player: str = None,
    gps_alt: float = None,
    gps_speed: float = None,
    satellites: int = None,
    hdop: float = None
):
    """Insert a device location record."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO device_locations 
        (device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, satellites, hdop, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, satellites, hdop, timestamp)
    )
    conn.commit()
    conn.close()


def get_all_device_locations():
    """Return all device locations as a list of dicts (most recent first)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """SELECT id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp FROM device_locations ORDER BY timestamp DESC"""
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result


def get_device_locations_by_device_id(device_id: str):
    """Return device locations for a specific device_id, most recent first."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """SELECT id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp FROM device_locations 
        WHERE device_id = ? ORDER BY timestamp DESC""",
        (device_id,)
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result


def get_latest_device_locations():
    """Return the most recent location for each unique device_id."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """SELECT id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp FROM device_locations 
        WHERE id IN (
            SELECT MAX(id) FROM device_locations GROUP BY device_id
        ) ORDER BY timestamp DESC"""
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({k: r[k] for k in r.keys()})
    return result
