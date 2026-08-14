"""Tests for the /activities endpoint"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities"""
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify we get a dictionary with all activities
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "Basketball Team" in data
    assert "Soccer Club" in data
    assert "Art Studio" in data
    assert "Music Band" in data
    assert "Debate Team" in data
    assert "Science Club" in data


def test_get_activities_has_correct_structure(client):
    """Test that activities have correct data structure"""
    response = client.get("/activities")
    data = response.json()
    
    # Check a specific activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_get_activities_has_participants(client):
    """Test that activities include participant data"""
    response = client.get("/activities")
    data = response.json()
    
    # Verify Chess Club has initial participants
    chess_club = data["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_get_activities_response_consistency(client):
    """Test that multiple requests return consistent data"""
    response1 = client.get("/activities")
    response2 = client.get("/activities")
    
    assert response1.json() == response2.json()
