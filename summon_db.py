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

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
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
