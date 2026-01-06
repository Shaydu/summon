-- Migration: Consolidate mob_id and minecraft_id to single primary key
-- Date: 2026-01-05
-- Description: Remove redundant mob_id column, make minecraft_id the primary key

-- ============================================
-- STEP 1: Drop old primary key and rename
-- ============================================

-- Drop the old primary key constraint
ALTER TABLE mobs DROP CONSTRAINT IF EXISTS mobs_pkey;

-- Drop the unique constraint on minecraft_id (will become primary key)
ALTER TABLE mobs DROP CONSTRAINT IF EXISTS mobs_minecraft_id_key;

-- Drop the mob_id column (it's redundant with minecraft_id)
ALTER TABLE mobs DROP COLUMN IF EXISTS mob_id;

-- Make minecraft_id the new primary key
ALTER TABLE mobs ADD PRIMARY KEY (minecraft_id);

-- ============================================
-- STEP 2: Same for items table
-- ============================================

ALTER TABLE items DROP CONSTRAINT IF EXISTS items_pkey;
ALTER TABLE items DROP CONSTRAINT IF EXISTS items_minecraft_id_key;
ALTER TABLE items DROP COLUMN IF EXISTS item_id;
ALTER TABLE items ADD PRIMARY KEY (minecraft_id);

-- ============================================
-- STEP 3: Update comments
-- ============================================

COMMENT ON COLUMN mobs.minecraft_id IS 'Minecraft entity ID (primary key, e.g., piglin, zombie)';
COMMENT ON COLUMN items.minecraft_id IS 'Minecraft item ID (primary key, e.g., diamond_sword, golden_apple)';
