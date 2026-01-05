#!/bin/bash
# PostgreSQL Database Initialization Script for Summon API
# This script creates the database, user, and tables

set -e

# Configuration (override with environment variables)
DB_NAME="${DB_NAME:-summon_db}"
DB_USER="${DB_USER:-summon_user}"
DB_PASSWORD="${DB_PASSWORD:-summon_pass123}"
POSTGRES_ADMIN="${POSTGRES_ADMIN:-postgres}"

echo "================================================"
echo "PostgreSQL Database Initialization"
echo "================================================"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "================================================"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    exit 1
fi

# Function to run SQL as postgres admin user
run_as_admin() {
    sudo -u $POSTGRES_ADMIN psql -c "$1"
}

echo ""
echo "Step 1: Creating database and user..."
echo "---------------------------------------"

# Create user if not exists
run_as_admin "DO \$\$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END \$\$;"

echo "✓ User created/verified: $DB_USER"

# Create database if not exists
run_as_admin "SELECT 'CREATE DATABASE $DB_NAME' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec"

echo "✓ Database created/verified: $DB_NAME"

# Grant privileges
run_as_admin "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
echo "✓ Privileges granted"

echo ""
echo "Step 2: Creating main application tables..."
echo "---------------------------------------"

# Apply main schema
sudo -u $POSTGRES_ADMIN psql -d $DB_NAME -f schema-postgres.sql

echo "✓ Main tables created (summons, device_locations)"

echo ""
echo "Step 3: Creating game objects tables..."
echo "---------------------------------------"

# Apply game objects schema
sudo -u $POSTGRES_ADMIN psql -d $DB_NAME -f mob/game-objects-schema.sql

echo "✓ Game objects tables created (mobs, items, actions)"

echo ""
echo "Step 4: Setting ownership and permissions..."
echo "---------------------------------------"

# Grant all privileges on all tables
sudo -u $POSTGRES_ADMIN psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
sudo -u $POSTGRES_ADMIN psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
sudo -u $POSTGRES_ADMIN psql -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;"

echo "✓ Permissions granted"

echo ""
echo "================================================"
echo "Database initialization complete!"
echo "================================================"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Test connection with:"
echo "  psql -h localhost -U $DB_USER -d $DB_NAME"
echo ""
echo "Set environment variables for the application:"
echo "  export DB_HOST=localhost"
echo "  export DB_PORT=5432"
echo "  export DB_NAME=$DB_NAME"
echo "  export DB_USER=$DB_USER"
echo "  export DB_PASSWORD=$DB_PASSWORD"
echo ""
echo "Or add to .env file for automatic loading"
echo "================================================"
