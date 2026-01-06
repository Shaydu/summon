#!/usr/bin/env python3
"""
Test NFC Token v1.1.1 format support.

Tests:
- Parse v1.1.1 "give_<item>" format
- Parse v1.1.1 "<entity>" format
- Token write with GPS coordinates
- Command execution
"""

import pytest
import sys
sys.path.insert(0, "/home/doo/minecraft-bedrock-server/summon")

from services.nfc_service import parse_token_v1_1_1, handle_nfc_event
import summon_db


def test_parse_give_token():
    """Test parsing v1.1.1 give_item tokens."""
    data = {"action": "give_diamond_sword"}
    action_type, entity, item = parse_token_v1_1_1(data)
    
    assert action_type == "give_item"
    assert entity is None
    assert item == "diamond_sword"


def test_parse_summon_token():
    """Test parsing v1.1.1 summon_entity tokens."""
    data = {"action": "piglin"}
    action_type, entity, item = parse_token_v1_1_1(data)
    
    assert action_type == "summon_entity"
    assert entity == "piglin"
    assert item is None


def test_handle_nfc_event_summon():
    """Test handling v1.1.1 summon token with GPS."""
    data = {
        "action": "zombie",
        "player": "TestPlayer",
        "device_id": "test-device-001",
        "gps_lat": 40.0150,
        "gps_lon": -105.2705,
        "timestamp": "2026-01-05T12:00:00Z"
    }
    
    response = handle_nfc_event(data)
    
    assert response["status"] == "ok"
    assert response["action_type"] == "summon_entity"
    assert response["entity"] == "zombie"
    assert "token_id" in response
    assert response["gps"]["lat"] == 40.0150
    assert response["gps"]["lon"] == -105.2705


def test_handle_nfc_event_give():
    """Test handling v1.1.1 give token with GPS."""
    data = {
        "action": "give_emerald",
        "player": "TestPlayer",
        "device_id": "test-device-002",
        "gps_lat": 40.0150,
        "gps_lon": -105.2705,
        "timestamp": "2026-01-05T12:00:00Z"
    }
    
    response = handle_nfc_event(data)
    
    assert response["status"] == "ok"
    assert response["action_type"] == "give_item"
    assert response["item"] == "emerald"
    assert "token_id" in response
    assert response["gps"]["lat"] == 40.0150
    assert response["gps"]["lon"] == -105.2705


def test_handle_nfc_event_no_gps():
    """Test handling v1.1.1 token without GPS (legacy mode)."""
    data = {
        "action": "creeper",
        "player": "TestPlayer",
        "timestamp": "2026-01-05T12:00:00Z"
    }
    
    response = handle_nfc_event(data)
    
    assert response["status"] == "ok"
    assert response["action_type"] == "summon_entity"
    assert response["entity"] == "creeper"
    # No token_id or gps in response when GPS not provided
    assert "token_id" not in response
    assert "gps" not in response


def test_missing_action():
    """Test error handling for missing action field."""
    data = {"player": "TestPlayer"}
    response = handle_nfc_event(data)
    
    assert response["status"] == "error"
    assert "action" in response["error"].lower()


def test_missing_player():
    """Test error handling for missing player field."""
    data = {"action": "zombie"}
    response = handle_nfc_event(data)
    
    assert response["status"] == "error"
    assert "player" in response["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
