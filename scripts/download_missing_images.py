#!/usr/bin/env python3
"""
Download missing mob and item images from Minecraft Wiki.
"""
import os
import sys
import requests
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summon_db

# Minecraft Wiki image URLs
WIKI_BASE = "https://minecraft.wiki"
STATIC_BASE = "https://static.wikia.nocookie.net/minecraft_gamepedia"

def download_image(minecraft_id: str, output_dir: str, is_item: bool = False) -> bool:
    """
    Try to download image for a Minecraft entity/item.
    Returns True if successful.
    """
    output_path = Path(output_dir) / f"{minecraft_id}.png"
    
    if output_path.exists():
        print(f"  ✓ {minecraft_id}.png already exists")
        return True
    
    # Format the name for wiki URLs (capitalize words, handle underscores)
    wiki_name = minecraft_id.replace('_', ' ').title().replace(' ', '_')
    
    # Try multiple URL patterns
    url_patterns = [
        # Direct wiki image links
        f"https://minecraft.wiki/images/{wiki_name}_JE2_BE2.png",
        f"https://minecraft.wiki/images/{wiki_name}_BE.png",
        f"https://minecraft.wiki/images/{wiki_name}_JE.png",
        f"https://minecraft.wiki/images/{wiki_name}.png",
        # Alternative patterns for items
        f"https://minecraft.wiki/images/{wiki_name}_JE3_BE3.png",
        f"https://minecraft.wiki/images/{wiki_name}_JE4_BE2.png",
        # Lowercase variants
        f"https://minecraft.wiki/images/{minecraft_id}.png",
        # Static wikia CDN
        f"{STATIC_BASE}/images/{minecraft_id}.png",
    ]
    
    for url in url_patterns:
        try:
            print(f"  Trying: {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; MinecraftImageScraper/1.0)'
            })
            
            if response.status_code == 200 and len(response.content) > 1000:  # Must be > 1KB
                output_path.write_bytes(response.content)
                print(f"  ✅ Downloaded {minecraft_id}.png from {url}")
                time.sleep(0.5)  # Be nice to the server
                return True
                
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            continue
    
    print(f"  ⚠️  Could not find image for {minecraft_id}")
    return False


def main():
    image_dir = Path(__file__).parent.parent / 'web' / 'mob_images'
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # Get existing images
    existing_images = set(f.stem for f in image_dir.glob('*.png'))
    
    # Get all mobs and items
    mobs = summon_db.get_all_mobs()
    items = summon_db.get_all_items()
    
    # Find missing mob images
    missing_mobs = []
    for mob in mobs:
        minecraft_id = mob.get('minecraft_id', '')
        if minecraft_id and minecraft_id not in existing_images:
            missing_mobs.append(minecraft_id)
    
    # Find missing item images
    missing_items = []
    for item in items:
        minecraft_id = item.get('minecraft_id', '')
        if minecraft_id and minecraft_id not in existing_images:
            missing_items.append(minecraft_id)
    
    print("=" * 60)
    print("Minecraft Image Downloader")
    print("=" * 60)
    print(f"\nFound {len(missing_mobs)} missing mob images")
    print(f"Found {len(missing_items)} missing item images")
    print(f"\nOutput directory: {image_dir}")
    print("=" * 60)
    
    # Download missing mob images
    if missing_mobs:
        print("\n📦 Downloading Mob Images")
        print("-" * 60)
        success_count = 0
        for mob_id in sorted(missing_mobs):
            print(f"\n🔍 {mob_id}:")
            if download_image(mob_id, str(image_dir), is_item=False):
                success_count += 1
        print(f"\n✅ Successfully downloaded {success_count}/{len(missing_mobs)} mob images")
    
    # Download missing item images
    if missing_items:
        print("\n\n📦 Downloading Item Images")
        print("-" * 60)
        success_count = 0
        for item_id in sorted(missing_items):
            print(f"\n🔍 {item_id}:")
            if download_image(item_id, str(image_dir), is_item=True):
                success_count += 1
        print(f"\n✅ Successfully downloaded {success_count}/{len(missing_items)} item images")
    
    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
