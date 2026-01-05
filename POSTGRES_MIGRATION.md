# PostgreSQL Database Migration Guide

## Overview

Your Summon API has been successfully migrated to use PostgreSQL as the database backend. The API signatures remain unchanged - all endpoints work exactly as before.

## What Changed

### Database Layer
- **Old**: SQLite (`summon.db` file)
- **New**: PostgreSQL (client-server database)
- **Backup**: SQLite version preserved in `summon_db_sqlite_backup.py`

### Files Updated
1. **summon_db.py** - Now uses PostgreSQL via psycopg2
2. **requirements.txt** - Added `psycopg2-binary>=2.9.9`
3. **schema-postgres.sql** - Main tables (summons, device_locations)
4. **mob/game-objects-schema.sql** - Game objects (mobs, items, actions)
5. **init_postgres.sh** - Automated database initialization script

### API Endpoints (Unchanged)
All API endpoints continue to work with the same signatures:
- POST `/summon` - Immediate summon
- POST `/api/summon/sync` - Single sync
- POST `/api/summon/sync/batch` - Batch sync
- GET `/summons` - List all summons
- GET `/summons/mob/<mob_name>` - Filter by mob
- POST `/api/device/location` - Record device location
- GET `/api/device/locations` - Get all locations

### Web Interface (Unchanged URLs)
- `https://10.0.0.227:8080/` - Home page (all mobs with counts)
- `https://10.0.0.227:8080/mob/<mob_id>` - Detailed mob page with summon history
- `https://10.0.0.227:8080/player/<player_name>` - Player discovery log
- `https://10.0.0.227:8080/log` - Global log view

## Setup Instructions

### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

### 2. Initialize the Database

Run the automated initialization script:
```bash
cd /home/doo/minecraft-bedrock-server/summon
./init_postgres.sh
```

This script will:
- Create the database `summon_db`
- Create the user `summon_user` with password
- Create all tables (summons, device_locations, mobs, items, actions)
- Set up indexes and views
- Grant necessary permissions
- Load sample mob/item data

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=summon_db
DB_USER=summon_user
DB_PASSWORD=summon_pass123
```

Or export them directly:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=summon_db
export DB_USER=summon_user
export DB_PASSWORD=summon_pass123
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install `psycopg2-binary` and other required packages.

### 5. Test the Connection

```bash
python -c "import summon_db; print('Connection successful!')"
```

Or test with psql:
```bash
psql -h localhost -U summon_user -d summon_db -c "SELECT COUNT(*) FROM summons;"
```

### 6. Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

```bash
python migrate_sqlite_to_postgres.py
```

(Migration script to be created if needed)

### 7. Start Services

**API Server:**
```bash
python run_api_sync_v3.py
```

**Web Server:**
```bash
cd web
python website.py
```

Access the web interface at: `https://10.0.0.227:8080/`

## Database Schema

### Main Tables

#### summons
Stores all summon requests:
- `id` (SERIAL PRIMARY KEY)
- `server_ip`, `server_port`
- `summoned_object_type` (entity/item type)
- `summoning_player` (who initiated)
- `summoned_player` (target player)
- `timestamp_utc` (when requested)
- `gps_lat`, `gps_lon` (optional GPS coordinates)

#### device_locations
Stores GPS location data from devices:
- `id` (SERIAL PRIMARY KEY)
- `device_id` (device identifier)
- `player` (associated player name)
- `gps_lat`, `gps_lon` (coordinates)
- `gps_alt`, `gps_speed` (optional)
- `satellites`, `hdop` (GPS quality metrics)
- `timestamp` (when recorded)

#### mobs
Game object metadata for entities:
- `mob_id`, `name`, `description`
- `mob_type` (hostile, passive, neutral, boss)
- `minecraft_id` (actual entity ID)
- `health`, `damage`, `armor`
- `rarity`, `biome`, `difficulty_rating`

#### items
Game object metadata for items:
- `item_id`, `name`, `description`
- `item_category` (weapon, tool, food, block, resource)
- `minecraft_id` (actual item ID)
- `max_stack_size`, `durability`, `damage`
- `rarity`, `value`, `enchantable`

#### actions
Metadata for executable actions:
- `action_id`, `action_type`, `name`
- `default_params` (JSONB)
- `requires_op`, `cooldown_seconds`
- `category`, `rarity`

## Useful PostgreSQL Commands

### Connect to database:
```bash
psql -h localhost -U summon_user -d summon_db
```

### Common queries:
```sql
-- View all tables
\dt

-- View table structure
\d summons

-- Count total summons
SELECT COUNT(*) FROM summons;

-- Recent summons
SELECT * FROM recent_summons LIMIT 10;

-- Summons by mob type
SELECT summoned_object_type, COUNT(*) as count 
FROM summons 
GROUP BY summoned_object_type 
ORDER BY count DESC;

-- Latest device locations
SELECT * FROM latest_device_locations;

-- All mobs
SELECT mob_id, name, mob_type, difficulty_rating FROM mobs ORDER BY name;
```

### Database maintenance:
```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Check database size
SELECT pg_size_pretty(pg_database_size('summon_db'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Backup and Restore

### Backup database:
```bash
pg_dump -h localhost -U summon_user summon_db > backup_$(date +%Y%m%d).sql
```

### Restore database:
```bash
psql -h localhost -U summon_user summon_db < backup_20260105.sql
```

### Automated daily backups:
Create a cron job:
```bash
crontab -e
```

Add:
```
0 2 * * * pg_dump -h localhost -U summon_user summon_db > /backups/summon_db_$(date +\%Y\%m\%d).sql
```

## Troubleshooting

### Connection refused
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify port 5432 is open: `netstat -tlnp | grep 5432`
- Check pg_hba.conf for authentication settings

### Permission denied
- Verify user permissions: `\du` in psql
- Re-run init_postgres.sh to fix permissions

### Module not found: psycopg2
```bash
pip install psycopg2-binary
```

### Cannot connect to database
- Check environment variables are set
- Verify .env file exists and is loaded
- Test with: `echo $DB_NAME`

### Web server shows no data
- Verify database has data: `psql -U summon_user summon_db -c "SELECT COUNT(*) FROM summons;"`
- Check API server is running and using correct database
- Review logs: `tail -f logs/api_sync_v3.log`

## Performance Tuning

For production use, consider:

1. **Connection pooling** - Use pgbouncer or SQLAlchemy connection pool
2. **Indexes** - Already created on frequently queried columns
3. **Query optimization** - Use EXPLAIN ANALYZE for slow queries
4. **Partitioning** - For large summons table, partition by date
5. **Monitoring** - Use pg_stat_statements for query analysis

## Security Notes

1. **Change default password** in production
2. **Use SSL connections** for remote access
3. **Restrict pg_hba.conf** to specific IPs
4. **Regular backups** - Critical data protection
5. **Monitor logs** - Check for unauthorized access attempts

## Support

For issues or questions:
- Check logs: `logs/api_sync_v3.log`
- Database logs: `/var/log/postgresql/`
- Review schema: `schema-postgres.sql` and `mob/game-objects-schema.sql`
