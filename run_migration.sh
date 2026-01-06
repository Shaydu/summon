#!/bin/bash

# Migration runner for PostGIS and tokens table
# Usage: ./run_migration.sh [migration_file]

set -e  # Exit on error

# Database connection settings (from existing setup)
DB_NAME="summon_db"
DB_USER="summon_user"
DB_PASSWORD="summon_pass123"
DB_HOST="localhost"
DB_PORT="5432"

# Default migration file
MIGRATION_FILE="${1:-migrations/001_add_postgis_and_tokens.sql}"

echo "=================================="
echo "Running Migration"
echo "=================================="
echo "Database: $DB_NAME"
echo "Migration: $MIGRATION_FILE"
echo ""

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

# Run migration
echo "Executing migration..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATION_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    
    # Verify PostGIS installation
    echo "Verifying PostGIS installation..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT PostGIS_Version();"
    
    echo ""
    echo "Verifying tokens table..."
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\d tokens"
    
else
    echo ""
    echo "❌ Migration failed!"
    exit 1
fi
