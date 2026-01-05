# PostgreSQL Database for Summon API

Your Summon API now uses PostgreSQL! 🎉

## Quick Start

```bash
# 1. Install PostgreSQL (if not already installed)
sudo apt install postgresql postgresql-contrib

# 2. Run the quick start script
./quickstart_postgres.sh
```

That's it! Your database is ready.

## What's Included

✅ **Database Layer**: PostgreSQL with connection pooling support  
✅ **Schema Files**: Complete table definitions with indexes and views  
✅ **Sample Data**: Pre-loaded mob, item, and action metadata  
✅ **Web Interface**: Works unchanged at https://10.0.0.227:8080/  
✅ **API Endpoints**: All endpoints work with same signatures  
✅ **Auto Setup**: Scripts to initialize everything automatically

## File Structure

```
schema-postgres.sql          # Main tables (summons, device_locations)
mob/game-objects-schema.sql  # Game objects (mobs, items, actions)
init_postgres.sh            # Database initialization script
quickstart_postgres.sh      # One-command setup
.env.example               # Environment configuration template
POSTGRES_MIGRATION.md      # Complete migration guide
```

## Database Tables

### Core Tables
- **summons** - All summon events with GPS data
- **device_locations** - GPS tracking from NFC devices
- **mobs** - Entity metadata (20+ mobs with stats)
- **items** - Item metadata (30+ items with properties)
- **actions** - Executable actions (time, weather, effects)

### Views
- **recent_summons** - Last 100 summons
- **latest_device_locations** - Latest location per device
- **summons_with_gps** - Only summons with location data

## Environment Configuration

Set these variables (or use `.env` file):

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=summon_db
DB_USER=summon_user
DB_PASSWORD=summon_pass123
```

## Usage

### Start Services
```bash
# API Server
python run_api_sync_v3.py

# Web Server
cd web && python website.py
```

### Access Web Interface
- Home: https://10.0.0.227:8080/
- Mob Details: https://10.0.0.227:8080/mob/piglin
- Player Log: https://10.0.0.227:8080/player/ActorPlayer

### Query Database
```bash
# Connect
psql -h localhost -U summon_user -d summon_db

# View recent summons
SELECT * FROM recent_summons LIMIT 10;

# Count by mob type
SELECT summoned_object_type, COUNT(*) 
FROM summons 
GROUP BY summoned_object_type 
ORDER BY COUNT(*) DESC;
```

## Need Help?

See [POSTGRES_MIGRATION.md](POSTGRES_MIGRATION.md) for:
- Detailed setup instructions
- Troubleshooting guide
- Backup/restore procedures
- Performance tuning tips
- Security best practices

## API Compatibility

✅ **All API endpoints unchanged**  
✅ **Same request/response formats**  
✅ **No client changes needed**  
✅ **Web interface URLs identical**

The migration is transparent to API users!
