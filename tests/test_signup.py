"""Tests for the /activities/{activity_name}/signup endpoint"""

import pytest


def test_signup_successful(client):
    """Test successful signup to an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup to a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client):
    """Test signing up a student already registered for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_full(client):
    """Test signing up to an activity that is full"""
    # First, fill up the activity
    response = client.get("/activities")
    data = response.json()
    
    # Find an activity with only 1 spot left (Basketball Team has 15 max, 1 participant)
    basketball = data["Basketball Team"]
    spots_available = basketball["max_participants"] - len(basketball["participants"])
    
    # Fill up the activity with new signups
    for i in range(spots_available):
        client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": f"student{i}@mergington.edu"}
        )
    
    # Now try to signup when full
    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "fullstudent@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]


def test_signup_multiple_students_same_activity(client):
    """Test multiple different students signing up for the same activity"""
    emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
    
    for email in emails:
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all were added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    for email in emails:
        assert email in activities["Programming Class"]["participants"]


def test_signup_updates_participant_count(client):
    """Test that signup correctly updates participant count"""
    # Get initial count
    response = client.get("/activities")
    initial_count = len(response.json()["Soccer Club"]["participants"])
    
    # Signup new student
    client.post(
        "/activities/Soccer%20Club/signup",
        params={"email": "newsoccer@mergington.edu"}
    )
    
    # Get updated count
    response = client.get("/activities")
    new_count = len(response.json()["Soccer Club"]["participants"])
    
    assert new_count == initial_count + 1
