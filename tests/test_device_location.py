import pytest
from fastapi.testclient import TestClient
from nfc_api import app

client = TestClient(app)
API_KEY = "super-secret-test-key22"


def test_device_location_success_all_fields():
    """Test device location with all fields including optional ones."""
    payload = {
        "device_id": "esp32-nfc-scanner-001",
        "player": "WiryHealer4014",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "gps_alt": 1655.3,
        "gps_speed": 0.0,
        "satellites": 8,
        "hdop": 1.2,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Device location logged"


def test_device_location_success_required_fields_only():
    """Test device location with only required fields."""
    payload = {
        "device_id": "esp32-test-device",
        "gps_lat": 37.7749,
        "gps_lon": -122.4194,
        "timestamp": "2025-12-25T23:00:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Device location logged"


def test_device_location_missing_device_id():
    """Test device location with missing device_id."""
    payload = {
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "device_id" in data["error"]


def test_device_location_empty_device_id():
    """Test device location with empty device_id."""
    payload = {
        "device_id": "",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "device_id" in data["error"]


def test_device_location_device_id_too_long():
    """Test device location with device_id exceeding 64 characters."""
    payload = {
        "device_id": "a" * 65,  # 65 characters
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "64 characters" in data["error"]


def test_device_location_missing_gps_lat():
    """Test device location with missing gps_lat."""
    payload = {
        "device_id": "esp32-test",
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lat" in data["error"]


def test_device_location_missing_gps_lon():
    """Test device location with missing gps_lon."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lon" in data["error"]


def test_device_location_invalid_gps_lat_too_low():
    """Test device location with gps_lat below -90."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": -91.0,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lat" in data["error"]
    assert "-90" in data["error"] and "90" in data["error"]


def test_device_location_invalid_gps_lat_too_high():
    """Test device location with gps_lat above 90."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 91.0,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lat" in data["error"]
    assert "-90" in data["error"] and "90" in data["error"]


def test_device_location_invalid_gps_lon_too_low():
    """Test device location with gps_lon below -180."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -181.0,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lon" in data["error"]
    assert "-180" in data["error"] and "180" in data["error"]


def test_device_location_invalid_gps_lon_too_high():
    """Test device location with gps_lon above 180."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": 181.0,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lon" in data["error"]
    assert "-180" in data["error"] and "180" in data["error"]


def test_device_location_invalid_gps_lat_not_number():
    """Test device location with non-numeric gps_lat."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": "not a number",
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lat" in data["error"]
    assert "number" in data["error"]


def test_device_location_invalid_gps_lon_not_number():
    """Test device location with non-numeric gps_lon."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": "not a number",
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "gps_lon" in data["error"]
    assert "number" in data["error"]


def test_device_location_missing_timestamp():
    """Test device location with missing timestamp."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "timestamp" in data["error"]


def test_device_location_empty_timestamp():
    """Test device location with empty timestamp."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": ""
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "timestamp" in data["error"]


def test_device_location_player_too_long():
    """Test device location with player exceeding 64 characters."""
    payload = {
        "device_id": "esp32-test",
        "player": "a" * 65,  # 65 characters
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "player" in data["error"]
    assert "64 characters" in data["error"]


def test_device_location_invalid_satellites():
    """Test device location with non-integer satellites."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "satellites": "eight",
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "satellites" in data["error"]
    assert "integer" in data["error"]


def test_device_location_invalid_hdop():
    """Test device location with non-numeric hdop."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "hdop": "invalid",
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "hdop" in data["error"]
    assert "number" in data["error"]


def test_device_location_invalid_api_key():
    """Test device location with invalid API key."""
    payload = {
        "device_id": "esp32-test",
        "gps_lat": 40.7580,
        "gps_lon": -105.3009,
        "timestamp": "2025-12-25T22:30:00Z"
    }
    response = client.post("/api/device/location", json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401


def test_device_location_not_json_object():
    """Test device location with non-dict body."""
    response = client.post("/api/device/location", json="not an object", headers={"x-api-key": API_KEY})
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "JSON object" in data["error"]


def test_device_location_boundary_values():
    """Test device location with boundary GPS values."""
    payloads = [
        {"device_id": "test", "gps_lat": -90.0, "gps_lon": -180.0, "timestamp": "2025-12-25T22:30:00Z"},
        {"device_id": "test", "gps_lat": 90.0, "gps_lon": 180.0, "timestamp": "2025-12-25T22:30:00Z"},
        {"device_id": "test", "gps_lat": 0.0, "gps_lon": 0.0, "timestamp": "2025-12-25T22:30:00Z"},
    ]
    for payload in payloads:
        response = client.post("/api/device/location", json=payload, headers={"x-api-key": API_KEY})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
