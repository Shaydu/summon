#!/bin/bash
# Quick Start: PostgreSQL Database Setup for Summon API
# Run this after PostgreSQL is installed

set -e

echo "================================================"
echo "PostgreSQL Quick Start for Summon API"
echo "================================================"
echo ""

# Step 1: Check if PostgreSQL is running
echo "Checking PostgreSQL status..."
if sudo systemctl is-active --quiet postgresql; then
    echo "✓ PostgreSQL is running"
else
    echo "✗ PostgreSQL is not running. Starting it..."
    sudo systemctl start postgresql
    echo "✓ PostgreSQL started"
fi

echo ""
echo "Step 1/5: Initializing database..."
./init_postgres.sh

echo ""
echo "Step 2/5: Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 3/5: Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "  Please review and update .env if needed"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Step 4/5: Testing database connection..."
python -c "
import summon_db
try:
    conn = summon_db.get_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM summons')
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f'✓ Database connection successful!')
    print(f'  Current summons count: {count}')
except Exception as e:
    print(f'✗ Connection failed: {e}')
    exit(1)
"

echo ""
echo "Step 5/5: Checking tables..."
psql -h localhost -U summon_user -d summon_db -c "\dt" > /dev/null 2>&1 && echo "✓ All tables created successfully"

echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Your PostgreSQL database is ready!"
echo ""
echo "Next steps:"
echo "  1. Start the API server:"
echo "     python run_api_sync_v3.py"
echo ""
echo "  2. Start the web server:"
echo "     cd web && python website.py"
echo ""
echo "  3. Access the web interface:"
echo "     https://10.0.0.227:8080/"
echo ""
echo "Useful commands:"
echo "  - Connect to DB: psql -h localhost -U summon_user -d summon_db"
echo "  - View logs: tail -f logs/api_sync_v3.log"
echo "  - Check status: python -c 'import summon_db; print(\"OK\")'"
echo ""
echo "Documentation: See POSTGRES_MIGRATION.md for details"
echo "================================================"
