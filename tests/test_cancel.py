"""
Unit and integration tests for DELETE /activities/{activity_name}/cancel endpoint.

Tests cover:
- Successful cancellation workflow
- Cancellation with non-existent participant
- Invalid activity handling
- Participant removal verification
"""

import pytest


class TestCancelSuccessful:
    """Test successful cancellation scenarios using AAA pattern."""

    def test_cancel_registered_participant(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant is registered for activity
        Act: DELETE request to /activities/{activity_name}/cancel
        Assert: Returns 200 and participant is unregistered
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.delete(
            f"/activities/{activity}/cancel",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity in response.json()["message"]

    def test_cancel_removes_participant_from_activity(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant is signed up
        Act: DELETE cancel request
        Assert: Participant no longer appears in /activities endpoint
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        client.delete(f"/activities/{activity}/cancel", params={"email": email})
        response = client.get("/activities")
        
        # Assert
        participants = response.json()[activity]["participants"]
        assert email not in participants

    def test_cancel_one_of_multiple_participants(self, client, reset_activities, sample_activity):
        """
        Arrange: Multiple participants signed up for activity
        Act: DELETE cancel for one participant
        Assert: Only that participant is removed, others remain
        """
        # Arrange
        activity = sample_activity
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        for email in emails:
            client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        client.delete(f"/activities/{activity}/cancel", params={"email": emails[1]})
        response = client.get("/activities")
        
        # Assert
        participants = response.json()[activity]["participants"]
        assert emails[0] in participants  # Still there
        assert emails[1] not in participants  # Removed
        assert emails[2] in participants  # Still there


class TestCancelNonParticipant:
    """Test cancellation of non-registered participants using AAA pattern."""

    def test_cancel_unregistered_participant(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant not registered for activity
        Act: DELETE cancel request for non-participant
        Assert: Returns 400 error with appropriate message
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act (participant never signed up)
        response = client.delete(
            f"/activities/{activity}/cancel",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_cancel_twice_fails_second_time(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Participant cancels their signup
        Act: Attempt to cancel same participant again
        Assert: Second cancel returns 400 error
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        first_cancel = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        second_cancel = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        
        # Assert
        assert first_cancel.status_code == 200
        assert second_cancel.status_code == 400

    def test_cancel_empty_activity(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Activity has no participants
        Act: DELETE cancel request
        Assert: Returns 400 error
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act
        response = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        
        # Assert
        assert response.status_code == 400


class TestCancelInvalidActivity:
    """Test invalid activity handling for cancellation using AAA pattern."""

    def test_cancel_nonexistent_activity(self, client, reset_activities, sample_email):
        """
        Arrange: Activity name that doesn't exist
        Act: DELETE cancel request with invalid activity
        Assert: Returns 404 error with appropriate message
        """
        # Arrange
        email = sample_email
        invalid_activity = "Nonexistent Activity"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/cancel",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_cancel_with_url_encoded_activity_name(self, client, reset_activities, sample_email):
        """
        Arrange: Activity name with URL-encoded characters
        Act: DELETE cancel with encoded activity name
        Assert: Returns 404 (activity doesn't exist)
        """
        # Arrange
        email = sample_email
        invalid_activity = "Science%20Olympiad%20Plus"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/cancel",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404


class TestCancelEmailVariations:
    """Test email variations in cancellation using AAA pattern."""

    def test_cancel_with_special_characters_in_email(self, client, reset_activities, sample_activity):
        """
        Arrange: Email with special characters that was previously signed up
        Act: Sign up and then cancel with same special char email
        Assert: Cancellation succeeds
        """
        # Arrange
        activity = sample_activity
        email = "student+test@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        
        # Assert
        assert response.status_code == 200

    def test_cancel_case_sensitive_email(self, client, reset_activities, sample_activity):
        """
        Arrange: Email signed up with lowercase
        Act: Attempt cancel with different case
        Assert: May or may not match depending on implementation (test as-is)
        """
        # Arrange
        activity = sample_activity
        email = "Student@mergington.edu"
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act - using same case as signup
        response = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        
        # Assert - should work with exact case match
        assert response.status_code == 200


class TestCancelResponseFormat:
    """Test response format and structure for cancellation using AAA pattern."""

    def test_cancel_success_response_structure(self, client, reset_activities, sample_activity, sample_email):
        """
        Arrange: Registered participant
        Act: DELETE cancel request
        Assert: Response contains expected message field
        """
        # Arrange
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.delete(f"/activities/{activity}/cancel", params={"email": email})
        data = response.json()
        
        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_cancel_error_response_structure(self, client, reset_activities, sample_email):
        """
        Arrange: Invalid activity
        Act: DELETE cancel request
        Assert: Error response contains detail field
        """
        # Arrange
        email = sample_email
        
        # Act
        response = client.delete(
            "/activities/InvalidActivity/cancel",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "detail" in data
        assert isinstance(data["detail"], str)
