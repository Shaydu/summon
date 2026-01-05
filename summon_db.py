import psycopg2
import psycopg2.extras
from datetime import datetime
import os

# PostgreSQL connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'summon_db')
DB_USER = os.getenv('DB_USER', 'summon_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'summon_pass123')

def get_connection():
    """Get a PostgreSQL database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    """Initialize database - tables should already exist."""
    pass  # Tables are created via SQL schema file

def insert_summon(
    server_ip, server_port, summoned_object_type,
    summoning_player, summoned_player, timestamp_utc,
    gps_lat=None, gps_lon=None
):
    """Insert a summon record."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO summons 
        (server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (server_ip, server_port, summoned_object_type, summoning_player, summoned_player, timestamp_utc, gps_lat, gps_lon)
    )
    conn.commit()
    cur.close()
    conn.close()



def get_all_summons():
    """Return all summons as a list of dicts (most recent first)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, 
        timestamp_utc, gps_lat, gps_lon FROM summons ORDER BY id DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_summon_by_id(summon_id):
    """Return a single summon by id as a dict, or None if not found."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, 
        timestamp_utc, gps_lat, gps_lon FROM summons WHERE id = %s""",
        (summon_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_summons_by_mob(mob_name: str):
    """Return summons filtered by summoned_object_type (case-insensitive), most recent first."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, 
        timestamp_utc, gps_lat, gps_lon FROM summons 
        WHERE LOWER(summoned_object_type) = LOWER(%s) ORDER BY id DESC""",
        (mob_name,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_summons_by_player(player_name: str):
    """Return summons filtered by summoning_player (case-insensitive), most recent first."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, server_ip, server_port, summoned_object_type, summoning_player, summoned_player, 
        timestamp_utc, gps_lat, gps_lon FROM summons 
        WHERE LOWER(summoning_player) = LOWER(%s) ORDER BY id DESC""",
        (player_name,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO device_locations 
        (device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, satellites, hdop, timestamp) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, satellites, hdop, timestamp)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_device_locations():
    """Return all device locations as a list of dicts (most recent first)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp FROM device_locations ORDER BY timestamp DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_device_locations_by_device_id(device_id: str):
    """Return device locations for a specific device_id, most recent first."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp FROM device_locations 
        WHERE device_id = %s ORDER BY timestamp DESC""",
        (device_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_device_locations():
    """Return the most recent location for each unique device_id."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT DISTINCT ON (device_id) 
        id, device_id, player, gps_lat, gps_lon, gps_alt, gps_speed, 
        satellites, hdop, timestamp 
        FROM device_locations 
        ORDER BY device_id, timestamp DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

# ==================== Game Objects Functions ====================

def get_all_mobs():
    """Return all mobs from the game objects database."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT mob_id, name, description, mob_type, minecraft_id, health, damage, armor,
        rarity, biome, difficulty_rating, image_url FROM mobs ORDER BY name"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def get_mob_by_minecraft_id(minecraft_id: str):
    """Get mob metadata by minecraft_id."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT mob_id, name, description, mob_type, minecraft_id, health, damage, armor,
        rarity, biome, difficulty_rating, image_url FROM mobs 
        WHERE minecraft_id = %s""",
        (minecraft_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def get_all_items():
    """Return all items from the game objects database."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT item_id, name, description, item_category, minecraft_id, max_stack_size,
        durability, damage, rarity, is_craftable, value, image_url FROM items ORDER BY name"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def get_item_by_minecraft_id(minecraft_id: str):
    """Get item metadata by minecraft_id."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT item_id, name, description, item_category, minecraft_id, max_stack_size,
        durability, damage, rarity, is_craftable, value, image_url FROM items 
        WHERE minecraft_id = %s""",
        (minecraft_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def get_all_actions():
    """Return all actions from the game objects database."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT action_id, action_type, name, description, category, rarity, 
        requires_op, cooldown_seconds FROM actions ORDER BY name"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

# ==================== Give Operation Logging ====================

def insert_give_operation(
    player: str,
    item: str,
    amount: int,
    timestamp: str,
    gps_lat: float = None,
    gps_lon: float = None,
    device_id: str = None
):
    """Log a give operation (item given to player) with optional GPS coordinates."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Create table if it doesn't exist (for backwards compatibility)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS give_operations (
            id SERIAL PRIMARY KEY,
            player VARCHAR(64) NOT NULL,
            item VARCHAR(64) NOT NULL,
            amount INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            gps_lat DOUBLE PRECISION,
            gps_lon DOUBLE PRECISION,
            device_id VARCHAR(64),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute(
        """INSERT INTO give_operations 
        (player, item, amount, timestamp, gps_lat, gps_lon, device_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (player, item, amount, timestamp, gps_lat, gps_lon, device_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_give_operations():
    """Return all give operations (most recent first)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT id, player, item, amount, timestamp, gps_lat, gps_lon, 
        device_id, created_at FROM give_operations ORDER BY created_at DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

# Initialize database (no-op for PostgreSQL, tables already exist)
init_db()
