"""
Unit tests for the main FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestMainEndpoints:
    """Test cases for main application endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """
        Test the root endpoint.
        
        In development mode, it should redirect to /docs.
        """
        response = client.get("/", follow_redirects=False)
        
        # Should redirect to docs in development
        assert response.status_code in [200, 307]
    
    def test_docs_endpoint(self, client: TestClient):
        """
        Test that API documentation is accessible.
        """
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "redoc" in response.text.lower()
    
    def test_redoc_endpoint(self, client: TestClient):
        """
        Test that ReDoc documentation is accessible.
        """
        response = client.get("/redoc")
        assert response.status_code == 200


@pytest.mark.unit
class TestApplicationLifecycle:
    """Test cases for application lifecycle events."""
    
    def test_app_starts_successfully(self, test_app):
        """
        Test that the application starts without errors.
        """
        assert test_app is not None
        assert test_app.title == "{{ cookiecutter.project_name }}"
    
    def test_cors_middleware_enabled(self, test_app):
        """
        Test that CORS middleware is configured.
        """
        # Check if CORSMiddleware is in the middleware stack
        middleware_types = [type(m) for m in test_app.user_middleware]
        from fastapi.middleware.cors import CORSMiddleware
        assert CORSMiddleware in middleware_types


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test cases for async endpoints."""
    
    async def test_async_root_endpoint(self, async_client):
        """
        Test the root endpoint using async client.
        """
        response = await async_client.get("/", follow_redirects=False)
        assert response.status_code in [200, 307]


@pytest.mark.unit
class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_not_found(self, client: TestClient):
        """
        Test that non-existent endpoints return 404.
        """
        response = client.get("/this-does-not-exist")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client: TestClient):
        """
        Test that wrong HTTP methods return 405.
        """
        # Try POST on an endpoint that only accepts GET
        response = client.post("/docs")
        assert response.status_code == 405


@pytest.mark.unit
class TestHealthCheck:
    """Test cases for health check functionality."""
    
    def test_application_healthy(self, client: TestClient):
        """
        Test that the application is healthy.
        """
        response = client.get("/")
        # As long as we get a response, the app is healthy
        assert response.status_code in [200, 307]
    
    def test_health_endpoint(self, client: TestClient):
        """
        Test the health check endpoint at root level.
        """
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "alive", "ready"]
    
    def test_health_live_endpoint(self, client: TestClient):
        """
        Test the liveness probe endpoint.
        """
        response = client.get("/health/live")
        assert response.status_code == 200
    
    def test_health_ready_endpoint(self, client: TestClient):
        """
        Test the readiness probe endpoint.
        """
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data

