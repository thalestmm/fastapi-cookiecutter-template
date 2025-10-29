"""
Pytest configuration and fixtures for testing.

This file contains shared fixtures that can be used across all tests.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient

from app.main import app
{% if cookiecutter.use_celery == 'y' %}
from app.worker.main import celery_app
{% endif %}


@pytest.fixture(scope="session")
def test_app():
    """
    Create a test instance of the FastAPI application.
    
    This fixture provides the FastAPI app for testing.
    Scope is session-wide to avoid recreating the app for each test.
    """
    return app


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """
    Create a test client for making requests to the API.
    
    This fixture provides a TestClient instance that can be used
    to make HTTP requests to the API endpoints.
    
    Example:
        def test_endpoint(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    with TestClient(test_app) as test_client:
        yield test_client


{% if cookiecutter.use_celery == 'y' %}
@pytest.fixture(scope="session")
def celery_config():
    """
    Override Celery configuration for testing.
    
    This fixture configures Celery to use an in-memory broker
    for testing purposes.
    """
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }


@pytest.fixture(scope="session")
def celery_worker_parameters():
    """
    Configure Celery worker parameters for testing.
    """
    return {
        'perform_ping_check': False,
    }


@pytest.fixture(scope="function")
def celery_test_app():
    """
    Provide Celery app instance for testing.
    """
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    return celery_app


{% endif %}
@pytest.fixture(scope="function")
def sample_data():
    """
    Provide sample data for testing.
    
    This fixture returns a dictionary of sample data that can be
    used in various tests.
    """
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25,
        "tags": ["test", "sample"],
    }


@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch):
    """
    Mock environment variables for testing.
    
    This fixture sets up test environment variables.
    """
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    {% if cookiecutter.use_celery == 'y' %}
    monkeypatch.setenv("CELERY_BROKER_URL", "memory://")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "cache+memory://")
    {% endif %}
    {% if cookiecutter.use_supabase == 'y' %}
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-key")
    {% endif %}


# Async fixtures for async tests
@pytest.fixture(scope="function")
async def async_client(test_app):
    """
    Create an async test client for testing async endpoints.
    
    Example:
        @pytest.mark.asyncio
        async def test_async_endpoint(async_client):
            response = await async_client.get("/")
            assert response.status_code == 200
    """
    from httpx import AsyncClient
    
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


__all__ = [
    "test_app",
    "client",
    "sample_data",
    "mock_env_vars",
    "async_client",
    {% if cookiecutter.use_celery == 'y' %}
    "celery_config",
    "celery_worker_parameters",
    "celery_test_app",
    {% endif %}
]

