#!/usr/bin/env python3
"""
Migrate game objects from docs/game_objects.db.sql to PostgreSQL database.
This script parses the SQLite INSERT statements and imports them into PostgreSQL.
"""

import re
import os
import summon_db

def get_image_url(minecraft_id: str, image_type: str = 'mob'):
    """
    Get the image URL for a mob or item, preferring animated GIFs over PNGs.
    
    Args:
        minecraft_id: The minecraft ID (e.g., 'zombie', 'diamond_sword')
        image_type: 'mob' or 'item'
    
    Returns:
        Image URL path or None
    """
    base_dir = 'mob' if image_type == 'mob' else 'items'
    
    # Check for animated GIF first
    gif_path = f"{base_dir}/{minecraft_id}.gif"
    if os.path.exists(gif_path):
        return f"/{gif_path}"
    
    # Fall back to PNG
    png_path = f"{base_dir}/{minecraft_id}.png"
    if os.path.exists(png_path):
        return f"/{png_path}"
    
    return None

def parse_sql_file(filepath):
    """Parse the SQL file and extract mobs, items, and actions data."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    mobs_data = []
    items_data = []
    actions_data = []
    
    # Find the mobs INSERT section - it ends with a semicolon followed by comment
    mobs_start = content.find("INSERT INTO mobs")
    if mobs_start != -1:
        # Find the end - look for "); followed by newline and --"
        mobs_end = content.find(");\n\n--", mobs_start)
        if mobs_end != -1:
            mobs_section = content[mobs_start:mobs_end]
            
            # Extract each mob entry - they start with \n(' and end with ),
            lines = mobs_section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("('") and "," in line:
                    # Remove trailing comma or semicolon
                    if line.endswith(','):
                        line = line[:-1]
                    elif line.endswith(');'):
                        line = line[:-2]
                    
                    # Parse the tuple
                    try:
                        # Add parens back and eval it
                        mob_tuple = eval(line)
                        if len(mob_tuple) >= 15:
                            mob = {
                                'mob_id': mob_tuple[0],
                                'name': mob_tuple[1],
                                'description': mob_tuple[2],
                                'mob_type': mob_tuple[3],
                                'minecraft_id': mob_tuple[4],
                                'health': int(mob_tuple[5]),
                                'damage': int(mob_tuple[6]),
                                'armor': int(mob_tuple[7]),
                                'rarity': mob_tuple[8],
                                'biome': mob_tuple[9],
                                'can_swim': int(mob_tuple[10]),
                                'can_fly': int(mob_tuple[11]),
                                'drops_items': mob_tuple[12],
                                'xp_reward': int(mob_tuple[13]),
                                'difficulty_rating': int(mob_tuple[14])
                            }
                            mobs_data.append(mob)
                    except Exception as e:
                        print(f"    Warning: Failed to parse mob line: {line[:50]}... Error: {e}")
    
    # Find the items INSERT section
    items_start = content.find("INSERT INTO items")
    if items_start != -1:
        items_end = content.find(");\n", items_start + 100)  # Skip the column definition line
        if items_end != -1:
            items_section = content[items_start:items_end]
            
            lines = items_section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("('") and "," in line:
                    if line.endswith(','):
                        line = line[:-1]
                    elif line.endswith(');'):
                        line = line[:-2]
                    
                    try:
                        # Parse tuple - items have varying length due to NULL values
                        item_tuple = eval(line)
                        if len(item_tuple) >= 5:
                            item = {
                                'item_id': item_tuple[0],
                                'name': item_tuple[1],
                                'description': item_tuple[2],
                                'item_category': item_tuple[3],
                                'minecraft_id': item_tuple[4],
                            }
                            items_data.append(item)
                    except Exception as e:
                        print(f"    Warning: Failed to parse item line: {line[:50]}... Error: {e}")
    
    return mobs_data, items_data, actions_data


def import_mobs(mobs_data):
    """Import mobs into the database."""
    existing_mobs = summon_db.get_all_mobs()
    existing_ids = {m.get('minecraft_id') for m in existing_mobs}
    
    added = 0
    skipped = 0
    
    for mob in mobs_data:
        if mob['minecraft_id'] in existing_ids:
            skipped += 1
            continue
        
        # Get image URL - prefer animated GIF
        image_url = get_image_url(mob['minecraft_id'], 'mob')
        
        try:
            summon_db.insert_mob(
                minecraft_id=mob['minecraft_id'],
                name=mob['name'],
                description=mob['description'],
                mob_type=mob['mob_type'],
                health=mob['health'],
                damage=mob['damage'],
                armor=mob['armor'],
                rarity=mob['rarity'],
                biome=mob['biome'],
                can_swim=bool(mob['can_swim']),
                can_fly=bool(mob['can_fly']),
                drops_items=mob['drops_items'],
                xp_reward=mob['xp_reward'],
                difficulty_rating=mob['difficulty_rating']
            )
            
            # Update image URL if found
            if image_url:
                conn = summon_db.get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE mobs SET image_url = %s WHERE minecraft_id = %s",
                    (image_url, mob['minecraft_id'])
                )
                conn.commit()
                cur.close()
                conn.close()
                
            added += 1
            image_indicator = "🎬" if image_url and image_url.endswith('.gif') else "🖼️" if image_url else "❌"
            print(f"  ✓ Added mob: {mob['minecraft_id']:20} ({mob['name']:20}) {image_indicator}")
        except Exception as e:
            print(f"  ✗ Failed to add mob {mob['minecraft_id']}: {e}")
    
    return added, skipped


def import_items(items_data):
    """Import items into the database."""
    existing_items = summon_db.get_all_items()
    existing_ids = {i.get('minecraft_id') for i in existing_items}
    
    added = 0
    skipped = 0
    
    for item in items_data:
        if item['minecraft_id'] in existing_ids:
            skipped += 1
            continue
        
        # Get image URL - prefer animated GIF
        image_url = get_image_url(item['minecraft_id'], 'item')
        
        try:
            summon_db.insert_item(
                minecraft_id=item['minecraft_id'],
                name=item['name'],
                description=item['description'],
                item_category=item['item_category']
            )
            
            # Update image URL if found
            if image_url:
                conn = summon_db.get_connection()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE items SET image_url = %s WHERE minecraft_id = %s",
                    (image_url, item['minecraft_id'])
                )
                conn.commit()
                cur.close()
                conn.close()
            
            added += 1
            image_indicator = "🎬" if image_url and image_url.endswith('.gif') else "🖼️" if image_url else "❌"
            print(f"  ✓ Added item: {item['minecraft_id']:20} ({item['name']:20}) {image_indicator}")
        except Exception as e:
            print(f"  ✗ Failed to add item {item['minecraft_id']}: {e}")
    
    return added, skipped


def main():
    """Main migration function."""
    print("=" * 60)
    print("MIGRATING GAME OBJECTS FROM docs/game_objects.db.sql")
    print("=" * 60)
    print()
    
    # Parse the SQL file
    print("Parsing SQL file...")
    mobs_data, items_data, actions_data = parse_sql_file('docs/game_objects.db.sql')
    print(f"  Found {len(mobs_data)} mobs")
    print(f"  Found {len(items_data)} items")
    print(f"  Found {len(actions_data)} actions")
    print()
    
    # Import mobs
    print("Importing mobs...")
    mobs_added, mobs_skipped = import_mobs(mobs_data)
    print(f"  Added: {mobs_added}, Skipped: {mobs_skipped}")
    print()
    
    # Import items
    print("Importing items...")
    items_added, items_skipped = import_items(items_data)
    print(f"  Added: {items_added}, Skipped: {items_skipped}")
    print()
    
    # Summary
    print("=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    print(f"Total mobs in database: {len(summon_db.get_all_mobs())}")
    print(f"Total items in database: {len(summon_db.get_all_items())}")
    print()


if __name__ == '__main__':
    main()
