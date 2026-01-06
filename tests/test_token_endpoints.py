"""
Test suite for token endpoints (API v3.6.1).

Tests the /api/tokens/nearby endpoint implementation against the spec
in docs/api/api-v3.6.1-proposed.md
"""

import pytest
import requests
import json
import summon_db
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_KEY = "super-secret-test-key22"
HEADERS = {"x-api-key": API_KEY}


class TestTokensNearbyEndpoint:
    """Test /api/tokens/nearby endpoint."""
    
    def setup_method(self):
        """Setup test data before each test."""
        # Insert test tokens at known locations
        self.test_tokens = []
        
        # Token 1: Piglin at exact search location
        token_id_1 = summon_db.insert_token(
            action_type="summon_entity",
            entity="piglin",
            gps_lat=40.7580,
            gps_lon=-105.3009,
            written_by="TestPlayer1",
            device_id="test-device-001"
        )
        self.test_tokens.append(token_id_1)
        
        # Token 2: Zombie nearby (~100m north)
        token_id_2 = summon_db.insert_token(
            action_type="summon_entity",
            entity="zombie",
            gps_lat=40.7590,
            gps_lon=-105.3009,
            written_by="TestPlayer2",
            device_id="test-device-002"
        )
        self.test_tokens.append(token_id_2)
        
        # Token 3: Diamond sword further away (~1km east)
        token_id_3 = summon_db.insert_token(
            action_type="give_item",
            item="diamond_sword",
            gps_lat=40.7580,
            gps_lon=-105.2880,
            written_by="TestPlayer3",
            device_id="test-device-003"
        )
        self.test_tokens.append(token_id_3)
        
        # Token 4: Far away token (should not appear in 5km searches)
        token_id_4 = summon_db.insert_token(
            action_type="summon_entity",
            entity="creeper",
            gps_lat=40.8500,
            gps_lon=-105.3009,
            written_by="TestPlayer4",
            device_id="test-device-004"
        )
        self.test_tokens.append(token_id_4)
    
    def test_basic_nearby_query(self):
        """Test basic nearby query returns expected structure."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure matches spec
        assert data["status"] == "ok"
        assert "current_position" in data
        assert data["current_position"]["lat"] == 40.7580
        assert data["current_position"]["lon"] == -105.3009
        assert "search_radius_km" in data
        assert "count" in data
        assert "tokens" in data
        assert isinstance(data["tokens"], list)
        
        # Should find at least 3 tokens within default 5km
        assert data["count"] >= 3
    
    def test_token_structure_summon_entity(self):
        """Test that summon_entity tokens have correct fields."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "action_type": "summon_entity",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Find a summon_entity token
        entity_tokens = [t for t in data["tokens"] if t["action_type"] == "summon_entity"]
        assert len(entity_tokens) > 0
        
        token = entity_tokens[0]
        
        # Verify required fields per spec
        assert "token_id" in token
        assert "action_type" in token
        assert token["action_type"] == "summon_entity"
        assert "entity" in token
        assert "name" in token
        assert "mob_type" in token or token.get("mob_type") is None
        assert "rarity" in token or token.get("rarity") is None
        assert "position" in token
        assert "lat" in token["position"]
        assert "lon" in token["position"]
        assert "distance_m" in token
        assert "bearing" in token
        assert "written_by" in token
        assert "written_at" in token
        
        # Verify bearing is 0-360
        assert 0 <= token["bearing"] < 360
        
        # Verify distance is non-negative
        assert token["distance_m"] >= 0
    
    def test_token_structure_give_item(self):
        """Test that give_item tokens have correct fields."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "action_type": "give_item",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Find a give_item token
        item_tokens = [t for t in data["tokens"] if t["action_type"] == "give_item"]
        assert len(item_tokens) > 0
        
        token = item_tokens[0]
        
        # Verify required fields per spec
        assert token["action_type"] == "give_item"
        assert "item" in token
        assert "name" in token
        assert "rarity" in token or token.get("rarity") is None
        assert "distance_m" in token
        assert "bearing" in token
    
    def test_distance_sorting(self):
        """Test that results are sorted by distance ascending."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify tokens are sorted by distance
        distances = [t["distance_m"] for t in data["tokens"]]
        assert distances == sorted(distances)
        
        # First token should be closest (at exact location)
        assert data["tokens"][0]["distance_m"] < 10  # Within 10 meters
    
    def test_radius_filter(self):
        """Test that radius_km parameter filters correctly."""
        # Query with very small radius (should only find closest token)
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "radius_km": 0.1,  # 100 meters
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only find tokens within 100m
        for token in data["tokens"]:
            assert token["distance_m"] <= 100
    
    def test_limit_parameter(self):
        """Test that limit parameter restricts results."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return at most 2 tokens
        assert len(data["tokens"]) <= 2
    
    def test_action_type_filter(self):
        """Test filtering by action_type."""
        # Filter for summon_entity only
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "action_type": "summon_entity",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned tokens should be summon_entity
        for token in data["tokens"]:
            assert token["action_type"] == "summon_entity"
        
        # Filter for give_item only
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "action_type": "give_item",
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned tokens should be give_item
        for token in data["tokens"]:
            assert token["action_type"] == "give_item"
    
    def test_invalid_coordinates(self):
        """Test validation of GPS coordinates."""
        # Invalid latitude (> 90)
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 100.0,
                "lon": -105.3009
            }
        )
        assert response.status_code == 422  # Validation error
        
        # Invalid longitude (< -180)
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -200.0
            }
        )
        assert response.status_code == 422
    
    def test_invalid_radius(self):
        """Test validation of radius_km parameter."""
        # Radius too small
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "radius_km": 0.05  # Below 0.1 minimum
            }
        )
        assert response.status_code == 422
        
        # Radius too large
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "radius_km": 100.0  # Above 50 maximum
            }
        )
        assert response.status_code == 422
    
    def test_invalid_limit(self):
        """Test validation of limit parameter."""
        # Limit too small
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 0
            }
        )
        assert response.status_code == 422
        
        # Limit too large
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 100
            }
        )
        assert response.status_code == 422
    
    def test_missing_api_key(self):
        """Test that API key is required."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            params={
                "lat": 40.7580,
                "lon": -105.3009
            }
        )
        assert response.status_code == 422  # Missing required header
    
    def test_invalid_api_key(self):
        """Test that invalid API key is rejected."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers={"x-api-key": "invalid-key"},
            params={
                "lat": 40.7580,
                "lon": -105.3009
            }
        )
        assert response.status_code == 401
    
    def test_bearing_calculation(self):
        """Test that bearing is calculated correctly."""
        response = requests.get(
            f"{BASE_URL}/api/tokens/nearby",
            headers=HEADERS,
            params={
                "lat": 40.7580,
                "lon": -105.3009,
                "limit": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the zombie token (should be roughly north)
        zombie_tokens = [t for t in data["tokens"] if t.get("entity") == "zombie"]
        if zombie_tokens:
            zombie = zombie_tokens[0]
            # Zombie is north, so bearing should be close to 0° or 360°
            # Allow some tolerance
            assert zombie["bearing"] < 10 or zombie["bearing"] > 350
        
        # Find the diamond_sword token (should be roughly east)
        sword_tokens = [t for t in data["tokens"] if t.get("item") == "diamond_sword"]
        if sword_tokens:
            sword = sword_tokens[0]
            # Sword is east, so bearing should be close to 90°
            assert 80 <= sword["bearing"] <= 100


class TestTokensListEndpoint:
    """Test /api/tokens endpoint (get all tokens)."""
    
    def test_get_all_tokens(self):
        """Test that we can list all tokens."""
        response = requests.get(
            f"{BASE_URL}/api/tokens",
            headers=HEADERS,
            params={"limit": 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "ok"
        assert "count" in data
        assert "tokens" in data
        assert isinstance(data["tokens"], list)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
