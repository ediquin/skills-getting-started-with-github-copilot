"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include required fields"""
        response = client.get("/activities")
        data = response.json()
        
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant lists"""
        response = client.get("/activities")
        data = response.json()
        
        chess = data["Chess Club"]
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successful signup for a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_list(self, client, reset_activities):
        """Test that signup actually adds participant to activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signup to nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that duplicate signup is prevented"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_preserves_existing_participants(self, client, reset_activities):
        """Test that adding new participant doesn't remove existing ones"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        
        # Original participants should still be there
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]
        # New participant should be added
        assert "newstudent@mergington.edu" in chess["participants"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can signup for multiple activities"""
        new_student = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={new_student}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={new_student}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        response = client.get("/activities")
        data = response.json()
        assert new_student in data["Chess Club"]["participants"]
        assert new_student in data["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client, reset_activities):
        """Test successful unregistration of existing participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes participant"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_preserves_other_participants(self, client, reset_activities):
        """Test that unregistering one participant doesn't affect others"""
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        # Other participant should still be there
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregister from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_all_participants(self, client, reset_activities):
        """Test unregistering all participants from an activity"""
        # Unregister both initial participants
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        client.delete(
            "/activities/Chess Club/unregister?email=daniel@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 0


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")


class TestActivityCapacity:
    """Tests for activity capacity constraints"""
    
    def test_signup_respects_max_participants(self, client, reset_activities):
        """Test that capacity limits are reported in activity data"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
    
    def test_participant_count_accuracy(self, client, reset_activities):
        """Test that participant count matches actual participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess = data["Chess Club"]
        assert len(chess["participants"]) == 2
        
        prog = data["Programming Class"]
        assert len(prog["participants"]) == 2
        
        gym = data["Gym Class"]
        assert len(gym["participants"]) == 2
