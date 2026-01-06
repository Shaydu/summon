#!/usr/bin/env python3
"""
Populate missing mobs and items into the database based on the mobs-and-items.md file.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summon_db

# Complete list of mobs from docs/mobs-and-items.md
MOBS_DATA = [
    # Passive mobs
    {"minecraft_id": "allay", "name": "Allay", "mob_type": "Passive"},
    {"minecraft_id": "armadillo", "name": "Armadillo", "mob_type": "Passive"},
    {"minecraft_id": "axolotl", "name": "Axolotl", "mob_type": "Passive"},
    {"minecraft_id": "bat", "name": "Bat", "mob_type": "Passive"},
    {"minecraft_id": "camel", "name": "Camel", "mob_type": "Passive"},
    {"minecraft_id": "cat", "name": "Cat", "mob_type": "Passive"},
    {"minecraft_id": "chicken", "name": "Chicken", "mob_type": "Passive"},
    {"minecraft_id": "cod", "name": "Cod", "mob_type": "Passive"},
    {"minecraft_id": "cow", "name": "Cow", "mob_type": "Passive"},
    {"minecraft_id": "donkey", "name": "Donkey", "mob_type": "Passive"},
    {"minecraft_id": "frog", "name": "Frog", "mob_type": "Passive"},
    {"minecraft_id": "glow_squid", "name": "Glow Squid", "mob_type": "Passive"},
    {"minecraft_id": "horse", "name": "Horse", "mob_type": "Passive"},
    {"minecraft_id": "mooshroom", "name": "Mooshroom", "mob_type": "Passive"},
    {"minecraft_id": "mule", "name": "Mule", "mob_type": "Passive"},
    {"minecraft_id": "ocelot", "name": "Ocelot", "mob_type": "Passive"},
    {"minecraft_id": "parrot", "name": "Parrot", "mob_type": "Passive"},
    {"minecraft_id": "pig", "name": "Pig", "mob_type": "Passive"},
    {"minecraft_id": "pufferfish", "name": "Pufferfish", "mob_type": "Passive"},
    {"minecraft_id": "rabbit", "name": "Rabbit", "mob_type": "Passive"},
    {"minecraft_id": "salmon", "name": "Salmon", "mob_type": "Passive"},
    {"minecraft_id": "sheep", "name": "Sheep", "mob_type": "Passive"},
    {"minecraft_id": "skeleton_horse", "name": "Skeleton Horse", "mob_type": "Passive"},
    {"minecraft_id": "sniffer", "name": "Sniffer", "mob_type": "Passive"},
    {"minecraft_id": "snow_golem", "name": "Snow Golem", "mob_type": "Passive"},
    {"minecraft_id": "squid", "name": "Squid", "mob_type": "Passive"},
    {"minecraft_id": "strider", "name": "Strider", "mob_type": "Passive"},
    {"minecraft_id": "tadpole", "name": "Tadpole", "mob_type": "Passive"},
    {"minecraft_id": "tropical_fish", "name": "Tropical Fish", "mob_type": "Passive"},
    {"minecraft_id": "turtle", "name": "Turtle", "mob_type": "Passive"},
    {"minecraft_id": "villager", "name": "Villager", "mob_type": "Passive"},
    {"minecraft_id": "wandering_trader", "name": "Wandering Trader", "mob_type": "Passive"},
    
    # Hostile mobs
    {"minecraft_id": "blaze", "name": "Blaze", "mob_type": "Hostile"},
    {"minecraft_id": "cave_spider", "name": "Cave Spider", "mob_type": "Hostile"},
    {"minecraft_id": "creeper", "name": "Creeper", "mob_type": "Hostile"},
    {"minecraft_id": "drowned", "name": "Drowned", "mob_type": "Hostile"},
    {"minecraft_id": "elder_guardian", "name": "Elder Guardian", "mob_type": "Hostile"},
    {"minecraft_id": "ender_dragon", "name": "Ender Dragon", "mob_type": "Hostile"},
    {"minecraft_id": "enderman", "name": "Enderman", "mob_type": "Hostile"},
    {"minecraft_id": "endermite", "name": "Endermite", "mob_type": "Hostile"},
    {"minecraft_id": "evoker", "name": "Evoker", "mob_type": "Hostile"},
    {"minecraft_id": "ghast", "name": "Ghast", "mob_type": "Hostile"},
    {"minecraft_id": "guardian", "name": "Guardian", "mob_type": "Hostile"},
    {"minecraft_id": "hoglin", "name": "Hoglin", "mob_type": "Hostile"},
    {"minecraft_id": "husk", "name": "Husk", "mob_type": "Hostile"},
    {"minecraft_id": "iron_golem", "name": "Iron Golem", "mob_type": "Neutral"},
    {"minecraft_id": "magma_cube", "name": "Magma Cube", "mob_type": "Hostile"},
    {"minecraft_id": "phantom", "name": "Phantom", "mob_type": "Hostile"},
    {"minecraft_id": "piglin", "name": "Piglin", "mob_type": "Hostile"},
    {"minecraft_id": "pillager", "name": "Pillager", "mob_type": "Hostile"},
    {"minecraft_id": "ravager", "name": "Ravager", "mob_type": "Hostile"},
    {"minecraft_id": "shulker", "name": "Shulker", "mob_type": "Hostile"},
    {"minecraft_id": "silverfish", "name": "Silverfish", "mob_type": "Hostile"},
    {"minecraft_id": "skeleton", "name": "Skeleton", "mob_type": "Hostile"},
    {"minecraft_id": "slime", "name": "Slime", "mob_type": "Hostile"},
    {"minecraft_id": "spider", "name": "Spider", "mob_type": "Hostile"},
    {"minecraft_id": "stray", "name": "Stray", "mob_type": "Hostile"},
    {"minecraft_id": "vex", "name": "Vex", "mob_type": "Hostile"},
    {"minecraft_id": "vindicator", "name": "Vindicator", "mob_type": "Hostile"},
    {"minecraft_id": "warden", "name": "Warden", "mob_type": "Hostile"},
    {"minecraft_id": "witch", "name": "Witch", "mob_type": "Hostile"},
    {"minecraft_id": "wither", "name": "Wither", "mob_type": "Hostile"},
    {"minecraft_id": "wither_skeleton", "name": "Wither Skeleton", "mob_type": "Hostile"},
    {"minecraft_id": "wolf", "name": "Wolf", "mob_type": "Neutral"},
    {"minecraft_id": "zoglin", "name": "Zoglin", "mob_type": "Hostile"},
    {"minecraft_id": "zombie", "name": "Zombie", "mob_type": "Hostile"},
    {"minecraft_id": "zombie_villager", "name": "Zombie Villager", "mob_type": "Hostile"},
]

def insert_mob_if_missing(minecraft_id, name, mob_type):
    """Insert mob if it doesn't exist in database."""
    conn = summon_db.get_connection()
    cur = conn.cursor()
    
    # Check if mob exists
    cur.execute("SELECT COUNT(*) FROM mobs WHERE minecraft_id = %s", (minecraft_id,))
    exists = cur.fetchone()[0] > 0
    
    if not exists:
        # Insert mob with basic data (mob_id = minecraft_id)
        cur.execute("""
            INSERT INTO mobs (mob_id, name, description, mob_type, minecraft_id, health, damage, armor, rarity, biome, difficulty_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            minecraft_id,  # mob_id (same as minecraft_id)
            name,
            f"{name} - {mob_type} mob",  # description
            mob_type,  # mob_type
            minecraft_id,  # minecraft_id
            20.0,  # health (default)
            2.0,  # damage (default)
            0.0,  # armor (default)
            "Common",  # rarity
            "Overworld",  # biome
            1  # difficulty_rating
        ))
        conn.commit()
        print(f"  ✅ Added {name} ({minecraft_id})")
        cur.close()
        conn.close()
        return True
    else:
        print(f"  ✓ {name} ({minecraft_id}) already exists")
        cur.close()
        conn.close()
        return False

def main():
    print("=" * 60)
    print("Populate Missing Mobs Script")
    print("=" * 60)
    
    # Get existing mobs
    existing_mobs = summon_db.get_all_mobs()
    existing_ids = set(mob.get('minecraft_id') for mob in existing_mobs)
    
    print(f"\nCurrent mobs in database: {len(existing_ids)}")
    print(f"Mobs in documentation: {len(MOBS_DATA)}")
    
    missing_count = sum(1 for mob in MOBS_DATA if mob['minecraft_id'] not in existing_ids)
    print(f"Missing mobs: {missing_count}")
    
    if missing_count == 0:
        print("\n✅ All mobs are already in the database!")
        return
    
    print("\n" + "=" * 60)
    print("Adding missing mobs...")
    print("=" * 60)
    
    added = 0
    for mob_data in MOBS_DATA:
        if insert_mob_if_missing(
            mob_data['minecraft_id'],
            mob_data['name'],
            mob_data['mob_type']
        ):
            added += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Added {added} new mobs to database")
    print(f"📊 Total mobs now: {len(existing_ids) + added}")
    print("=" * 60)

if __name__ == '__main__':
    main()
