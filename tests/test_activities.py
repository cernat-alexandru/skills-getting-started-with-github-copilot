"""
Unit and integration tests for GET /activities endpoint.

Tests cover:
- Retrieving all activities
- Response structure and format
- Participant data accuracy
- Data consistency after signup/cancel operations
"""

import pytest


class TestGetActivitiesSuccessful:
    """Test successful retrieval of activities using AAA pattern."""

    def test_get_activities_returns_200(self, client):
        """
        Arrange: Client ready to make request
        Act: GET request to /activities
        Assert: Returns 200 status code
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Application with multiple activities
        Act: GET request to /activities
        Assert: Response contains all activity names
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Debate Club",
            "Science Olympiad",
            "Art Studio",
            "Music Ensemble"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name in expected_activities:
            assert activity_name in data

    def test_get_activities_returns_json(self, client):
        """
        Arrange: Client making request
        Act: GET request to /activities
        Assert: Response is valid JSON dict
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert isinstance(response.json(), dict)


class TestActivitiesStructure:
    """Test the structure of activity data using AAA pattern."""

    def test_activity_contains_required_fields(self, client):
        """
        Arrange: Request for activities
        Act: GET /activities
        Assert: Each activity contains required fields
        """
        # Arrange
        required_fields = [
            "description",
            "schedule",
            "max_participants",
            "participants"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing {field} in {activity_name}"

    def test_participants_is_list(self, client):
        """
        Arrange: Request for activities
        Act: GET /activities
        Assert: Participants field is a list for each activity
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} is not a list"

    def test_max_participants_is_integer(self, client):
        """
        Arrange: Request for activities
        Act: GET /activities
        Assert: max_participants is an integer
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"max_participants for {activity_name} is not an integer"

    def test_description_and_schedule_are_strings(self, client):
        """
        Arrange: Request for activities
        Act: GET /activities
        Assert: description and schedule are strings
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)


class TestActivitiesAfterSignup:
    """Test activities data consistency after signup using AAA pattern."""

    def test_participants_updated_after_signup(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant signs up for activity
        Act: GET /activities after signup
        Assert: Participant appears in the activity's participants list
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        assert email in participants

    def test_multiple_participants_in_activity(self, client, reset_activities, sample_activity):
        """
        Arrange: Multiple participants sign up
        Act: GET /activities
        Assert: All participants appear in the same activity
        """
        # Arrange
        activity = sample_activity
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        for email in emails:
            client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        for email in emails:
            assert email in participants

    def test_participant_count_increases(self, client, reset_activities, sample_activity):
        """
        Arrange: No participants initially
        Act: Add two participants, get activities between each
        Assert: Participant count increases correctly
        """
        # Arrange
        activity = sample_activity
        email1 = "first@mergington.edu"
        email2 = "second@mergington.edu"
        
        # Act & Assert
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        client.post(f"/activities/{activity}/signup", params={"email": email1})
        response_after_one = client.get("/activities")
        count_after_one = len(response_after_one.json()[activity]["participants"])
        
        client.post(f"/activities/{activity}/signup", params={"email": email2})
        response_after_two = client.get("/activities")
        count_after_two = len(response_after_two.json()[activity]["participants"])
        
        assert count_after_one == count_before + 1
        assert count_after_two == count_after_one + 1


class TestActivitiesAfterCancel:
    """Test activities data consistency after cancellation using AAA pattern."""

    def test_participant_removed_after_cancel(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant signs up then cancels
        Act: GET /activities after cancel
        Assert: Participant is no longer in the list
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        client.delete(f"/activities/{activity}/cancel", params={"email": email})
        
        # Act
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        assert email not in participants

    def test_other_participants_remain_after_cancel(self, client, reset_activities, sample_activity):
        """
        Arrange: Multiple participants, one cancels
        Act: GET /activities after one cancels
        Assert: Other participants still in list
        """
        # Arrange
        activity = sample_activity
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        email3 = "charlie@mergington.edu"
        
        client.post(f"/activities/{activity}/signup", params={"email": email1})
        client.post(f"/activities/{activity}/signup", params={"email": email2})
        client.post(f"/activities/{activity}/signup", params={"email": email3})
        
        # Act
        client.delete(f"/activities/{activity}/cancel", params={"email": email2})
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        # Assert
        assert email1 in participants
        assert email2 not in participants
        assert email3 in participants

    def test_participant_count_decreases(self, client, reset_activities, sample_activity):
        """
        Arrange: Multiple participants signed up
        Act: Cancel one participant
        Assert: Participant count decreases by 1
        """
        # Arrange
        activity = sample_activity
        emails = ["alice@mergington.edu", "bob@mergington.edu"]
        for email in emails:
            client.post(f"/activities/{activity}/signup", params={"email": email})
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Act
        client.delete(f"/activities/{activity}/cancel", params={"email": emails[0]})
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])
        
        # Assert
        assert count_after == count_before - 1


class TestActivitiesIndependence:
    """Test that activities are independent using AAA pattern."""

    def test_signup_in_one_activity_not_affect_other(self, client, reset_activities):
        """
        Arrange: Two different activities
        Act: Sign up participant in one activity
        Assert: Participant not in other activities
        """
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        email = "student@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        assert email in response.json()[activity1]["participants"]
        assert email not in response.json()[activity2]["participants"]

    def test_cancel_in_one_activity_not_affect_other(self, client, reset_activities):
        """
        Arrange: Participant in two activities, cancels one
        Act: Cancel in one activity
        Assert: Participant still in other activity
        """
        # Arrange
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        email = "student@mergington.edu"
        
        client.post(f"/activities/{activity1}/signup", params={"email": email})
        client.post(f"/activities/{activity2}/signup", params={"email": email})
        
        # Act
        client.delete(f"/activities/{activity1}/cancel", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        assert email not in response.json()[activity1]["participants"]
        assert email in response.json()[activity2]["participants"]
