-- PostgreSQL Database Schema for Summon API
-- Main application tables: summons, device_locations
-- This schema complements mob/game-objects-schema.sql

-- ============================================
-- SUMMONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS summons (
    id SERIAL PRIMARY KEY,
    server_ip TEXT,
    server_port INTEGER,
    summoned_object_type TEXT NOT NULL,
    summoning_player TEXT NOT NULL,
    summoned_player TEXT NOT NULL,
    timestamp_utc TIMESTAMP WITH TIME ZONE NOT NULL,
    gps_lat DOUBLE PRECISION,
    gps_lon DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_port CHECK (server_port > 0 AND server_port <= 65535),
    CONSTRAINT valid_lat CHECK (gps_lat IS NULL OR (gps_lat >= -90 AND gps_lat <= 90)),
    CONSTRAINT valid_lon CHECK (gps_lon IS NULL OR (gps_lon >= -180 AND gps_lon <= 180))
);

-- Indexes for summons table
CREATE INDEX IF NOT EXISTS idx_summons_summoning_player ON summons(summoning_player);
CREATE INDEX IF NOT EXISTS idx_summons_summoned_player ON summons(summoned_player);
CREATE INDEX IF NOT EXISTS idx_summons_object_type ON summons(summoned_object_type);
CREATE INDEX IF NOT EXISTS idx_summons_timestamp ON summons(timestamp_utc DESC);
CREATE INDEX IF NOT EXISTS idx_summons_server ON summons(server_ip, server_port);

-- Comments
COMMENT ON TABLE summons IS 'Stores all summon requests made through the API';
COMMENT ON COLUMN summons.summoned_object_type IS 'Type of entity or item summoned (e.g., piglin, diamond_sword)';
COMMENT ON COLUMN summons.summoning_player IS 'Player who initiated the summon';
COMMENT ON COLUMN summons.summoned_player IS 'Target player for the summon';
COMMENT ON COLUMN summons.timestamp_utc IS 'When the summon was requested (UTC)';

-- ============================================
-- DEVICE LOCATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS device_locations (
    id SERIAL PRIMARY KEY,
    device_id TEXT NOT NULL,
    player TEXT,
    gps_lat DOUBLE PRECISION NOT NULL,
    gps_lon DOUBLE PRECISION NOT NULL,
    gps_alt DOUBLE PRECISION,
    gps_speed DOUBLE PRECISION,
    satellites INTEGER,
    hdop DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_device_id CHECK (device_id != ''),
    CONSTRAINT valid_lat CHECK (gps_lat >= -90 AND gps_lat <= 90),
    CONSTRAINT valid_lon CHECK (gps_lon >= -180 AND gps_lon <= 180),
    CONSTRAINT valid_satellites CHECK (satellites IS NULL OR satellites >= 0),
    CONSTRAINT valid_hdop CHECK (hdop IS NULL OR hdop >= 0)
);

-- Indexes for device_locations table
CREATE INDEX IF NOT EXISTS idx_device_locations_device_id ON device_locations(device_id);
CREATE INDEX IF NOT EXISTS idx_device_locations_player ON device_locations(player);
CREATE INDEX IF NOT EXISTS idx_device_locations_timestamp ON device_locations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_device_locations_device_timestamp ON device_locations(device_id, timestamp DESC);

-- Comments
COMMENT ON TABLE device_locations IS 'Stores GPS location data from NFC-enabled devices';
COMMENT ON COLUMN device_locations.device_id IS 'Unique identifier for the device';
COMMENT ON COLUMN device_locations.player IS 'Associated Minecraft player name (optional)';
COMMENT ON COLUMN device_locations.gps_lat IS 'GPS latitude in degrees';
COMMENT ON COLUMN device_locations.gps_lon IS 'GPS longitude in degrees';
COMMENT ON COLUMN device_locations.gps_alt IS 'GPS altitude in meters (optional)';
COMMENT ON COLUMN device_locations.gps_speed IS 'GPS speed in m/s (optional)';
COMMENT ON COLUMN device_locations.satellites IS 'Number of GPS satellites in use (optional)';
COMMENT ON COLUMN device_locations.hdop IS 'Horizontal Dilution of Precision (optional)';
COMMENT ON COLUMN device_locations.timestamp IS 'When the location was recorded';

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Recent summons (last 100)
CREATE OR REPLACE VIEW recent_summons AS
SELECT 
    id,
    server_ip,
    server_port,
    summoned_object_type,
    summoning_player,
    summoned_player,
    timestamp_utc,
    gps_lat,
    gps_lon,
    created_at
FROM summons
ORDER BY timestamp_utc DESC
LIMIT 100;

-- View: Latest device locations (one per device)
CREATE OR REPLACE VIEW latest_device_locations AS
SELECT DISTINCT ON (device_id)
    id,
    device_id,
    player,
    gps_lat,
    gps_lon,
    gps_alt,
    gps_speed,
    satellites,
    hdop,
    timestamp
FROM device_locations
ORDER BY device_id, timestamp DESC;

-- View: Summons with location data
CREATE OR REPLACE VIEW summons_with_gps AS
SELECT 
    id,
    server_ip,
    server_port,
    summoned_object_type,
    summoning_player,
    summoned_player,
    timestamp_utc,
    gps_lat,
    gps_lon
FROM summons
WHERE gps_lat IS NOT NULL AND gps_lon IS NOT NULL
ORDER BY timestamp_utc DESC;

-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Get all summons by a specific player
-- SELECT * FROM summons WHERE summoning_player = 'ActorPlayer' ORDER BY timestamp_utc DESC;

-- Get summons for a specific mob type
-- SELECT * FROM summons WHERE summoned_object_type = 'piglin' ORDER BY timestamp_utc DESC;

-- Get recent summons with GPS data
-- SELECT * FROM summons_with_gps LIMIT 50;

-- Get latest location for each device
-- SELECT * FROM latest_device_locations;

-- Get all locations for a specific device
-- SELECT * FROM device_locations WHERE device_id = 'ios-device-123' ORDER BY timestamp DESC;

-- Get summon statistics by mob type
-- SELECT summoned_object_type, COUNT(*) as count FROM summons GROUP BY summoned_object_type ORDER BY count DESC;

-- Get summon activity by player
-- SELECT summoning_player, COUNT(*) as summon_count FROM summons GROUP BY summoning_player ORDER BY summon_count DESC;
