import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have all 9 activities
        assert len(data) == 9
        
        # Check specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Robotics Club" in data
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        
        # Verify all required fields are present
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
        # Verify content
        assert activity["description"] == "Learn strategies and compete in chess tournaments"
        assert activity["max_participants"] == 12
        assert len(activity["participants"]) == 2


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Basketball"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that student cannot signup twice for same activity"""
        # Attempt to signup student who is already registered
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple different students can signup for activity"""
        # First signup
        response1 = client.post(
            "/activities/Basketball/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup for different student
        response2 = client.post(
            "/activities/Basketball/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are in participants
        participants = activities["Basketball"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity"""
        # First verify student is registered
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from activity that doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister student who is not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_multiple_times_fails(self, client, reset_activities):
        """Test that unregister fails the second time"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response2.status_code == 400


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
