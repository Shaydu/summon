#!/bin/bash

# Test script for tokens table and PostGIS functionality

DB_NAME="summon_db"
DB_USER="summon_user"
DB_PASSWORD="summon_pass123"

echo "Testing tokens table and PostGIS..."
echo ""

# Test 1: Insert a test token
echo "1. Inserting test token..."
PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" << EOF
INSERT INTO tokens (action_type, entity, gps_write_lat, gps_write_lon, written_by, device_id)
VALUES ('summon_entity', 'piglin', 40.7580, -105.3009, 'TestPlayer', 'test-device-001');
EOF

# Test 2: Query nearby tokens using PostGIS
echo ""
echo "2. Querying tokens within 10km of test location..."
PGPASSWORD="$DB_PASSWORD" psql -h localhost -U "$DB_USER" -d "$DB_NAME" << EOF
SELECT 
  token_id,
  action_type,
  entity,
  written_by,
  gps_write_lat,
  gps_write_lon,
  ROUND(ST_Distance(
    gps_location,
    ST_SetSRID(ST_MakePoint(-105.3009, 40.7580), 4326)::geography
  )::numeric, 1) AS distance_m
FROM tokens
WHERE ST_DWithin(
  gps_location,
  ST_SetSRID(ST_MakePoint(-105.3009, 40.7580), 4326)::geography,
  10000
)
ORDER BY distance_m
LIMIT 5;
EOF

echo ""
echo "✅ Tests completed!"
