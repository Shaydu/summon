#!/usr/bin/env python3
"""
Download missing mob images from Minecraft Wiki.
Prefers animated GIFs over static PNGs.
"""

import os
import requests
import summon_db
import hashlib
from urllib.parse import quote

def get_wikia_url(filename):
    """Generate Wikia URL with hash-based path."""
    # Wikia uses MD5 hash for URL structure
    md5 = hashlib.md5(filename.encode()).hexdigest()
    hash_prefix = md5[0]
    hash_dir = md5[0:2]
    return f"https://static.wikia.nocookie.net/minecraft_gamepedia/images/{hash_prefix}/{hash_dir}/{quote(filename)}"

# Mob name to Wiki filename mapping (for mobs with different naming)
WIKI_NAME_MAP = {
    'cave_spider': 'CaveSpider',
    'ender_dragon': 'EnderDragon',
    'elder_guardian': 'ElderGuardian',
    'iron_golem': 'IronGolem',
    'magma_cube': 'MagmaCube',
    'polar_bear': 'PolarBear',
    'wither_skeleton': 'WitherSkeleton',
    'zombified_piglin': 'ZombifiedPiglin',
}

def get_wiki_name(minecraft_id):
    """Convert minecraft_id to Wiki face image name."""
    if minecraft_id in WIKI_NAME_MAP:
        return WIKI_NAME_MAP[minecraft_id]
    # Default: capitalize first letter of each word
    return ''.join(word.capitalize() for word in minecraft_id.split('_'))

def download_image(url, output_path):
    """Download an image from URL to output_path."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        print(f"    Error downloading {url}: {e}")
        return False

def find_and_download_image(minecraft_id, mob_name):
    """
    Try to find and download mob image from Minecraft Wiki.
    Tries GIF first (animated), then falls back to PNG.
    """
    wiki_name = get_wiki_name(minecraft_id)
    
    # Try different image filename patterns
    possible_files = [
        # Animated versions (preferred)
        f"{wiki_name}Face.gif",
        f"{wiki_name}.gif",
        # Static PNG versions
        f"{wiki_name}Face.png",
        f"{wiki_name}.png",
        f"{wiki_name}_JE2_BE2.png",
    ]
    
    for filename in possible_files:
        is_gif = filename.endswith('.gif')
        ext = '.gif' if is_gif else '.png'
        output_path = f"mob/{minecraft_id}{ext}"
        
        # Try Wikia URL with hash-based path
        url = get_wikia_url(filename)
        if download_image(url, output_path):
            indicator = "🎬" if is_gif else "🖼️"
            print(f"  {indicator} Downloaded: {mob_name:20} -> {output_path}")
            return output_path
        
        # Try direct minecraft.wiki URL
        direct_url = f"https://minecraft.wiki/images/{filename}"
        if download_image(direct_url, output_path):
            indicator = "🎬" if is_gif else "🖼️"
            print(f"  {indicator} Downloaded: {mob_name:20} -> {output_path}")
            return output_path
    
    print(f"  ✗ Not found: {mob_name:20}")
    return None

def main():
    """Main function to download missing mob images."""
    print("=" * 60)
    print("DOWNLOADING MISSING MOB IMAGES")
    print("=" * 60)
    print()
    
    # Get all mobs without images
    all_mobs = summon_db.get_all_mobs()
    missing_images = [m for m in all_mobs if not m.get('image_url')]
    
    print(f"Mobs missing images: {len(missing_images)}")
    print()
    
    if not missing_images:
        print("All mobs have images!")
        return
    
    # Create mob directory if it doesn't exist
    os.makedirs('mob', exist_ok=True)
    
    downloaded = 0
    failed = []
    
    conn = summon_db.get_connection()
    cur = conn.cursor()
    
    for mob in missing_images:
        minecraft_id = mob.get('minecraft_id')
        name = mob.get('name', minecraft_id)
        
        image_path = find_and_download_image(minecraft_id, name)
        
        if image_path:
            # Update database with image URL
            cur.execute(
                "UPDATE mobs SET image_url = %s WHERE minecraft_id = %s",
                (f"/{image_path}", minecraft_id)
            )
            downloaded += 1
        else:
            failed.append(minecraft_id)
    
    conn.commit()
    cur.close()
    conn.close()
    
    print()
    print("=" * 60)
    print(f"Downloaded: {downloaded}/{len(missing_images)}")
    if failed:
        print(f"Failed: {len(failed)}")
        print(f"  {', '.join(failed)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
