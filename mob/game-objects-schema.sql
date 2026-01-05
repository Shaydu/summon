-- Game Objects Database Schema
-- For PostgreSQL
-- Stores metadata for mobs, items, and actions used in NFC tokens

-- ============================================
-- MOBS / ENTITIES TABLE
-- ============================================
CREATE TABLE mobs (
    mob_id TEXT PRIMARY KEY,                    -- e.g., "piglin", "zombie", "ender_dragon"
    name TEXT NOT NULL,                         -- Display name: "Piglin", "Zombie"
    description TEXT,                           -- Lore/bio text
    mob_type TEXT NOT NULL,                     -- hostile, passive, neutral, boss
    minecraft_id TEXT UNIQUE NOT NULL,          -- Actual Minecraft entity ID

    -- Combat stats
    health INTEGER,                             -- Hit points
    damage INTEGER,                             -- Attack damage
    armor INTEGER DEFAULT 0,                    -- Armor points

    -- Spawn metadata
    rarity TEXT,                                -- common, uncommon, rare, legendary, mythic
    biome TEXT,                                 -- Where they naturally spawn
    min_light_level INTEGER,                    -- Spawn light requirements
    max_light_level INTEGER,

    -- Behavioral traits
    can_swim BOOLEAN DEFAULT FALSE,
    can_fly BOOLEAN DEFAULT FALSE,
    drops_items TEXT,                           -- JSON array of item IDs

    -- Visual/display
    image_url TEXT,                             -- Icon/sprite URL
    sound_effect TEXT,                          -- Mob sound identifier

    -- Game balance
    xp_reward INTEGER DEFAULT 0,
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 10),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ITEMS / GIFTS TABLE
-- ============================================
CREATE TABLE items (
    item_id TEXT PRIMARY KEY,                   -- e.g., "emerald", "diamond_sword"
    name TEXT NOT NULL,                         -- Display name: "Emerald", "Diamond Sword"
    description TEXT,                           -- Item lore/description
    item_category TEXT NOT NULL,                -- weapon, tool, food, block, resource, misc
    minecraft_id TEXT UNIQUE NOT NULL,          -- Actual Minecraft item ID

    -- Item properties
    max_stack_size INTEGER DEFAULT 64,          -- How many can stack (1-64)
    durability INTEGER,                         -- For tools/weapons/armor (NULL if not applicable)
    damage INTEGER,                             -- Weapon damage
    armor_value INTEGER,                        -- Armor protection value
    food_value INTEGER,                         -- Hunger points restored
    saturation REAL,                            -- Food saturation value

    -- Crafting/obtaining
    is_craftable BOOLEAN DEFAULT FALSE,
    crafting_recipe TEXT,                       -- JSON or reference to recipe
    rarity TEXT,                                -- common, uncommon, rare, legendary

    -- Visual/display
    image_url TEXT,                             -- Icon/sprite URL
    color_code TEXT,                            -- Hex color for UI theming

    -- Game balance
    value INTEGER,                              -- In-game currency value
    enchantable BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ACTIONS TABLE
-- ============================================
CREATE TABLE actions (
    action_id TEXT PRIMARY KEY,                 -- e.g., "set_time_day", "teleport_spawn"
    action_type TEXT NOT NULL,                  -- set_time, teleport, execute_command, weather, etc.
    name TEXT NOT NULL,                         -- Display name: "Set Time to Day"
    description TEXT,                           -- What this action does

    -- Action parameters (stored as JSON for flexibility)
    default_params JSONB,                       -- Default parameters for this action
    required_params TEXT[],                     -- Array of required param names

    -- Access control
    requires_op BOOLEAN DEFAULT FALSE,          -- Requires operator privileges
    cooldown_seconds INTEGER DEFAULT 0,         -- Minimum time between uses

    -- Visual/display
    icon_name TEXT,                             -- Icon identifier
    color_code TEXT,                            -- UI color

    -- Classification
    category TEXT,                              -- world, player, server, admin
    rarity TEXT,                                -- common, rare, legendary

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

-- Mobs indexes
CREATE INDEX idx_mobs_type ON mobs(mob_type);
CREATE INDEX idx_mobs_rarity ON mobs(rarity);
CREATE INDEX idx_mobs_minecraft_id ON mobs(minecraft_id);

-- Items indexes
CREATE INDEX idx_items_category ON items(item_category);
CREATE INDEX idx_items_rarity ON items(rarity);
CREATE INDEX idx_items_minecraft_id ON items(minecraft_id);

-- Actions indexes
CREATE INDEX idx_actions_type ON actions(action_type);
CREATE INDEX idx_actions_category ON actions(category);

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE mobs IS 'Metadata for all summonable entities/mobs';
COMMENT ON TABLE items IS 'Metadata for all giveable items/gifts';
COMMENT ON TABLE actions IS 'Metadata for all executable actions (time, weather, teleport, etc.)';

-- ============================================
-- SAMPLE DATA - MOBS
-- ============================================

INSERT INTO mobs (mob_id, name, description, mob_type, minecraft_id, health, damage, rarity, biome, can_swim, can_fly, difficulty_rating) VALUES
('zombie', 'Zombie', 'Classic undead mob that burns in sunlight', 'hostile', 'zombie', 20, 3, 'common', 'overworld', FALSE, FALSE, 2),
('piglin', 'Piglin', 'Gold-loving inhabitants of the Nether', 'neutral', 'piglin', 16, 5, 'common', 'nether', FALSE, FALSE, 3),
('creeper', 'Creeper', 'Explosive green menace', 'hostile', 'creeper', 20, 49, 'common', 'overworld', FALSE, FALSE, 4),
('enderman', 'Enderman', 'Tall, teleporting creature from the End', 'neutral', 'enderman', 40, 7, 'uncommon', 'end', TRUE, FALSE, 5),
('skeleton', 'Skeleton', 'Ranged undead archer', 'hostile', 'skeleton', 20, 4, 'common', 'overworld', FALSE, FALSE, 3),
('sheep', 'Sheep', 'Peaceful wool-producing animal', 'passive', 'sheep', 8, 0, 'common', 'overworld', FALSE, FALSE, 1),
('cow', 'Cow', 'Passive mob that provides leather and beef', 'passive', 'cow', 10, 0, 'common', 'overworld', FALSE, FALSE, 1),
('pig', 'Pig', 'Rideable passive mob', 'passive', 'pig', 10, 0, 'common', 'overworld', FALSE, FALSE, 1),
('chicken', 'Chicken', 'Egg-laying passive mob', 'passive', 'chicken', 4, 0, 'common', 'overworld', FALSE, FALSE, 1),
('wither_skeleton', 'Wither Skeleton', 'Dangerous Nether fortress mob', 'hostile', 'wither_skeleton', 20, 8, 'rare', 'nether', FALSE, FALSE, 6),
('blaze', 'Blaze', 'Flying fireball-shooting mob from Nether fortresses', 'hostile', 'blaze', 20, 6, 'uncommon', 'nether', FALSE, TRUE, 5),
('ender_dragon', 'Ender Dragon', 'The ultimate boss mob', 'boss', 'ender_dragon', 200, 15, 'legendary', 'end', FALSE, TRUE, 10),
('wither', 'Wither', 'Three-headed boss mob', 'boss', 'wither', 300, 8, 'legendary', 'overworld', FALSE, TRUE, 10),
('iron_golem', 'Iron Golem', 'Protective village guardian', 'neutral', 'iron_golem', 100, 21, 'uncommon', 'village', FALSE, FALSE, 6),
('wolf', 'Wolf', 'Tameable wild dog', 'neutral', 'wolf', 8, 4, 'common', 'forest', FALSE, FALSE, 2),
('spider', 'Spider', 'Climbing hostile arthropod', 'hostile', 'spider', 16, 2, 'common', 'overworld', FALSE, FALSE, 2),
('cave_spider', 'Cave Spider', 'Poisonous spider found in mineshafts', 'hostile', 'cave_spider', 12, 2, 'uncommon', 'cave', FALSE, FALSE, 4),
('witch', 'Witch', 'Potion-throwing hostile mob', 'hostile', 'witch', 26, 0, 'uncommon', 'swamp', FALSE, FALSE, 5),
('phantom', 'Phantom', 'Flying undead that attacks players who haven''t slept', 'hostile', 'phantom', 20, 6, 'uncommon', 'overworld', FALSE, TRUE, 4),
('guardian', 'Guardian', 'Aquatic defender of ocean monuments', 'hostile', 'guardian', 30, 8, 'rare', 'ocean', TRUE, FALSE, 6);

-- ============================================
-- SAMPLE DATA - ITEMS
-- ============================================

INSERT INTO items (item_id, name, description, item_category, minecraft_id, max_stack_size, durability, damage, rarity, is_craftable, value, enchantable) VALUES
-- Resources
('emerald', 'Emerald', 'Precious green gem used for trading', 'resource', 'emerald', 64, NULL, NULL, 'uncommon', FALSE, 100, FALSE),
('diamond', 'Diamond', 'Rare and valuable blue gem', 'resource', 'diamond', 64, NULL, NULL, 'rare', FALSE, 500, FALSE),
('iron_ingot', 'Iron Ingot', 'Refined iron for crafting', 'resource', 'iron_ingot', 64, NULL, NULL, 'common', TRUE, 10, FALSE),
('gold_ingot', 'Gold Ingot', 'Shiny metal ingot', 'resource', 'gold_ingot', 64, NULL, NULL, 'uncommon', TRUE, 50, FALSE),
('coal', 'Coal', 'Fuel and crafting material', 'resource', 'coal', 64, NULL, NULL, 'common', FALSE, 2, FALSE),
('redstone', 'Redstone', 'Electrical component for circuits', 'resource', 'redstone', 64, NULL, NULL, 'common', FALSE, 5, FALSE),

-- Weapons
('diamond_sword', 'Diamond Sword', 'Powerful melee weapon', 'weapon', 'diamond_sword', 1, 1561, 7, 'rare', TRUE, 200, TRUE),
('iron_sword', 'Iron Sword', 'Standard melee weapon', 'weapon', 'iron_sword', 1, 250, 6, 'common', TRUE, 50, TRUE),
('bow', 'Bow', 'Ranged weapon that shoots arrows', 'weapon', 'bow', 1, 384, 0, 'common', TRUE, 30, TRUE),
('crossbow', 'Crossbow', 'Advanced ranged weapon', 'weapon', 'crossbow', 1, 326, 0, 'uncommon', TRUE, 75, TRUE),

-- Tools
('diamond_pickaxe', 'Diamond Pickaxe', 'Fast mining tool', 'tool', 'diamond_pickaxe', 1, 1561, 0, 'rare', TRUE, 150, TRUE),
('iron_pickaxe', 'Iron Pickaxe', 'Standard mining tool', 'tool', 'iron_pickaxe', 1, 250, 0, 'common', TRUE, 40, TRUE),
('iron_axe', 'Iron Axe', 'Woodcutting and combat tool', 'tool', 'iron_axe', 1, 250, 0, 'common', TRUE, 40, TRUE),
('fishing_rod', 'Fishing Rod', 'Tool for catching fish', 'tool', 'fishing_rod', 1, 64, 0, 'common', TRUE, 20, TRUE),

-- Food
('apple', 'Apple', 'Restores a small amount of hunger', 'food', 'apple', 64, NULL, NULL, 'common', FALSE, 5, FALSE),
('bread', 'Bread', 'Basic food item', 'food', 'bread', 64, NULL, NULL, 'common', TRUE, 10, FALSE),
('cooked_beef', 'Cooked Beef', 'Nutritious cooked meat', 'food', 'cooked_beef', 64, NULL, NULL, 'common', FALSE, 15, FALSE),
('golden_apple', 'Golden Apple', 'Rare food that grants special effects', 'food', 'golden_apple', 64, NULL, NULL, 'rare', TRUE, 200, FALSE),
('cookie', 'Cookie', 'Sweet treat', 'food', 'cookie', 64, NULL, NULL, 'common', TRUE, 8, FALSE),

-- Blocks
('dirt', 'Dirt', 'Basic earth block', 'block', 'dirt', 64, NULL, NULL, 'common', FALSE, 1, FALSE),
('stone', 'Stone', 'Basic stone block', 'block', 'stone', 64, NULL, NULL, 'common', FALSE, 1, FALSE),
('oak_planks', 'Oak Planks', 'Wooden planks for building', 'block', 'oak_planks', 64, NULL, NULL, 'common', TRUE, 2, FALSE),
('glass', 'Glass', 'Transparent block', 'block', 'glass', 64, NULL, NULL, 'common', TRUE, 5, FALSE),
('tnt', 'TNT', 'Explosive block', 'block', 'tnt', 64, NULL, NULL, 'uncommon', TRUE, 50, FALSE),
('torch', 'Torch', 'Light source', 'block', 'torch', 64, NULL, NULL, 'common', TRUE, 2, FALSE),

-- Misc
('bucket', 'Bucket', 'Container for liquids', 'misc', 'bucket', 16, NULL, NULL, 'common', TRUE, 15, FALSE),
('compass', 'Compass', 'Points to world spawn', 'misc', 'compass', 64, NULL, NULL, 'common', TRUE, 30, FALSE),
('map', 'Map', 'Shows explored terrain', 'misc', 'map', 64, NULL, NULL, 'common', TRUE, 40, FALSE),
('saddle', 'Saddle', 'Allows riding certain mobs', 'misc', 'saddle', 1, NULL, NULL, 'uncommon', FALSE, 100, FALSE),
('name_tag', 'Name Tag', 'Allows naming mobs', 'misc', 'name_tag', 64, NULL, NULL, 'uncommon', FALSE, 75, FALSE),
('ender_pearl', 'Ender Pearl', 'Teleportation item', 'misc', 'ender_pearl', 16, NULL, NULL, 'uncommon', FALSE, 80, FALSE),
('elytra', 'Elytra', 'Wings for gliding', 'misc', 'elytra', 1, 432, NULL, 'legendary', FALSE, 1000, TRUE);

-- ============================================
-- SAMPLE DATA - ACTIONS
-- ============================================

INSERT INTO actions (action_id, action_type, name, description, default_params, required_params, requires_op, cooldown_seconds, category, rarity) VALUES
-- Time actions
('set_time_day', 'set_time', 'Set Time to Day', 'Changes the time to early morning', '{"time": "day"}', ARRAY['time'], FALSE, 0, 'world', 'common'),
('set_time_night', 'set_time', 'Set Time to Night', 'Changes the time to early evening', '{"time": "night"}', ARRAY['time'], FALSE, 0, 'world', 'common'),
('set_time_noon', 'set_time', 'Set Time to Noon', 'Changes the time to midday', '{"time": 6000}', ARRAY['time'], FALSE, 0, 'world', 'common'),
('set_time_midnight', 'set_time', 'Set Time to Midnight', 'Changes the time to midnight', '{"time": 18000}', ARRAY['time'], FALSE, 0, 'world', 'common'),

-- Weather actions
('set_weather_clear', 'set_weather', 'Clear Weather', 'Makes the weather sunny', '{"weather": "clear"}', ARRAY['weather'], FALSE, 60, 'world', 'common'),
('set_weather_rain', 'set_weather', 'Rain', 'Makes it rain', '{"weather": "rain"}', ARRAY['weather'], FALSE, 60, 'world', 'common'),
('set_weather_thunder', 'set_weather', 'Thunder Storm', 'Summons a thunderstorm', '{"weather": "thunder"}', ARRAY['weather'], FALSE, 120, 'world', 'uncommon'),

-- Teleport actions
('teleport_spawn', 'teleport', 'Teleport to Spawn', 'Teleports player to world spawn point', '{"x": 0, "y": 64, "z": 0}', ARRAY['player'], FALSE, 300, 'player', 'uncommon'),
('teleport_home', 'teleport', 'Teleport Home', 'Teleports player to their bed spawn', '{}', ARRAY['player'], FALSE, 600, 'player', 'rare'),

-- Broadcast actions
('broadcast_message', 'broadcast', 'Broadcast Message', 'Sends a message to all players', '{}', ARRAY['message'], FALSE, 10, 'server', 'common'),

-- Player effects
('give_regeneration', 'effect', 'Regeneration', 'Grants regeneration effect', '{"effect": "regeneration", "duration": 30, "amplifier": 1}', ARRAY['player'], FALSE, 300, 'player', 'uncommon'),
('give_speed', 'effect', 'Speed Boost', 'Grants speed effect', '{"effect": "speed", "duration": 60, "amplifier": 1}', ARRAY['player'], FALSE, 300, 'player', 'uncommon'),
('give_jump_boost', 'effect', 'Jump Boost', 'Grants jump boost effect', '{"effect": "jump_boost", "duration": 60, "amplifier": 2}', ARRAY['player'], FALSE, 300, 'player', 'uncommon'),
('give_night_vision', 'effect', 'Night Vision', 'Grants night vision', '{"effect": "night_vision", "duration": 180, "amplifier": 0}', ARRAY['player'], FALSE, 600, 'player', 'rare'),

-- Admin actions
('server_restart', 'server_control', 'Restart Server', 'Restarts the Minecraft server', '{}', ARRAY[], TRUE, 0, 'admin', 'legendary'),
('backup_world', 'server_control', 'Backup World', 'Creates a world backup', '{}', ARRAY[], TRUE, 3600, 'admin', 'legendary');

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: All hostile mobs
CREATE VIEW hostile_mobs AS
SELECT * FROM mobs WHERE mob_type = 'hostile' ORDER BY difficulty_rating DESC;

-- View: All passive mobs
CREATE VIEW passive_mobs AS
SELECT * FROM mobs WHERE mob_type = 'passive' ORDER BY name;

-- View: Boss mobs
CREATE VIEW boss_mobs AS
SELECT * FROM mobs WHERE mob_type = 'boss' ORDER BY health DESC;

-- View: Legendary items
CREATE VIEW legendary_items AS
SELECT * FROM items WHERE rarity = 'legendary' ORDER BY value DESC;

-- View: Weapons catalog
CREATE VIEW weapons AS
SELECT * FROM items WHERE item_category = 'weapon' ORDER BY damage DESC;

-- View: Food items
CREATE VIEW food_items AS
SELECT * FROM items WHERE item_category = 'food' ORDER BY food_value DESC;

-- ============================================
-- EXAMPLE QUERIES
-- ============================================

-- Get all hostile mobs ordered by difficulty
-- SELECT * FROM hostile_mobs;

-- Get all items that can be enchanted
-- SELECT name, item_category, rarity FROM items WHERE enchantable = TRUE;

-- Get mob details for a specific minecraft_id
-- SELECT * FROM mobs WHERE minecraft_id = 'piglin';

-- Get all rare and legendary items
-- SELECT name, item_category, value FROM items WHERE rarity IN ('rare', 'legendary') ORDER BY value DESC;

-- Get all actions that don't require operator privileges
-- SELECT name, action_type, description FROM actions WHERE requires_op = FALSE;

-- Get food items sorted by nutrition
-- SELECT name, food_value, saturation FROM items WHERE item_category = 'food' ORDER BY food_value DESC NULLS LAST;

-- ============================================
-- SQLite version (for development/testing)
-- ============================================
-- Uncomment the following to use SQLite instead of PostgreSQL
/*
-- MOBS TABLE (SQLite)
CREATE TABLE mobs (
    mob_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    mob_type TEXT NOT NULL,
    minecraft_id TEXT UNIQUE NOT NULL,
    health INTEGER,
    damage INTEGER,
    armor INTEGER DEFAULT 0,
    rarity TEXT,
    biome TEXT,
    min_light_level INTEGER,
    max_light_level INTEGER,
    can_swim INTEGER DEFAULT 0,
    can_fly INTEGER DEFAULT 0,
    drops_items TEXT,
    image_url TEXT,
    sound_effect TEXT,
    xp_reward INTEGER DEFAULT 0,
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 10),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ITEMS TABLE (SQLite)
CREATE TABLE items (
    item_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    item_category TEXT NOT NULL,
    minecraft_id TEXT UNIQUE NOT NULL,
    max_stack_size INTEGER DEFAULT 64,
    durability INTEGER,
    damage INTEGER,
    armor_value INTEGER,
    food_value INTEGER,
    saturation REAL,
    is_craftable INTEGER DEFAULT 0,
    crafting_recipe TEXT,
    rarity TEXT,
    image_url TEXT,
    color_code TEXT,
    value INTEGER,
    enchantable INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ACTIONS TABLE (SQLite)
CREATE TABLE actions (
    action_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    default_params TEXT,
    required_params TEXT,
    requires_op INTEGER DEFAULT 0,
    cooldown_seconds INTEGER DEFAULT 0,
    icon_name TEXT,
    color_code TEXT,
    category TEXT,
    rarity TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
*/
