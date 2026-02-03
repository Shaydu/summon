# Adding Mobs to Summon Dashboard

This guide explains how to add new Minecraft mobs to the Summon web dashboard at `https://10.0.0.227:8080/`

## Overview

The Summon system displays mobs on the web dashboard by pulling data from the PostgreSQL database. To add a new mob, you need to:

1. Prepare a mob image file (PNG format)
2. Add the mob to the database with metadata
3. The dashboard automatically displays the new mob

## Quick Start

### Step 1: Prepare Your Image

- Format: PNG image
- Recommended size: 100x100px to 200x200px
- Keep file size reasonable (under 500KB)
- Name the file after the Minecraft entity ID (lowercase, underscores for spaces)

Examples:
- `warden.png`
- `iron_golem.png`
- `ender_dragon.png`

### Step 2: Add Mob to Database

Use the provided script:

```bash
cd /home/doo/minecraft-bedrock-server/summon
python3 scripts/add_mob.py \
  --minecraft-id warden \
  --name "Warden" \
  --description "A powerful hostile mob from the Deep Dark" \
  --mob-type hostile \
  --health 500 \
  --damage 32 \
  --rarity legendary \
  --biome deep_dark \
  --difficulty 5 \
  --image-path /path/to/warden.png
```

### Step 3: Refresh the Dashboard

Visit `https://10.0.0.227:8080/` and refresh the page. Your new mob will appear!

## Script Arguments

### Required Arguments:
- `--minecraft-id` - Minecraft entity ID (used internally, lowercase with underscores)
- `--name` - Display name on the dashboard

### Optional Arguments:
- `--description` - Detailed description of the mob
- `--mob-type` - Type: `hostile`, `passive`, or `neutral` (default: `passive`)
- `--health` - HP value (default: 20)
- `--damage` - Damage per hit (default: 0)
- `--armor` - Armor rating (default: 0)
- `--rarity` - Rarity level: `common`, `uncommon`, `rare`, `legendary` (default: `common`)
- `--biome` - Associated biome (default: `any`)
- `--difficulty` - Difficulty rating 1-5 (default: 0)
- `--image-path` - Path to PNG image file to copy to mob_images directory

## Examples

### Example 1: Simple Mob (Passive)

```bash
python3 scripts/add_mob.py \
  --minecraft-id sheep \
  --name "Sheep" \
  --description "A harmless woolly animal" \
  --mob-type passive \
  --health 10 \
  --image-path ~/Downloads/sheep.png
```

### Example 2: Boss Mob (Hostile)

```bash
python3 scripts/add_mob.py \
  --minecraft-id wither \
  --name "Wither" \
  --description "A three-headed undead boss" \
  --mob-type hostile \
  --health 300 \
  --damage 16 \
  --rarity legendary \
  --difficulty 5 \
  --biome nether \
  --image-path ~/Downloads/wither.png
```

### Example 3: Neutral Mob

```bash
python3 scripts/add_mob.py \
  --minecraft-id bee \
  --name "Bee" \
  --description "A small flying insect that pollinates flowers" \
  --mob-type neutral \
  --health 10 \
  --damage 2 \
  --rarity uncommon \
  --biome flower_forest \
  --image-path ~/Downloads/bee.png
```

## Image Management

Images are stored in: `/home/doo/minecraft-bedrock-server/summon/web/mob_images/`

The script automatically copies your image to this directory with the correct filename based on `--minecraft-id`.

You can also manually add images:

```bash
cp /path/to/your/image.png /home/doo/minecraft-bedrock-server/summon/web/mob_images/minecraft_id.png
```

## Verification

To verify a mob was added successfully:

```bash
# Check the database
python3 scripts/check_mob.py --minecraft-id warden

# Or visit the dashboard and look for your mob in the list
# https://10.0.0.227:8080/
```

## Updating an Existing Mob

To update mob information (like stats or description), edit the database directly or delete and re-add:

```bash
# Delete the mob
python3 scripts/delete_mob.py --minecraft-id warden

# Re-add with new information
python3 scripts/add_mob.py --minecraft-id warden --name "Warden" ...
```

## Troubleshooting

### Mob doesn't appear on dashboard
- Refresh the page (Ctrl+F5 or Cmd+Shift+R)
- Check the database connection (PostgreSQL must be running)
- Verify the mob was inserted: `python3 scripts/check_mob.py --minecraft-id your_mob_id`

### Image not displaying
- Verify the image file exists: `ls -la /home/doo/minecraft-bedrock-server/summon/web/mob_images/your_mob_id.png`
- Check file permissions: should be readable by the web server user
- Try a different image format (ensure it's valid PNG)

### Database connection error
- Ensure PostgreSQL is running and accessible
- Check environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

## Database Schema

The mobs table contains the following fields:

```sql
CREATE TABLE mobs (
    mob_id VARCHAR(255) PRIMARY KEY,
    minecraft_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    mob_type VARCHAR(50),           -- 'hostile', 'passive', 'neutral'
    health INTEGER,
    damage INTEGER,
    armor INTEGER,
    rarity VARCHAR(50),              -- 'common', 'uncommon', 'rare', 'legendary'
    biome VARCHAR(255),
    can_swim BOOLEAN,
    can_fly BOOLEAN,
    drops_items TEXT,
    xp_reward INTEGER,
    difficulty_rating INTEGER,
    image_url VARCHAR(500)
);
```

## Integration with Website

The web dashboard (`website.py`) automatically:
1. Queries all mobs from the database
2. Displays them with their images from `/mob_images/`
3. Shows summon counts for each mob
4. Allows filtering discovered vs all mobs

No code changes needed when adding mobs — just update the database!
