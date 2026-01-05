# Device Location Tracking - Implementation Guide

This guide walks through the complete implementation of periodic GPS location tracking for ESP32 devices.

## Overview

**Feature**: ESP32 devices periodically send their GPS position to the backend server for display on an admin panel map.

**Update Frequency**: Every 60 seconds (configurable)

**Battery Impact**: Low - GPS is already running for NFC scanning, only adds WiFi transmission cost

---

## Files Modified/Created

### Documentation
- ✅ **[docs/api/api-v3.5.md](api-v3.5.md)** - API specification with new endpoint
- ✅ **[docs/api/device-location-endpoint.py](device-location-endpoint.py)** - Backend implementation
- ✅ **[docs/api/device-location-schema.sql](device-location-schema.sql)** - Database schema

### Hardware (ESP32)
- ✅ **[arduino-setup/summon_nfc_esp32/summon_nfc_esp32.ino](../../arduino-setup/summon_nfc_esp32/summon_nfc_esp32.ino)**
  - Added global variables (lines 164-166)
  - Added `sendDeviceLocation()` function (lines 999-1076)
  - Added periodic update in `loop()` (lines 373-395)

---

## Implementation Steps

### Step 1: Backend Setup

#### 1.1 Create Database Table

Run the SQL schema in your PostgreSQL database:

```bash
psql -U your_user -d your_database -f docs/api/device-location-schema.sql
```

Or for SQLite (testing):
```bash
sqlite3 your_database.db < docs/api/device-location-schema.sql
```

Verify table was created:
```sql
\d device_locations  -- PostgreSQL
.schema device_locations  -- SQLite
```

#### 1.2 Add Backend Endpoint

Copy the service file to your backend repository:

```bash
# Copy to your backend repo
cp docs/api/device-location-endpoint.py /path/to/backend/summon/services/device_service.py
```

#### 1.3 Register Router in Main API

Edit your `nfc_api.py` (or main FastAPI app file):

```python
from services import device_service

# ... existing code ...

# Add device location tracking routes
app.include_router(device_service.router)
```

#### 1.4 Test Backend Endpoint

Start your backend server, then test with curl:

```bash
curl -X POST http://10.0.0.19:8000/api/device/location \
  -H "Content-Type: application/json" \
  -H "x-api-key: super-secret-test-key22" \
  -d '{
    "device_id": "esp32-test-device",
    "gps_lat": 40.7580,
    "gps_lon": -105.3009,
    "gps_alt": 1655.3,
    "satellites": 8,
    "hdop": 1.2,
    "timestamp": "2025-01-05T12:00:00Z"
  }'
```

Expected response:
```json
{"status":"ok","message":"Device location logged"}
```

Verify in database:
```sql
SELECT * FROM device_locations ORDER BY received_at DESC LIMIT 1;
```

---

### Step 2: ESP32 Firmware Upload

#### 2.1 Review Configuration

In `arduino-setup/summon_nfc_esp32/summon_nfc_esp32.ino`, verify these settings:

```cpp
// Line 44 - Device ID
const char* deviceId = "esp32-nfc-scanner-001";

// Line 38 - Player name
const char* defaultPlayer = "WiryHealer4014";

// Line 1015 - Server URL (update to match your backend)
String url = "http://10.0.0.19:8000/api/device/location";

// Line 166 - Update interval (60 seconds = 1 minute)
const unsigned long LOCATION_UPDATE_INTERVAL = 60000;
```

**Adjust these values for your setup!**

#### 2.2 Upload Firmware

```bash
cd /Users/shaydu/summon-nano-local
./esp32-upload.sh
```

Or upload via Arduino IDE.

#### 2.3 Monitor Serial Output

Connect to serial monitor (115200 baud) and look for:

```
[GPS] Sending periodic location update...
[GPS] Sending device location:
{"device_id":"esp32-nfc-scanner-001","player":"WiryHealer4014","gps_lat":40.758,"gps_lon":-105.301,...}
[GPS] Response code: 200
[GPS] Response: {"status":"ok","message":"Device location logged"}
[GPS] ✓ Location update sent successfully
```

If no GPS fix yet:
```
[GPS] Skipping location update - no GPS fix yet
```

If no WiFi:
```
[GPS] Skipping location update - no WiFi
```

---

### Step 3: Testing & Validation

#### 3.1 Test Indoor (No GPS)

Expected behavior:
- Device skips location updates every 60 seconds
- Serial output: `[GPS] Skipping location update - no GPS fix yet`

#### 3.2 Test Outdoor (GPS Fix)

Expected behavior:
- Within 30-60 seconds, GPS acquires fix (check GPS diagnostic screen)
- Every 60 seconds, device sends location update
- Serial output shows successful POST with 200 response

#### 3.3 Test Offline/Online Transition

1. Start device with WiFi connected and GPS fix
2. Verify location updates are being sent
3. Turn off WiFi router
4. Verify device skips updates (no WiFi message)
5. Turn WiFi back on
6. Verify device resumes sending updates

#### 3.4 Verify Database Storage

Check that locations are being logged:

```sql
-- Latest location for each device
SELECT DISTINCT ON (device_id)
    device_id,
    player,
    lat,
    lon,
    satellites,
    hdop,
    timestamp,
    received_at
FROM device_locations
ORDER BY device_id, timestamp DESC;

-- Location history for specific device
SELECT
    lat,
    lon,
    satellites,
    hdop,
    timestamp
FROM device_locations
WHERE device_id = 'esp32-nfc-scanner-001'
ORDER BY timestamp DESC
LIMIT 10;
```

