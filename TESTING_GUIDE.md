# Testing Guide for RAG Story Application

This guide provides comprehensive information about testing the RAG Story Application.

## Table of Contents
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The application uses pytest for testing with the following key features:
- **Async Support**: Using `pytest-asyncio` for async function testing
- **Database Isolation**: Each test runs in a transaction that's rolled back
- **Fixture-based Setup**: Reusable test data and configurations
- **API Testing**: Using `httpx.AsyncClient` for testing FastAPI endpoints

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_auth_api.py         # Authentication endpoint tests
├── test_story_api.py        # Story API endpoint tests
├── test_story_class_api.py  # Story class API tests
├── test_story_crud.py       # Story CRUD operation tests
├── test_story_class_crud.py # Story class CRUD tests
├── test_user_crud.py        # User CRUD tests
├── test_act_crud.py         # Act CRUD tests
└── test_security.py         # Security and authentication tests
```

## Running Tests

### Quick Start
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_story_api.py

# Run specific test function
pytest tests/test_story_api.py::test_create_story_api

# Run with coverage
pytest --cov=app --cov-report=html
```

### Using the Test Runner Script
```bash
# Run comprehensive test suite with reporting
python run_tests.py
```

### Environment Setup
```bash
# Create test database
createdb ragstory_test

# Set environment variables
export TEST_POSTGRES_DB=ragstory_test
export TEST_POSTGRES_USER=testuser
export TEST_POSTGRES_PASSWORD=testpass
```

## Writing Tests

### Basic Test Structure
```python
import pytest
from httpx import AsyncClient

# Mark module for async
pytestmark = pytest.mark.asyncio

async def test_example(
    async_test_client: AsyncClient,
    test_auth_headers: dict,
    test_world
):
    """Test description."""
    response = await async_test_client.get(
        f"/api/worlds/{test_world.id}",
        headers=test_auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == test_world.id
```

### Testing CRUD Operations
```python
async def test_create_item(db_session: AsyncSession):
    """Test creating an item."""
    from app.crud.item import create_item
    from app.schemas.item import ItemCreate
    
    item_data = ItemCreate(name="Test Item")
    item = await create_item(db=db_session, item=item_data)
    
    assert item.name == "Test Item"
    assert item.id is not None
```

### Testing API Endpoints
```python
async def test_api_endpoint(
    async_test_client: AsyncClient,
    test_auth_headers: dict
):
    """Test API endpoint."""
    data = {"name": "Test"}
    
    response = await async_test_client.post(
        "/api/items/",
        json=data,
        headers=test_auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == data["name"]
```

## Test Fixtures

### Available Fixtures

#### Authentication Fixtures
- `test_user`: Creates a regular test user
- `admin_user`: Creates an admin test user  
- `test_auth_headers`: Provides auth headers for regular user
- `admin_auth_headers`: Provides auth headers for admin user

#### Data Fixtures
- `test_world`: Creates a test world
- `test_story`: Creates a test story
- `test_story_class`: Creates a test story class
- `test_act`: Creates a test act
- `test_character`: Creates a test character

#### Database Fixtures
- `db_session`: Provides isolated database session
- `async_test_client`: Provides HTTP client for API testing

### Creating Custom Fixtures
```python
@pytest_asyncio.fixture
async def custom_fixture(db_session: AsyncSession):
    """Create custom test data."""
    # Setup
    data = await create_test_data(db_session)
    
    yield data  # Provide to test
    
    # Cleanup (if needed)
    await cleanup_test_data(db_session, data)
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use transactions that rollback after each test
- Don't rely on test execution order

### 2. Clear Test Names
```python
# Good
async def test_create_story_with_valid_data_succeeds():
async def test_update_story_by_non_owner_returns_403():

# Bad
async def test_story():
async def test_1():
```

### 3. Arrange-Act-Assert Pattern
```python
async def test_example():
    # Arrange
    data = prepare_test_data()
    
    # Act
    result = await perform_action(data)
    
    # Assert
    assert result.status == "success"
```

### 4. Test Edge Cases
- Empty inputs
- Invalid data types
- Boundary values
- Permission checks
- Error conditions

### 5. Use Fixtures Effectively
```python
# Good - Reusable fixtures
async def test_with_fixtures(test_user, test_world):
    # Use pre-created test data
    
# Bad - Creating data in each test
async def test_without_fixtures(db_session):
    user = await create_user(...)  # Repeated in many tests
    world = await create_world(...)  # Repeated in many tests
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database exists
psql -U postgres -c "SELECT datname FROM pg_database WHERE datname = 'ragstory_test';"

# Check connection string
echo $TEST_DATABASE_URL
```

#### 2. Async Test Failures
```python
# Ensure test is marked async
@pytest.mark.asyncio
async def test_async_function():
    # OR use pytestmark at module level
```

#### 3. Import Errors
```bash
# Ensure project is in PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or install in development mode
pip install -e .
```

#### 4. Fixture Not Found
```python
# Check fixture is in conftest.py or imported
# Check fixture scope matches usage
```

### Debugging Tests
```bash
# Run with full traceback
pytest -vv --tb=long

# Run with print statements visible
pytest -s

# Run with debugger
pytest --pdb

# Run specific test with debugging
pytest -k "test_name" -vv --pdb
```

### Test Database Reset
```bash
# Drop and recreate test database
dropdb ragstory_test
createdb ragstory_test

# Run migrations
alembic upgrade head
```

## Performance Testing

### Load Testing Example
```python
import asyncio
import time

async def test_concurrent_requests(async_test_client):
    """Test API under concurrent load."""
    async def make_request():
        return await async_test_client.get("/api/stories/")
    
    start_time = time.time()
    
    # Make 100 concurrent requests
    tasks = [make_request() for _ in range(100)]
    responses = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # Should complete in reasonable time
    assert duration < 5.0  # seconds
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: ragstory_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy testing guide](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)