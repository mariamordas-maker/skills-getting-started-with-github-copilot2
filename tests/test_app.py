"""
Tests for the Mergington High School API

Uses pytest and FastAPI's TestClient to test the API endpoints.
Resets the in-memory activities state before each test.
"""

import pytest
import importlib
from fastapi.testclient import TestClient
import src.app


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset the app's global activities state before each test."""
    importlib.reload(src.app)
    yield
    importlib.reload(src.app)


@pytest.fixture
def client():
    """Provide a TestClient for the app."""
    return TestClient(src.app.app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_dict(self, client):
        """GET /activities should return a dictionary of activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_has_required_fields(self, client):
        """Each activity should have required fields."""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_adds_participant(self, client):
        """POST /activities/{name}/signup should add a participant."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "newstudent@mergington.edu" in response.json()["message"]
    
    def test_signup_fails_if_already_signed_up(self, client):
        """POST /activities/{name}/signup should fail if student already signed up."""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_fails_for_unknown_activity(self, client):
        """POST /activities/{name}/signup should return 404 for unknown activity."""
        response = client.post(
            "/activities/Unknown Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveFromActivity:
    """Tests for POST /activities/{activity_name}/remove endpoint."""
    
    def test_remove_removes_participant(self, client):
        """POST /activities/{name}/remove should remove a participant."""
        response = client.post(
            "/activities/Chess Club/remove",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "michael@mergington.edu" in response.json()["message"]
    
    def test_remove_fails_if_not_signed_up(self, client):
        """POST /activities/{name}/remove should fail if student not signed up."""
        response = client.post(
            "/activities/Chess Club/remove",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "Student not found" in response.json()["detail"]
    
    def test_remove_fails_for_unknown_activity(self, client):
        """POST /activities/{name}/remove should return 404 for unknown activity."""
        response = client.post(
            "/activities/Unknown Activity/remove",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
