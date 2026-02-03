#!/usr/bin/env python3
"""
Add Mob Script for Summon

Adds a new Minecraft mob to the Summon database with metadata and image.

Usage:
    python3 add_mob.py --minecraft-id warden --name "Warden" --image-path ./warden.png

Required Arguments:
    --minecraft-id: Minecraft entity ID (lowercase, underscores for spaces)
    --name: Display name for the mob

Optional Arguments:
    --description: Detailed description of the mob
    --mob-type: Type of mob (hostile, passive, neutral). Default: passive
    --health: HP value. Default: 20
    --damage: Damage per hit. Default: 0
    --armor: Armor rating. Default: 0
    --rarity: Rarity level (common, uncommon, rare, legendary). Default: common
    --biome: Associated biome. Default: any
    --difficulty: Difficulty rating 1-5. Default: 0
    --image-path: Path to PNG image file to copy to mob_images
"""

import sys
import os
import argparse
import shutil
from pathlib import Path

# Add parent directory to path to import summon_db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import summon_db
except ImportError as e:
    print(f"Error: Could not import summon_db. Make sure PostgreSQL is configured.")
    print(f"Details: {e}")
    sys.exit(1)


def copy_image_to_mob_images(image_path, minecraft_id):
    """Copy image to web/mob_images directory with minecraft_id as filename."""
    try:
        image_path = Path(image_path)
        
        # Verify source exists
        if not image_path.exists():
            print(f"Error: Image file not found: {image_path}")
            return False
        
        # Get file extension
        file_ext = image_path.suffix.lower()
        if file_ext not in ['.png', '.jpg', '.jpeg', '.gif']:
            print(f"Warning: Unsupported image format {file_ext}. Expected .png, .jpg, or .gif")
            return False
        
        # Determine destination
        script_dir = Path(__file__).parent.parent
        mob_images_dir = script_dir / 'web' / 'mob_images'
        
        # Create directory if it doesn't exist
        mob_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        dest_path = mob_images_dir / f"{minecraft_id}.png"
        shutil.copy2(image_path, dest_path)
        
        print(f"✓ Image copied to: {dest_path}")
        return True
        
    except Exception as e:
        print(f"Error copying image: {e}")
        return False


def validate_args(args):
    """Validate command-line arguments."""
    errors = []
    
    if not args.minecraft_id:
        errors.append("--minecraft-id is required")
    
    if not args.name:
        errors.append("--name is required")
    
    if args.mob_type and args.mob_type not in ['hostile', 'passive', 'neutral']:
        errors.append(f"--mob-type must be one of: hostile, passive, neutral (got {args.mob_type})")
    
    if args.rarity and args.rarity not in ['common', 'uncommon', 'rare', 'legendary']:
        errors.append(f"--rarity must be one of: common, uncommon, rare, legendary (got {args.rarity})")
    
    if args.difficulty and (args.difficulty < 0 or args.difficulty > 5):
        errors.append(f"--difficulty must be between 0-5 (got {args.difficulty})")
    
    if args.image_path:
        image_path = Path(args.image_path)
        if not image_path.exists():
            errors.append(f"Image file not found: {args.image_path}")
    
    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Add a new Minecraft mob to the Summon database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic mob
  python3 add_mob.py --minecraft-id sheep --name "Sheep"
  
  # Full details with image
  python3 add_mob.py \\
    --minecraft-id warden \\
    --name "Warden" \\
    --description "A powerful hostile mob from the Deep Dark" \\
    --mob-type hostile \\
    --health 500 \\
    --damage 32 \\
    --rarity legendary \\
    --difficulty 5 \\
    --image-path ./warden.png
        '''
    )
    
    # Required arguments
    parser.add_argument('--minecraft-id', required=True,
                        help='Minecraft entity ID (lowercase, underscores for spaces)')
    parser.add_argument('--name', required=True,
                        help='Display name for the mob')
    
    # Optional arguments
    parser.add_argument('--description', default=None,
                        help='Description of the mob')
    parser.add_argument('--mob-type', default='passive',
                        help='Type of mob: hostile, passive, neutral (default: passive)')
    parser.add_argument('--health', type=int, default=20,
                        help='HP value (default: 20)')
    parser.add_argument('--damage', type=int, default=0,
                        help='Damage per hit (default: 0)')
    parser.add_argument('--armor', type=int, default=0,
                        help='Armor rating (default: 0)')
    parser.add_argument('--rarity', default='common',
                        help='Rarity: common, uncommon, rare, legendary (default: common)')
    parser.add_argument('--biome', default='any',
                        help='Associated biome (default: any)')
    parser.add_argument('--difficulty', type=int, default=0,
                        help='Difficulty rating 0-5 (default: 0)')
    parser.add_argument('--image-path', default=None,
                        help='Path to PNG image file to copy to mob_images')
    
    args = parser.parse_args()
    
    # Validate arguments
    errors = validate_args(args)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  ✗ {error}")
        sys.exit(1)
    
    # Display what we're about to add
    print("\n📋 Adding mob with the following details:")
    print(f"  Minecraft ID: {args.minecraft_id}")
    print(f"  Name: {args.name}")
    print(f"  Type: {args.mob_type}")
    print(f"  Health: {args.health}")
    print(f"  Damage: {args.damage}")
    print(f"  Rarity: {args.rarity}")
    print(f"  Difficulty: {args.difficulty}/5")
    if args.description:
        print(f"  Description: {args.description}")
    if args.image_path:
        print(f"  Image: {args.image_path}")
    print()
    
    # Copy image if provided
    if args.image_path:
        print("🖼️  Copying image...")
        if not copy_image_to_mob_images(args.image_path, args.minecraft_id):
            print("Failed to copy image. Continuing without image...")
    
    # Insert into database
    print("💾 Adding mob to database...")
    try:
        summon_db.insert_mob(
            minecraft_id=args.minecraft_id,
            name=args.name,
            description=args.description,
            mob_type=args.mob_type,
            health=args.health,
            damage=args.damage,
            armor=args.armor,
            rarity=args.rarity,
            biome=args.biome,
            difficulty_rating=args.difficulty
        )
        print(f"✓ Mob '{args.name}' ({args.minecraft_id}) added successfully!")
        print(f"\n🌐 View on dashboard: https://10.0.0.227:8080/mob/{args.minecraft_id}")
        
    except Exception as e:
        print(f"✗ Error adding mob to database: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
