"""
Shared test fixtures and configuration for FastAPI tests.

This module provides:
- TestClient for HTTP testing
- Sample activity fixtures
- Database reset functionality
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Arrange: Create a TestClient instance for making HTTP requests.
    
    Provides access to the FastAPI test client for integration testing.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Arrange: Reset activities to a clean state for each test.
    
    This fixture clears all participants from each activity before each test
    to ensure tests don't affect each other.
    """
    original_state = {}
    
    # Store original state
    for activity_name, activity_data in activities.items():
        original_state[activity_name] = activity_data["participants"].copy()
    
    # Clear participants before test
    for activity_data in activities.values():
        activity_data["participants"] = []
    
    yield
    
    # Restore original state after test
    for activity_name, participants_list in original_state.items():
        activities[activity_name]["participants"] = participants_list.copy()


@pytest.fixture
def sample_email():
    """
    Arrange: Provide a sample valid email for testing.
    
    Returns a standard format email for signup tests.
    """
    return "student@mergington.edu"


@pytest.fixture
def sample_activity():
    """
    Arrange: Provide a sample activity name for testing.
    
    Returns an activity name that exists in the database.
    """
    return "Chess Club"
