# Test Suite

This directory contains the test suite for {{ cookiecutter.project_name }}.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_main.py
```

### Run Specific Test Class or Function

```bash
# Run a specific class
pytest tests/test_main.py::TestMainEndpoints

# Run a specific test
pytest tests/test_main.py::TestMainEndpoints::test_root_endpoint
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

{% if cookiecutter.use_celery == 'y' %}
# Run only Celery tests
pytest -m celery
{% endif %}
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared fixtures and configuration
├── test_main.py             # Tests for main application
{% if cookiecutter.use_celery == 'y' %}├── test_celery_tasks.py     # Tests for Celery tasks
├── test_celery_api.py       # Tests for Celery API endpoints
{% endif %}└── README.md                # This file
```

## Writing Tests

### Basic Test Example

```python
def test_example(client):
    """Test description."""
    response = client.get("/endpoint")
    assert response.status_code == 200
    assert response.json() == {"key": "value"}
```

### Async Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_async_example(async_client):
    """Async test description."""
    response = await async_client.get("/endpoint")
    assert response.status_code == 200
```

{% if cookiecutter.use_celery == 'y' %}
### Celery Task Test Example

```python
@pytest.mark.celery
def test_task_example(celery_test_app):
    """Test Celery task."""
    from app.worker.tasks import my_task
    
    result = my_task.apply(args=[1, 2])
    assert result.get() == expected_value
```
{% endif %}

### Using Fixtures

```python
def test_with_fixtures(client, sample_data):
    """Test using multiple fixtures."""
    response = client.post("/endpoint", json=sample_data)
    assert response.status_code == 201
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('app.services.external_api.call')
def test_with_mock(mock_call, client):
    """Test with mocked external service."""
    mock_call.return_value = {"data": "mocked"}
    
    response = client.get("/endpoint")
    assert response.status_code == 200
    mock_call.assert_called_once()
```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_unit():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_integration(client):
    """Integration test example."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test example."""
    pass
```

## Fixtures

Common fixtures available in `conftest.py`:

- `test_app`: FastAPI application instance
- `client`: Synchronous test client
- `async_client`: Asynchronous test client
- `sample_data`: Sample data dictionary
- `mock_env_vars`: Mocked environment variables
{% if cookiecutter.use_celery == 'y' %}- `celery_test_app`: Celery app for testing
- `celery_config`: Celery configuration
{% endif %}

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **Mock External Dependencies**: Don't make real API calls or database connections
5. **Use Fixtures**: Share common setup code via fixtures
6. **Test Edge Cases**: Test both happy path and error cases
7. **Keep Tests Fast**: Mock slow operations
8. **One Assertion Per Test**: Focus each test on one thing

## Continuous Integration

Tests are automatically run in CI/CD pipelines. Ensure all tests pass before merging.

## Troubleshooting

### Import Errors

If you get import errors, ensure you're in the backend directory:
```bash
cd backend
pytest
```

### Celery Tests Failing

For Celery tests, ensure `task_always_eager=True` is set in test configuration.

### Async Tests Not Running

Ensure `pytest-asyncio` is installed:
```bash
pip install pytest-asyncio
```

## Coverage Goals

Aim for:
- **Overall**: 80%+ code coverage
- **Critical paths**: 95%+ coverage
- **Business logic**: 90%+ coverage

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

