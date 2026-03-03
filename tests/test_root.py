"""
Unit and integration tests for GET / endpoint.

Tests cover:
- Redirect behavior
- Redirect destination
- Status codes
"""

import pytest


class TestRootRedirect:
    """Test root path redirect behavior using AAA pattern."""

    def test_root_returns_redirect(self, client):
        """
        Arrange: Client ready to make request
        Act: GET request to /
        Assert: Returns 307 redirect status code
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client ready to make request
        Act: GET request to / with redirect following
        Assert: Redirects to /static/index.html
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        # Check that we successfully got the HTML page
        assert response.status_code == 200
        assert "html" in response.text.lower()

    def test_root_redirect_location_header(self, client):
        """
        Arrange: Client making request without following redirects
        Act: GET request to /
        Assert: Location header points to /static/index.html
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert "location" in response.headers
        assert response.headers["location"] == "/static/index.html"


class TestRootResponseFormat:
    """Test root endpoint response format using AAA pattern."""

    def test_root_response_format_is_redirect(self, client):
        """
        Arrange: Making GET request
        Act: GET /
        Assert: Response is a redirect response
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        # 3xx status code indicates redirect
        assert 300 <= response.status_code < 400

    def test_root_followed_has_html_content_type(self, client):
        """
        Arrange: Making request with redirect following
        Act: GET / (follow redirects)
        Assert: Final response has HTML content type
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert "text/html" in response.headers.get("content-type", "")


class TestRootEndpointConsistency:
    """Test root endpoint consistency using AAA pattern."""

    def test_root_always_redirects_to_same_location(self, client):
        """
        Arrange: Making multiple requests
        Act: GET / multiple times
        Assert: All requests redirect to same location
        """
        # Arrange
        expected_location = "/static/index.html"
        
        # Act & Assert
        for _ in range(3):
            response = client.get("/", follow_redirects=False)
            assert response.headers["location"] == expected_location

    def test_root_redirect_independent_of_headers(self, client):
        """
        Arrange: Requests with different headers
        Act: GET / with various headers
        Assert: All redirect consistently
        """
        # Arrange
        # (client provided by fixture)
        
        # Act
        response1 = client.get("/", follow_redirects=False)
        response2 = client.get(
            "/",
            headers={"User-Agent": "Custom Agent"},
            follow_redirects=False
        )
        
        # Assert
        assert response1.headers["location"] == response2.headers["location"]
