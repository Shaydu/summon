#!/usr/bin/env python3
"""
Script to clear summons and device_locations data from PostgreSQL database.
Preserves game objects (mobs, items, actions) tables.
"""
import psycopg2
import os

# PostgreSQL connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'summon_db')
DB_USER = os.getenv('DB_USER', 'summon_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'summon_pass123')

def clear_data():
    """Clear summons and device_locations tables."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        # Get counts before deletion
        cur.execute("SELECT COUNT(*) FROM summons")
        summons_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM device_locations")
        device_locations_count = cur.fetchone()[0]
        
        print(f"Found {summons_count} summons records")
        print(f"Found {device_locations_count} device_locations records")
        
        # Delete data
        cur.execute("DELETE FROM summons")
        cur.execute("DELETE FROM device_locations")
        
        conn.commit()
        
        print(f"\n✅ Cleared {summons_count} summons records")
        print(f"✅ Cleared {device_locations_count} device_locations records")
        print("\n✅ Database cleaned successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Database Cleanup Script")
    print("=" * 60)
    print("\nThis will delete all records from:")
    print("  - summons table (NFC summon/spawn logs)")
    print("  - device_locations table (GPS tracking data)")
    print("\nGame objects (mobs, items, actions) will be preserved.")
    print("=" * 60)
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response in ('yes', 'y'):
        clear_data()
    else:
        print("\n❌ Cancelled - no data was deleted")
