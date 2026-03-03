"""
Unit and integration tests for POST /activities/{activity_name}/signup endpoint.

Tests cover:
- Successful signup workflow
- Duplicate signup prevention
- Invalid activity handling
- Email validation
"""

import pytest


class TestSignupSuccessful:
    """Test successful signup scenarios using AAA pattern."""

    def test_signup_valid_activity_and_email(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Valid activity name and email
        Act: POST request to /activities/{activity_name}/signup
        Assert: Returns 200, includes participant in response
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Empty participant list for activity
        Act: POST signup request
        Assert: Participant appears in /activities endpoint
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_multiple_different_students(self, client, reset_activities, sample_activity):
        """
        Arrange: Multiple unique emails
        Act: Each POST signup request with different email
        Assert: All participants are added to the activity
        """
        # Arrange
        activity = sample_activity
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # Act & Assert
        for email in emails:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Verify all are in the activity
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants


class TestSignupDuplicatePrevention:
    """Test duplicate signup prevention using AAA pattern."""

    def test_duplicate_signup_rejected(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Student already signed up for activity
        Act: Attempt to sign up same student again
        Assert: Returns 400 error with appropriate message
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_duplicate_signup_does_not_add_twice(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Student signs up once
        Act: Attempt duplicate signup
        Assert: Participant list contains email only once
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert participants.count(email) == 1


class TestSignupInvalidActivity:
    """Test invalid activity handling using AAA pattern."""

    def test_signup_nonexistent_activity(self, client, reset_activities, sample_email):
        """
        Arrange: Activity name that doesn't exist
        Act: POST signup request with invalid activity
        Assert: Returns 404 error with appropriate message
        """
        # Arrange
        email = sample_email
        invalid_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_with_special_characters_in_activity(self, client, reset_activities, sample_email):
        """
        Arrange: Activity name with URL-encoded special characters
        Act: POST signup with URL-encoded activity name
        Assert: Returns 404 (activity doesn't exist)
        """
        # Arrange
        email = sample_email
        invalid_activity = "Art%20Studio%20Advanced"  # URL-encoded
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404


class TestSignupEmailFormats:
    """Test various email format handling using AAA pattern."""

    def test_signup_with_valid_email_formats(self, client, reset_activities, sample_activity):
        """
        Arrange: Various valid email formats
        Act: POST signup with each email format
        Assert: All are accepted and stored
        """
        # Arrange
        activity = sample_activity
        emails = [
            "student123@mergington.edu",
            "john.doe@mergington.edu",
            "a@mergington.edu",
        ]
        
        # Act & Assert
        for email in emails:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200

    def test_signup_with_special_characters_in_email(self, client, reset_activities, sample_activity):
        """
        Arrange: Email with special characters (not URL-encoded)
        Act: POST signup with special char email
        Assert: Email is accepted and stored as-is
        """
        # Arrange
        activity = sample_activity
        email = "student+test@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Assert
        assert response.status_code == 200
        response_check = client.get("/activities")
        assert email in response_check.json()[activity]["participants"]


class TestSignupResponseFormat:
    """Test response format and structure using AAA pattern."""

    def test_signup_success_response_structure(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Valid signup request
        Act: POST to signup endpoint
        Assert: Response contains expected message field
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        data = response.json()
        
        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
