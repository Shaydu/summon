-- Game Objects SQLite Database
-- Complete database with mobs, items, and actions
-- To create: sqlite3 game_objects.db < game_objects.db.sql

-- ============================================
-- MOBS / ENTITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS mobs (
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

-- ============================================
-- ITEMS / GIFTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS items (
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

-- ============================================
-- ACTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS actions (
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

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_mobs_type ON mobs(mob_type);
CREATE INDEX idx_mobs_rarity ON mobs(rarity);
CREATE INDEX idx_mobs_minecraft_id ON mobs(minecraft_id);

CREATE INDEX idx_items_category ON items(item_category);
CREATE INDEX idx_items_rarity ON items(rarity);
CREATE INDEX idx_items_minecraft_id ON items(minecraft_id);

CREATE INDEX idx_actions_type ON actions(action_type);
CREATE INDEX idx_actions_category ON actions(category);

-- ============================================
-- POPULATE MOBS TABLE
-- ============================================
INSERT INTO mobs (mob_id, name, description, mob_type, minecraft_id, health, damage, armor, rarity, biome, can_swim, can_fly, drops_items, xp_reward, difficulty_rating) VALUES
('zombie', 'Zombie', 'Undead mob that burns in sunlight and drops rotten flesh', 'hostile', 'zombie', 20, 3, 0, 'common', 'overworld', 0, 0, '["rotten_flesh","iron_ingot","carrot","potato"]', 5, 2),
('piglin', 'Piglin', 'Gold-loving inhabitants of the Nether who barter items', 'neutral', 'piglin', 16, 5, 0, 'common', 'nether', 0, 0, '["gold_nugget","gold_ingot","porkchop"]', 5, 3),
('creeper', 'Creeper', 'Explosive green menace that silently approaches players', 'hostile', 'creeper', 20, 49, 0, 'common', 'overworld', 0, 0, '["gunpowder","music_disc"]', 5, 4),
('enderman', 'Enderman', 'Tall teleporting creature from the End dimension', 'neutral', 'enderman', 40, 7, 0, 'uncommon', 'end', 1, 0, '["ender_pearl"]', 5, 5),
('skeleton', 'Skeleton', 'Ranged undead archer armed with bow and arrows', 'hostile', 'skeleton', 20, 4, 0, 'common', 'overworld', 0, 0, '["bone","arrow","bow"]', 5, 3),
('spider', 'Spider', 'Climbing hostile arthropod found in dark areas', 'hostile', 'spider', 16, 2, 0, 'common', 'overworld', 0, 0, '["string","spider_eye"]', 5, 2),
('cave_spider', 'Cave Spider', 'Poisonous spider found in abandoned mineshafts', 'hostile', 'cave_spider', 12, 2, 0, 'uncommon', 'cave', 0, 0, '["string","spider_eye"]', 5, 4),
('witch', 'Witch', 'Hostile mob that throws harmful and helpful splash potions', 'hostile', 'witch', 26, 0, 0, 'uncommon', 'swamp', 0, 0, '["glass_bottle","glowstone_dust","redstone","sugar","stick"]', 5, 5),
('blaze', 'Blaze', 'Flying fireball-shooting mob from Nether fortresses', 'hostile', 'blaze', 20, 6, 0, 'uncommon', 'nether', 0, 1, '["blaze_rod"]', 10, 5),
('wither_skeleton', 'Wither Skeleton', 'Dangerous tall skeleton found in Nether fortresses', 'hostile', 'wither_skeleton', 20, 8, 0, 'rare', 'nether', 0, 0, '["coal","bone","wither_skeleton_skull"]', 5, 6),
('phantom', 'Phantom', 'Flying undead that spawns when players haven''t slept', 'hostile', 'phantom', 20, 6, 0, 'uncommon', 'overworld', 0, 1, '["phantom_membrane"]', 5, 4),
('guardian', 'Guardian', 'Aquatic defender of ocean monuments with laser beam', 'hostile', 'guardian', 30, 8, 0, 'rare', 'ocean', 1, 0, '["prismarine_shard","prismarine_crystals","raw_cod"]', 10, 6),
('elder_guardian', 'Elder Guardian', 'Larger, more powerful guardian that inflicts mining fatigue', 'hostile', 'elder_guardian', 80, 8, 0, 'rare', 'ocean', 1, 0, '["prismarine_shard","prismarine_crystals","wet_sponge","raw_cod"]', 10, 8),
('ender_dragon', 'Ender Dragon', 'The ultimate boss mob found in the End dimension', 'boss', 'ender_dragon', 200, 15, 0, 'legendary', 'end', 0, 1, '["dragon_egg","xp_orb"]', 12000, 10),
('wither', 'Wither', 'Three-headed boss mob summoned by players', 'boss', 'wither', 300, 8, 4, 'legendary', 'overworld', 0, 1, '["nether_star"]', 50, 10),

-- Passive Mobs
('sheep', 'Sheep', 'Peaceful wool-producing animal that can be sheared and dyed', 'passive', 'sheep', 8, 0, 0, 'common', 'overworld', 0, 0, '["wool","mutton"]', 1, 1),
('cow', 'Cow', 'Passive mob that provides leather, beef, and milk', 'passive', 'cow', 10, 0, 0, 'common', 'overworld', 0, 0, '["leather","beef"]', 1, 1),
('pig', 'Pig', 'Rideable passive mob that drops porkchops', 'passive', 'pig', 10, 0, 0, 'common', 'overworld', 0, 0, '["porkchop"]', 1, 1),
('chicken', 'Chicken', 'Small passive mob that lays eggs and drops feathers', 'passive', 'chicken', 4, 0, 0, 'common', 'overworld', 0, 0, '["feather","chicken"]', 1, 1),
('rabbit', 'Rabbit', 'Small passive mob found in various biomes', 'passive', 'rabbit', 3, 0, 0, 'common', 'overworld', 0, 0, '["rabbit_hide","rabbit","rabbit_foot"]', 1, 1),
('horse', 'Horse', 'Tameable rideable animal with various coat colors', 'passive', 'horse', 15, 0, 0, 'uncommon', 'plains', 0, 0, '["leather"]', 1, 1),
('donkey', 'Donkey', 'Tameable pack animal that can carry chests', 'passive', 'donkey', 15, 0, 0, 'uncommon', 'plains', 0, 0, '["leather"]', 1, 1),
('cat', 'Cat', 'Tameable pet that scares away creepers and phantoms', 'passive', 'cat', 10, 0, 0, 'uncommon', 'village', 0, 0, '["string"]', 1, 1),
('parrot', 'Parrot', 'Colorful bird that can perch on player shoulders', 'passive', 'parrot', 6, 0, 0, 'uncommon', 'jungle', 0, 1, '["feather"]', 1, 1),
('bee', 'Bee', 'Flying insect that pollinates flowers and produces honey', 'neutral', 'bee', 10, 2, 0, 'uncommon', 'plains', 0, 1, '[]', 1, 2),

-- Neutral Mobs
('wolf', 'Wolf', 'Tameable wild dog that becomes hostile when attacked', 'neutral', 'wolf', 8, 4, 0, 'common', 'forest', 0, 0, '[]', 1, 2),
('iron_golem', 'Iron Golem', 'Large protective mob that defends villages', 'neutral', 'iron_golem', 100, 21, 0, 'uncommon', 'village', 0, 0, '["iron_ingot","poppy"]', 0, 6),
('polar_bear', 'Polar Bear', 'Large neutral mob found in snowy biomes', 'neutral', 'polar_bear', 30, 6, 0, 'uncommon', 'ice_plains', 1, 0, '["raw_cod","raw_salmon"]', 1, 4),
('panda', 'Panda', 'Rare neutral mob found in bamboo jungles', 'neutral', 'panda', 20, 6, 0, 'rare', 'jungle', 0, 0, '["bamboo"]', 1, 2),
('llama', 'Llama', 'Spitting pack animal found in mountains and savannas', 'neutral', 'llama', 15, 1, 0, 'uncommon', 'mountain', 0, 0, '["leather"]', 1, 2),
('dolphin', 'Dolphin', 'Friendly aquatic mammal that helps find treasure', 'neutral', 'dolphin', 10, 3, 0, 'uncommon', 'ocean', 1, 0, '["raw_cod"]', 0, 2),

-- More Hostile Mobs
('drowned', 'Drowned', 'Underwater zombie variant that wields tridents', 'hostile', 'drowned', 20, 3, 0, 'common', 'ocean', 1, 0, '["rotten_flesh","gold_ingot","trident","nautilus_shell"]', 5, 4),
('husk', 'Husk', 'Desert zombie variant immune to sunlight', 'hostile', 'husk', 20, 3, 0, 'common', 'desert', 0, 0, '["rotten_flesh","sand"]', 5, 2),
('stray', 'Stray', 'Frozen skeleton variant that shoots slowness arrows', 'hostile', 'stray', 20, 4, 0, 'uncommon', 'ice_plains', 0, 0, '["bone","arrow","slowness_arrow"]', 5, 3),
('zombified_piglin', 'Zombified Piglin', 'Neutral undead piglin found in the Nether', 'neutral', 'zombified_piglin', 20, 8, 0, 'common', 'nether', 0, 0, '["rotten_flesh","gold_nugget","gold_ingot"]', 5, 3),
('ghast', 'Ghast', 'Large flying jellyfish-like mob that shoots fireballs', 'hostile', 'ghast', 10, 17, 0, 'uncommon', 'nether', 0, 1, '["ghast_tear","gunpowder"]', 5, 5),
('magma_cube', 'Magma Cube', 'Bouncing hostile mob made of magma', 'hostile', 'magma_cube', 16, 6, 0, 'common', 'nether', 1, 0, '["magma_cream"]', 4, 3),
('slime', 'Slime', 'Bouncing hostile mob that splits when killed', 'hostile', 'slime', 16, 4, 0, 'uncommon', 'swamp', 0, 0, '["slimeball"]', 4, 2),
('silverfish', 'Silverfish', 'Small hostile insect that hides in stone blocks', 'hostile', 'silverfish', 8, 1, 0, 'uncommon', 'stronghold', 0, 0, '[]', 5, 2),
('endermite', 'Endermite', 'Small hostile insect spawned by ender pearls', 'hostile', 'endermite', 8, 2, 0, 'rare', 'end', 0, 0, '[]', 3, 2),
('shulker', 'Shulker', 'End city mob that shoots homing projectiles', 'hostile', 'shulker', 30, 4, 0, 'rare', 'end', 0, 0, '["shulker_shell"]', 5, 7),
('vindicator', 'Vindicator', 'Axe-wielding illager found in woodland mansions', 'hostile', 'vindicator', 24, 13, 0, 'rare', 'mansion', 0, 0, '["emerald","iron_axe"]', 5, 6),
('evoker', 'Evoker', 'Spell-casting illager that summons vexes', 'hostile', 'evoker', 24, 6, 0, 'rare', 'mansion', 0, 0, '["emerald","totem_of_undying"]', 10, 7),
('vex', 'Vex', 'Small flying hostile mob summoned by evokers', 'hostile', 'vex', 14, 9, 0, 'rare', 'mansion', 0, 1, '[]', 3, 5),
('pillager', 'Pillager', 'Crossbow-wielding illager that raids villages', 'hostile', 'pillager', 24, 5, 0, 'uncommon', 'outpost', 0, 0, '["arrow","crossbow","emerald"]', 5, 4),
('ravager', 'Ravager', 'Large beast ridden by pillagers during raids', 'hostile', 'ravager', 100, 12, 0, 'rare', 'outpost', 0, 0, '["saddle"]', 20, 7),

-- New Mobs (1.20+)
('armadillo', 'Armadillo', 'Rolling defensive creature that drops scutes for wolf armor', 'passive', 'armadillo', 12, 0, 0, 'uncommon', 'savanna', 0, 0, '["armadillo_scute"]', 1, 1),
('axolotl', 'Axolotl', 'Aquatic amphibian that helps fight underwater hostile mobs', 'passive', 'axolotl', 14, 2, 0, 'uncommon', 'lush_caves', 1, 0, '[]', 1, 2),
('cod', 'Cod', 'Common fish found in ocean and river biomes', 'passive', 'cod', 3, 0, 0, 'common', 'ocean', 1, 0, '["raw_cod","bone_meal"]', 1, 1);

-- ============================================
-- POPULATE ITEMS TABLE
-- ============================================
INSERT INTO items (item_id, name, description, item_category, minecraft_id, max_stack_size, durability, damage, armor_value, food_value, saturation, is_craftable, rarity, value, enchantable) VALUES

-- Resources
('emerald', 'Emerald', 'Precious green gem used for trading with villagers', 'resource', 'emerald', 64, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 100, 0),
('diamond', 'Diamond', 'Rare and valuable blue gem found deep underground', 'resource', 'diamond', 64, NULL, NULL, NULL, NULL, NULL, 0, 'rare', 500, 0),
('iron_ingot', 'Iron Ingot', 'Refined iron used for crafting tools and armor', 'resource', 'iron_ingot', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 10, 0),
('gold_ingot', 'Gold Ingot', 'Shiny metal ingot used for crafting and trading', 'resource', 'gold_ingot', 64, NULL, NULL, NULL, NULL, NULL, 1, 'uncommon', 50, 0),
('coal', 'Coal', 'Black mineral used as fuel and for crafting torches', 'resource', 'coal', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 2, 0),
('redstone', 'Redstone', 'Electrical component for building circuits and contraptions', 'resource', 'redstone', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 5, 0),
('lapis_lazuli', 'Lapis Lazuli', 'Blue dye and enchanting material', 'resource', 'lapis_lazuli', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 8, 0),
('netherite_ingot', 'Netherite Ingot', 'Rare upgrade material stronger than diamond', 'resource', 'netherite_ingot', 64, NULL, NULL, NULL, NULL, NULL, 1, 'legendary', 2000, 0),
('ender_pearl', 'Ender Pearl', 'Teleportation item dropped by endermen', 'resource', 'ender_pearl', 16, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 80, 0),
('blaze_rod', 'Blaze Rod', 'Crafting material dropped by blazes', 'resource', 'blaze_rod', 64, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 60, 0),

-- Weapons
('diamond_sword', 'Diamond Sword', 'Powerful melee weapon made from diamonds', 'weapon', 'diamond_sword', 1, 1561, 7, NULL, NULL, NULL, 1, 'rare', 200, 1),
('iron_sword', 'Iron Sword', 'Standard melee weapon made from iron', 'weapon', 'iron_sword', 1, 250, 6, NULL, NULL, NULL, 1, 'common', 50, 1),
('golden_sword', 'Golden Sword', 'Fast but weak sword made from gold', 'weapon', 'golden_sword', 1, 32, 4, NULL, NULL, NULL, 1, 'uncommon', 75, 1),
('stone_sword', 'Stone Sword', 'Basic melee weapon made from cobblestone', 'weapon', 'stone_sword', 1, 131, 5, NULL, NULL, NULL, 1, 'common', 15, 1),
('netherite_sword', 'Netherite Sword', 'The strongest melee weapon in the game', 'weapon', 'netherite_sword', 1, 2031, 8, NULL, NULL, NULL, 1, 'legendary', 1000, 1),
('bow', 'Bow', 'Ranged weapon that shoots arrows', 'weapon', 'bow', 1, 384, 0, NULL, NULL, NULL, 1, 'common', 30, 1),
('crossbow', 'Crossbow', 'Advanced ranged weapon with higher damage', 'weapon', 'crossbow', 1, 326, 0, NULL, NULL, NULL, 1, 'uncommon', 75, 1),
('trident', 'Trident', 'Rare aquatic weapon that can be thrown', 'weapon', 'trident', 1, 250, 9, NULL, NULL, NULL, 0, 'rare', 300, 1),

-- Tools
('diamond_pickaxe', 'Diamond Pickaxe', 'Fast mining tool for stone and ores', 'tool', 'diamond_pickaxe', 1, 1561, 0, NULL, NULL, NULL, 1, 'rare', 150, 1),
('iron_pickaxe', 'Iron Pickaxe', 'Standard mining tool', 'tool', 'iron_pickaxe', 1, 250, 0, NULL, NULL, NULL, 1, 'common', 40, 1),
('diamond_axe', 'Diamond Axe', 'Fast woodcutting and combat tool', 'tool', 'diamond_axe', 1, 1561, 9, NULL, NULL, NULL, 1, 'rare', 150, 1),
('iron_axe', 'Iron Axe', 'Standard woodcutting tool', 'tool', 'iron_axe', 1, 250, 0, NULL, NULL, NULL, 1, 'common', 40, 1),
('diamond_shovel', 'Diamond Shovel', 'Fast digging tool for dirt and sand', 'tool', 'diamond_shovel', 1, 1561, 0, NULL, NULL, NULL, 1, 'rare', 120, 1),
('fishing_rod', 'Fishing Rod', 'Tool for catching fish and treasure', 'tool', 'fishing_rod', 1, 64, 0, NULL, NULL, NULL, 1, 'common', 20, 1),
('shears', 'Shears', 'Tool for harvesting wool and leaves', 'tool', 'shears', 1, 238, 0, NULL, NULL, NULL, 1, 'common', 25, 0),
('flint_and_steel', 'Flint and Steel', 'Fire-starting tool', 'tool', 'flint_and_steel', 1, 64, 0, NULL, NULL, NULL, 1, 'common', 15, 0),

-- Armor
('diamond_helmet', 'Diamond Helmet', 'Head protection made from diamonds', 'armor', 'diamond_helmet', 1, 363, NULL, 3, NULL, NULL, 1, 'rare', 250, 1),
('diamond_chestplate', 'Diamond Chestplate', 'Body protection made from diamonds', 'armor', 'diamond_chestplate', 1, 528, NULL, 8, NULL, NULL, 1, 'rare', 400, 1),
('diamond_leggings', 'Diamond Leggings', 'Leg protection made from diamonds', 'armor', 'diamond_leggings', 1, 495, NULL, 6, NULL, NULL, 1, 'rare', 350, 1),
('diamond_boots', 'Diamond Boots', 'Foot protection made from diamonds', 'armor', 'diamond_boots', 1, 429, NULL, 3, NULL, NULL, 1, 'rare', 200, 1),
('iron_helmet', 'Iron Helmet', 'Standard head protection', 'armor', 'iron_helmet', 1, 165, NULL, 2, NULL, NULL, 1, 'common', 75, 1),
('iron_chestplate', 'Iron Chestplate', 'Standard body protection', 'armor', 'iron_chestplate', 1, 240, NULL, 6, NULL, NULL, 1, 'common', 120, 1),

-- Food
('apple', 'Apple', 'Basic fruit that restores hunger', 'food', 'apple', 64, NULL, NULL, NULL, 4, 2.4, 0, 'common', 5, 0),
('bread', 'Bread', 'Filling food made from wheat', 'food', 'bread', 64, NULL, NULL, NULL, 5, 6.0, 1, 'common', 10, 0),
('cooked_beef', 'Cooked Beef', 'Nutritious cooked meat from cows', 'food', 'cooked_beef', 64, NULL, NULL, NULL, 8, 12.8, 0, 'common', 15, 0),
('cooked_porkchop', 'Cooked Porkchop', 'Tasty cooked meat from pigs', 'food', 'cooked_porkchop', 64, NULL, NULL, NULL, 8, 12.8, 0, 'common', 15, 0),
('golden_apple', 'Golden Apple', 'Rare food that grants regeneration and absorption', 'food', 'golden_apple', 64, NULL, NULL, NULL, 4, 9.6, 1, 'rare', 200, 0),
('enchanted_golden_apple', 'Enchanted Golden Apple', 'Legendary food with powerful effects', 'food', 'enchanted_golden_apple', 64, NULL, NULL, NULL, 4, 9.6, 0, 'legendary', 1000, 0),
('cookie', 'Cookie', 'Sweet treat made from wheat and cocoa', 'food', 'cookie', 64, NULL, NULL, NULL, 2, 0.4, 1, 'common', 8, 0),
('cake', 'Cake', 'Placeable food item with multiple servings', 'food', 'cake', 1, NULL, NULL, NULL, 14, 2.8, 1, 'uncommon', 40, 0),
('melon_slice', 'Melon Slice', 'Refreshing fruit that restores a small amount of hunger', 'food', 'melon_slice', 64, NULL, NULL, NULL, 2, 1.2, 0, 'common', 3, 0),
('carrot', 'Carrot', 'Orange vegetable that can be eaten or used for breeding', 'food', 'carrot', 64, NULL, NULL, NULL, 3, 3.6, 0, 'common', 5, 0),

-- Blocks
('dirt', 'Dirt', 'Basic earth block found everywhere', 'block', 'dirt', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 1, 0),
('stone', 'Stone', 'Basic stone block', 'block', 'stone', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 1, 0),
('cobblestone', 'Cobblestone', 'Stone block dropped when mining stone', 'block', 'cobblestone', 64, NULL, NULL, NULL, NULL, NULL, 0, 'common', 1, 0),
('oak_planks', 'Oak Planks', 'Wooden planks for building', 'block', 'oak_planks', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 2, 0),
('glass', 'Glass', 'Transparent block made from sand', 'block', 'glass', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 5, 0),
('tnt', 'TNT', 'Explosive block activated by fire or redstone', 'block', 'tnt', 64, NULL, NULL, NULL, NULL, NULL, 1, 'uncommon', 50, 0),
('torch', 'Torch', 'Light source made from coal and sticks', 'block', 'torch', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 2, 0),
('glowstone', 'Glowstone', 'Bright block found in the Nether', 'block', 'glowstone', 64, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 25, 0),
('obsidian', 'Obsidian', 'Extremely tough block created by lava and water', 'block', 'obsidian', 64, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 40, 0),
('bedrock', 'Bedrock', 'Indestructible block at the bottom of the world', 'block', 'bedrock', 64, NULL, NULL, NULL, NULL, NULL, 0, 'legendary', 0, 0),

-- Misc
('bucket', 'Bucket', 'Container for carrying liquids', 'misc', 'bucket', 16, NULL, NULL, NULL, NULL, NULL, 1, 'common', 15, 0),
('water_bucket', 'Water Bucket', 'Bucket filled with water', 'misc', 'water_bucket', 1, NULL, NULL, NULL, NULL, NULL, 0, 'common', 20, 0),
('lava_bucket', 'Lava Bucket', 'Bucket filled with lava', 'misc', 'lava_bucket', 1, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 50, 0),
('compass', 'Compass', 'Navigation tool that points to world spawn', 'misc', 'compass', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 30, 0),
('clock', 'Clock', 'Device that shows the current time', 'misc', 'clock', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 30, 0),
('map', 'Map', 'Shows explored terrain', 'misc', 'map', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 40, 0),
('saddle', 'Saddle', 'Allows riding horses, pigs, and other mobs', 'misc', 'saddle', 1, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 100, 0),
('name_tag', 'Name Tag', 'Allows naming and preventing despawn of mobs', 'misc', 'name_tag', 64, NULL, NULL, NULL, NULL, NULL, 0, 'uncommon', 75, 0),
('lead', 'Lead', 'Rope for leading animals', 'misc', 'lead', 64, NULL, NULL, NULL, NULL, NULL, 1, 'common', 20, 0),
('elytra', 'Elytra', 'Wings that allow gliding through the air', 'misc', 'elytra', 1, 432, NULL, NULL, NULL, NULL, 0, 'legendary', 1000, 1),
('totem_of_undying', 'Totem of Undying', 'One-time use item that prevents death', 'misc', 'totem_of_undying', 1, NULL, NULL, NULL, NULL, NULL, 0, 'legendary', 800, 0),
('nether_star', 'Nether Star', 'Rare crafting material dropped by the Wither', 'misc', 'nether_star', 64, NULL, NULL, NULL, NULL, NULL, 0, 'legendary', 5000, 0);

-- ============================================
-- POPULATE ACTIONS TABLE
-- ============================================
INSERT INTO actions (action_id, action_type, name, description, default_params, required_params, requires_op, cooldown_seconds, category, rarity) VALUES

-- Time actions
('set_time_day', 'set_time', 'Set Time to Day', 'Changes the time to early morning (1000 ticks)', '{"time": "day"}', '["time"]', 0, 0, 'world', 'common'),
('set_time_night', 'set_time', 'Set Time to Night', 'Changes the time to early evening (13000 ticks)', '{"time": "night"}', '["time"]', 0, 0, 'world', 'common'),
('set_time_noon', 'set_time', 'Set Time to Noon', 'Changes the time to midday (6000 ticks)', '{"time": 6000}', '["time"]', 0, 0, 'world', 'common'),
('set_time_midnight', 'set_time', 'Set Time to Midnight', 'Changes the time to midnight (18000 ticks)', '{"time": 18000}', '["time"]', 0, 0, 'world', 'common'),
('set_time_sunrise', 'set_time', 'Set Time to Sunrise', 'Changes the time to sunrise (0 ticks)', '{"time": 0}', '["time"]', 0, 0, 'world', 'common'),
('set_time_sunset', 'set_time', 'Set Time to Sunset', 'Changes the time to sunset (12000 ticks)', '{"time": 12000}', '["time"]', 0, 0, 'world', 'common'),

-- Weather actions
('set_weather_clear', 'set_weather', 'Clear Weather', 'Makes the weather sunny and clear', '{"weather": "clear"}', '["weather"]', 0, 60, 'world', 'common'),
('set_weather_rain', 'set_weather', 'Rain', 'Makes it rain (snow in cold biomes)', '{"weather": "rain"}', '["weather"]', 0, 60, 'world', 'common'),
('set_weather_thunder', 'set_weather', 'Thunder Storm', 'Summons a thunderstorm with lightning', '{"weather": "thunder"}', '["weather"]', 0, 120, 'world', 'uncommon'),

-- Teleport actions
('teleport_spawn', 'teleport', 'Teleport to Spawn', 'Teleports player to world spawn point', '{"x": 0, "y": 64, "z": 0}', '["player"]', 0, 300, 'player', 'uncommon'),
('teleport_home', 'teleport', 'Teleport Home', 'Teleports player to their bed spawn location', '{}', '["player"]', 0, 600, 'player', 'rare'),
('teleport_nether', 'teleport', 'Teleport to Nether', 'Teleports player to Nether spawn', '{}', '["player"]', 0, 1800, 'player', 'rare'),
('teleport_end', 'teleport', 'Teleport to End', 'Teleports player to the End dimension', '{}', '["player"]', 1, 3600, 'player', 'legendary'),

-- Broadcast actions
('broadcast_message', 'broadcast', 'Broadcast Message', 'Sends a message to all players on the server', '{}', '["message"]', 0, 10, 'server', 'common'),

-- Player effects
('give_regeneration', 'effect', 'Regeneration', 'Grants regeneration effect (heal over time)', '{"effect": "regeneration", "duration": 30, "amplifier": 1}', '["player"]', 0, 300, 'player', 'uncommon'),
('give_speed', 'effect', 'Speed Boost', 'Grants speed effect for faster movement', '{"effect": "speed", "duration": 60, "amplifier": 1}', '["player"]', 0, 300, 'player', 'uncommon'),
('give_jump_boost', 'effect', 'Jump Boost', 'Grants jump boost for higher jumping', '{"effect": "jump_boost", "duration": 60, "amplifier": 2}', '["player"]', 0, 300, 'player', 'uncommon'),
('give_night_vision', 'effect', 'Night Vision', 'Grants night vision to see in darkness', '{"effect": "night_vision", "duration": 180, "amplifier": 0}', '["player"]', 0, 600, 'player', 'rare'),
('give_strength', 'effect', 'Strength', 'Grants strength for increased melee damage', '{"effect": "strength", "duration": 180, "amplifier": 1}', '["player"]', 0, 600, 'player', 'rare'),
('give_resistance', 'effect', 'Resistance', 'Grants resistance to reduce damage taken', '{"effect": "resistance", "duration": 180, "amplifier": 0}', '["player"]', 0, 600, 'player', 'rare'),
('give_fire_resistance', 'effect', 'Fire Resistance', 'Grants immunity to fire and lava damage', '{"effect": "fire_resistance", "duration": 180, "amplifier": 0}', '["player"]', 0, 600, 'player', 'rare'),
('give_water_breathing', 'effect', 'Water Breathing', 'Grants ability to breathe underwater', '{"effect": "water_breathing", "duration": 300, "amplifier": 0}', '["player"]', 0, 600, 'player', 'rare'),
('give_invisibility', 'effect', 'Invisibility', 'Makes the player invisible to mobs', '{"effect": "invisibility", "duration": 120, "amplifier": 0}', '["player"]', 0, 900, 'player', 'legendary'),
('give_levitation', 'effect', 'Levitation', 'Makes the player float upward', '{"effect": "levitation", "duration": 10, "amplifier": 0}', '["player"]', 0, 600, 'player', 'uncommon'),

-- Game mode changes
('gamemode_survival', 'gamemode', 'Survival Mode', 'Changes player to survival mode', '{"mode": "survival"}', '["player"]', 1, 0, 'player', 'uncommon'),
('gamemode_creative', 'gamemode', 'Creative Mode', 'Changes player to creative mode', '{"mode": "creative"}', '["player"]', 1, 0, 'player', 'uncommon'),
('gamemode_adventure', 'gamemode', 'Adventure Mode', 'Changes player to adventure mode', '{"mode": "adventure"}', '["player"]', 1, 0, 'player', 'uncommon'),

-- Admin actions
('server_restart', 'server_control', 'Restart Server', 'Restarts the Minecraft server (admin only)', '{}', '[]', 1, 0, 'admin', 'legendary'),
('backup_world', 'server_control', 'Backup World', 'Creates a backup of the world save', '{}', '[]', 1, 3600, 'admin', 'legendary'),
('save_all', 'server_control', 'Save World', 'Forces the server to save all chunks', '{}', '[]', 1, 300, 'admin', 'rare');

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
SELECT * FROM items WHERE item_category = 'weapon' ORDER BY damage DESC NULLS LAST;

-- View: Food items
CREATE VIEW food_items AS
SELECT * FROM items WHERE item_category = 'food' ORDER BY food_value DESC NULLS LAST;

-- View: Common queries
-- SELECT * FROM hostile_mobs;
-- SELECT * FROM weapons;
-- SELECT name, description, food_value FROM food_items WHERE food_value >= 5;
-- SELECT * FROM mobs WHERE minecraft_id = 'piglin';
-- SELECT * FROM items WHERE rarity IN ('rare', 'legendary') ORDER BY value DESC;

