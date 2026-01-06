-- Migration: Add PostGIS extension and tokens table
-- Date: 2026-01-05
-- Description: Enable spatial queries for nearby token discovery

-- ============================================
-- ENABLE POSTGIS EXTENSION
-- ============================================
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- TOKENS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS tokens (
    token_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Action details
    action_type TEXT NOT NULL CHECK (action_type IN ('summon_entity', 'give_item', 'set_time')),
    entity TEXT,  -- Minecraft entity ID (e.g., 'piglin')
    item TEXT,    -- Minecraft item ID (e.g., 'diamond_sword')
    
    -- GPS location where token was written (PostGIS geography type)
    gps_location GEOGRAPHY(POINT, 4326),  -- WGS84 coordinate system
    gps_write_lat DOUBLE PRECISION,
    gps_write_lon DOUBLE PRECISION,
    
    -- Metadata
    written_by TEXT NOT NULL,
    device_id TEXT,
    nfc_tag_uid TEXT,  -- Optional: NFC tag UID for duplicate detection
    
    -- Timestamps
    written_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_action_entity CHECK (
        (action_type = 'summon_entity' AND entity IS NOT NULL) OR action_type != 'summon_entity'
    ),
    CONSTRAINT valid_action_item CHECK (
        (action_type = 'give_item' AND item IS NOT NULL) OR action_type != 'give_item'
    ),
    CONSTRAINT valid_gps_lat CHECK (gps_write_lat IS NULL OR (gps_write_lat >= -90 AND gps_write_lat <= 90)),
    CONSTRAINT valid_gps_lon CHECK (gps_write_lon IS NULL OR (gps_write_lon >= -180 AND gps_write_lon <= 180))
);

-- ============================================
-- INDEXES FOR TOKENS TABLE
-- ============================================

-- Spatial index for fast proximity searches (most important!)
CREATE INDEX IF NOT EXISTS idx_tokens_gps_location ON tokens USING GIST (gps_location);

-- Standard indexes for filtering
CREATE INDEX IF NOT EXISTS idx_tokens_action_type ON tokens(action_type);
CREATE INDEX IF NOT EXISTS idx_tokens_entity ON tokens(entity) WHERE entity IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tokens_item ON tokens(item) WHERE item IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tokens_written_by ON tokens(written_by);
CREATE INDEX IF NOT EXISTS idx_tokens_written_at ON tokens(written_at DESC);
CREATE INDEX IF NOT EXISTS idx_tokens_nfc_tag ON tokens(nfc_tag_uid) WHERE nfc_tag_uid IS NOT NULL;

-- Composite index for common filtered queries
CREATE INDEX IF NOT EXISTS idx_tokens_action_location ON tokens(action_type) 
WHERE gps_location IS NOT NULL;

-- ============================================
-- TRIGGER: Sync lat/lon to PostGIS geography
-- ============================================

CREATE OR REPLACE FUNCTION sync_token_gps_location()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.gps_write_lat IS NOT NULL AND NEW.gps_write_lon IS NOT NULL THEN
        NEW.gps_location := ST_SetSRID(
            ST_MakePoint(NEW.gps_write_lon, NEW.gps_write_lat),
            4326
        )::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_token_gps_location
BEFORE INSERT OR UPDATE ON tokens
FOR EACH ROW
EXECUTE FUNCTION sync_token_gps_location();

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE tokens IS 'Stores NFC token write locations for nearby discovery and navigation';
COMMENT ON COLUMN tokens.token_id IS 'Unique token identifier (UUID)';
COMMENT ON COLUMN tokens.action_type IS 'Type of action: summon_entity, give_item, or set_time';
COMMENT ON COLUMN tokens.entity IS 'Minecraft entity ID for summon_entity actions';
COMMENT ON COLUMN tokens.item IS 'Minecraft item ID for give_item actions';
COMMENT ON COLUMN tokens.gps_location IS 'PostGIS geography point for spatial queries (auto-synced from lat/lon)';
COMMENT ON COLUMN tokens.gps_write_lat IS 'Latitude where token was written (-90 to 90)';
COMMENT ON COLUMN tokens.gps_write_lon IS 'Longitude where token was written (-180 to 180)';
COMMENT ON COLUMN tokens.written_by IS 'Player or device that wrote the token';
COMMENT ON COLUMN tokens.device_id IS 'Device identifier that wrote the token';
COMMENT ON COLUMN tokens.nfc_tag_uid IS 'NFC tag UID for duplicate detection';
COMMENT ON COLUMN tokens.written_at IS 'When the token was written';

-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Find tokens within 5km of a point (using PostGIS)
-- SELECT 
--   token_id,
--   action_type,
--   entity,
--   item,
--   written_by,
--   ST_Distance(gps_location, ST_SetSRID(ST_MakePoint(-105.3009, 40.7580), 4326)::geography) AS distance_m
-- FROM tokens
-- WHERE ST_DWithin(
--   gps_location,
--   ST_SetSRID(ST_MakePoint(-105.3009, 40.7580), 4326)::geography,
--   5000  -- 5km in meters
-- )
-- ORDER BY distance_m
-- LIMIT 10;