---

## Configuration Options

### Update Interval Tuning

Edit line 166 in `summon_nfc_esp32.ino`:

```cpp
// More frequent (30 seconds) - higher battery drain
const unsigned long LOCATION_UPDATE_INTERVAL = 30000;

// Standard (60 seconds) - recommended
const unsigned long LOCATION_UPDATE_INTERVAL = 60000;

// Battery saver (5 minutes)
const unsigned long LOCATION_UPDATE_INTERVAL = 300000;
```

### Server URL

Edit line 1015 to point to your backend:

```cpp
String url = "http://YOUR_SERVER_IP:8000/api/device/location";
```

### Quality Filtering

To only send high-quality GPS fixes, modify line 1001:

```cpp
// Current: send if any valid fix
if (!gps.location.isValid()) {

// Better: only send if good quality
if (!gps.location.isValid() ||
    !gps.hdop.isValid() ||
    gps.hdop.hdop() > 3.0 ||
    gps.satellites.value() < 6) {
```

---

## Troubleshooting

### No Location Updates Being Sent

**Check Serial Monitor:**
1. Is GPS getting a fix? Look for: `[GPS] Skipping location update - no GPS fix yet`
   - Solution: Take device outdoors, wait 30-60 seconds for GPS lock
   - Check GPS diagnostic screen (menu → GPS Diagnostic)

2. Is WiFi connected? Look for: `[GPS] Skipping location update - no WiFi`
   - Solution: Verify WiFi credentials in code (lines 34-35)
   - Check if device is in range of WiFi

3. Are updates being attempted? Look for: `[GPS] Sending periodic location update...`
   - If not appearing every 60 seconds, check `LOCATION_UPDATE_INTERVAL` setting

### Backend Returning Errors

**HTTP 401 Unauthorized:**
- Verify API key matches between ESP32 and backend
- ESP32 (line 41): `const char* apiKey = "super-secret-test-key22";`
- Backend: Check `API_KEY` variable

**HTTP 400 Bad Request:**
- Check serial monitor for the JSON payload being sent
- Verify timestamp format is ISO8601 UTC
- Verify GPS coordinates are in valid ranges (-90 to 90, -180 to 180)

**HTTP 500 Internal Server Error:**
- Check backend logs for errors
- Verify database table exists and is accessible
- Check database connection

### GPS Not Getting Fix

**Symptoms:**
- GPS diagnostic shows 0 satellites
- No location data after 5+ minutes outdoors

**Solutions:**
1. Check wiring (GPS RX/TX to ESP32 pins 16/17)
2. Ensure GPS antenna has clear view of sky (not indoors)
3. Cold start can take 30-60 seconds, warm start 1-5 seconds
4. Try power cycling the device

---

## Admin Panel Integration

### Get Latest Device Positions

```sql
SELECT DISTINCT ON (device_id)
    device_id,
    player,
    lat,
    lon,
    timestamp
FROM device_locations
ORDER BY device_id, timestamp DESC;
```

### Get Device Trail (Breadcrumb Path)

```sql
SELECT lat, lon, timestamp
FROM device_locations
WHERE device_id = 'esp32-nfc-scanner-001'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp ASC;  -- Chronological for path drawing
```

### Display on Map (Leaflet.js Example)

```javascript
// Fetch latest positions
const response = await fetch('/api/devices/locations/latest');
const devices = await response.json();

// Add markers to map
devices.forEach(device => {
  L.marker([device.lat, device.lon])
    .addTo(map)
    .bindPopup(`
      <b>${device.device_id}</b><br>
      Player: ${device.player || 'N/A'}<br>
      Last seen: ${new Date(device.timestamp).toLocaleString()}
    `);
});
```

---

## Performance & Battery

### Expected Battery Impact

**GPS Module:**
- Already running continuously for NFC scanning
- **No additional cost**

**WiFi Transmission:**
- ~50-100mA for 1-2 seconds per update
- At 60-second intervals: ~1.5-3.5 mAh per update
- Per day (1440 updates): ~2.2-5.0 Ah

**Total Daily Impact:**
- 60-second interval: ~2.2-5.0 Ah/day
- 5-minute interval: ~0.4-1.0 Ah/day

**Battery Life (with 10,000 mAh battery):**
- 60-second updates: ~2-4 days
- 5-minute updates: ~10-25 days
- *Note: Actual battery life depends on many factors (screen usage, NFC scanning frequency, etc.)*

---

## Next Steps

1. ✅ Test endpoint with curl
2. ✅ Upload firmware to ESP32
3. ✅ Verify location updates in serial monitor
4. ✅ Check database for stored locations
5. ⏳ Build admin panel map view
6. ⏳ Add real-time updates (WebSocket/SSE)
7. ⏳ Implement data retention policy (auto-delete old locations)

---

## Support

- **API Specification:** [docs/api/api-v3.5.md](api-v3.5.md#device-location-tracking-endpoint)
- **Backend Code:** [docs/api/device-location-endpoint.py](device-location-endpoint.py)
- **Database Schema:** [docs/api/device-location-schema.sql](device-location-schema.sql)
- **Firmware:** [arduino-setup/summon_nfc_esp32/summon_nfc_esp32.ino](../../arduino-setup/summon_nfc_esp32/summon_nfc_esp32.ino)
