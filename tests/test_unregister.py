"""Tests for the /activities/{activity_name}/unregister endpoint"""

import pytest


def test_unregister_successful(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from a non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent%20Activity/unregister",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant_not_found(client):
    """Test unregistering a student not signed up for an activity"""
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": "notstudent@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Student not found" in data["detail"]


def test_unregister_updates_participant_count(client):
    """Test that unregister correctly updates participant count"""
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()["Music Band"]["participants"])
    
    # Unregister a student
    client.delete(
        "/activities/Music%20Band/unregister",
        params={"email": "lucas@mergington.edu"}
    )
    
    # Get updated count
    response = client.get("/activities")
    new_count = len(response.json()["Music Band"]["participants"])
    
    assert new_count == initial_count - 1


def test_unregister_multiple_participants(client):
    """Test unregistering multiple participants from same activity"""
    initial_response = client.get("/activities")
    initial_participants = initial_response.json()["Gym Class"]["participants"].copy()
    
    # Unregister both participants
    for email in initial_participants:
        response = client.delete(
            "/activities/Gym%20Class/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all were removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert len(activities["Gym Class"]["participants"]) == 0


def test_unregister_then_signup_same_participant(client):
    """Test that a student can re-signup after unregistering"""
    email = "daniel@mergington.edu"
    
    # Unregister
    response = client.delete(
        "/activities/Chess%20Club/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Try to signup again
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify re-signup was successful
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities["Chess Club"]["participants"]


def test_unregister_frees_activity_spot(client):
    """Test that unregistering frees up a spot in a full activity"""
    # First, fill up an activity
    response = client.get("/activities")
    data = response.json()
    
    basketball = data["Basketball Team"]
    spots_available = basketball["max_participants"] - len(basketball["participants"])
    
    # Fill up the activity
    new_emails = []
    for i in range(spots_available):
        email = f"filler{i}@mergington.edu"
        new_emails.append(email)
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
    
    # Verify it's full now
    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "cantfit@mergington.edu"}
    )
    assert response.status_code == 400
    
    # Unregister one participant
    client.delete(
        "/activities/Basketball%20Team/unregister",
        params={"email": new_emails[0]}
    )
    
    # Now signup should work
    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "canfitNow@mergington.edu"}
    )
    assert response.status_code == 200
