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

def insert_mob(
    minecraft_id: str,
    name: str,
    description: str = None,
    mob_type: str = None,
    health: int = 0,
    damage: int = 0,
    armor: int = 0,
    rarity: str = 'common',
    biome: str = None,
    can_swim: bool = False,
    can_fly: bool = False,
    drops_items: str = None,
    xp_reward: int = 0,
    difficulty_rating: int = 0
):
    """Insert a new mob into the database."""
    conn = get_connection()
    cur = conn.cursor()
    # Use minecraft_id as mob_id for simplicity
    cur.execute(
        """INSERT INTO mobs 
        (mob_id, minecraft_id, name, description, mob_type, health, damage, armor, rarity, biome, can_swim, can_fly, drops_items, xp_reward, difficulty_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (minecraft_id) DO NOTHING""",
        (minecraft_id, minecraft_id, name, description, mob_type, health, damage, armor, rarity, biome, can_swim, can_fly, drops_items, xp_reward, difficulty_rating)
    )
    conn.commit()
    cur.close()
    conn.close()

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

def insert_item(
    minecraft_id: str,
    name: str,
    description: str = None,
    item_category: str = None,
    max_stack_size: int = 64,
    durability: int = None,
    damage: int = None,
    rarity: str = 'common',
    is_craftable: bool = False,
    value: int = 0
):
    """Insert a new item into the database."""
    conn = get_connection()
    cur = conn.cursor()
    # Use minecraft_id as item_id for simplicity
    cur.execute(
        """INSERT INTO items 
        (item_id, minecraft_id, name, description, item_category, max_stack_size, durability, damage, rarity, is_craftable, value)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (minecraft_id) DO NOTHING""",
        (minecraft_id, minecraft_id, name, description, item_category, max_stack_size, durability, damage, rarity, is_craftable, value)
    )
    conn.commit()
    cur.close()
    conn.close()

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


# ============================================
# TOKEN FUNCTIONS (GPS-based discovery)
# ============================================

def insert_token(
    action_type, entity=None, item=None,
    gps_lat=None, gps_lon=None,
    written_by=None, device_id=None, nfc_tag_uid=None,
    written_at=None
):
    """
    Insert a token record for GPS-based discovery.
    
    Args:
        action_type: 'summon_entity', 'give_item', or 'set_time'
        entity: Minecraft entity ID (required for summon_entity)
        item: Minecraft item ID (required for give_item)
        gps_lat: Latitude where token was written
        gps_lon: Longitude where token was written
        written_by: Player or device that wrote the token
        device_id: Device identifier
        nfc_tag_uid: NFC tag UID for duplicate detection
        written_at: Timestamp (defaults to NOW())
    
    Returns:
        UUID of the created token
    """
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        """INSERT INTO tokens 
        (action_type, entity, item, gps_write_lat, gps_write_lon, written_by, device_id, nfc_tag_uid, written_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, NOW()))
        RETURNING token_id""",
        (action_type, entity, item, gps_lat, gps_lon, written_by, device_id, nfc_tag_uid, written_at)
    )
    
    token_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return str(token_id)


def get_nearby_tokens(
    lat, lon, radius_km,
    limit=50, action_type=None, mob_type=None
):
    """
    Get tokens within a radius of a GPS location using PostGIS spatial queries.
    
    Args:
        lat: Latitude of search origin
        lon: Longitude of search origin
        radius_km: Search radius in kilometers
        limit: Maximum number of results (default 50)
        action_type: Optional filter for action type
        mob_type: Optional filter for mob type (only for summon_entity actions)
    
    Returns:
        List of token dicts with distance_m and bearing fields
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Convert km to meters for PostGIS
    radius_m = radius_km * 1000
    
    # Build query with optional filters
    # Note: Returns N nearest tokens regardless of distance (no radius filtering)
    query = """
        SELECT 
            t.token_id,
            t.action_type,
            t.entity,
            t.item,
            t.gps_write_lat AS lat,
            t.gps_write_lon AS lon,
            t.written_by,
            t.device_id,
            t.nfc_tag_uid,
            t.written_at,
            -- Calculate distance using PostGIS
            ST_Distance(
                t.gps_location,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
            ) AS distance_m,
            -- Mob metadata (if entity exists)
            m.name AS mob_name,
            m.rarity AS mob_rarity,
            m.mob_type,
            m.image_url AS mob_image,
            -- Item metadata (if item exists)
            i.name AS item_name,
            i.rarity AS item_rarity,
            i.image_url AS item_image
        FROM tokens t
        LEFT JOIN mobs m ON t.entity = m.minecraft_id
        LEFT JOIN items i ON t.item = i.minecraft_id
        WHERE t.gps_location IS NOT NULL
    """
    
    params = [lon, lat]
    
    # Add optional filters
    if action_type:
        query += " AND t.action_type = %s"
        params.append(action_type)
    
    if mob_type:
        query += " AND m.mob_type = %s"
        params.append(mob_type)
    
    # Order by distance and limit results
    query += """
        ORDER BY distance_m ASC
        LIMIT %s
    """
    params.append(limit)
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [dict(r) for r in rows]


def get_all_tokens(limit=100):
    """Get all tokens (for testing/debugging)."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT 
            token_id, action_type, entity, item,
            gps_write_lat, gps_write_lon,
            written_by, device_id, nfc_tag_uid, written_at
        FROM tokens
        ORDER BY written_at DESC
        LIMIT %s""",
        (limit,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]


# Initialize database (no-op for PostgreSQL, tables already exist)
init_db()
