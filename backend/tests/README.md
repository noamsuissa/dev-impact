# Backend Tests

This directory contains unit tests for the Dev Impact backend services and utilities.

## Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration (in backend/)
├── services/
│   ├── __init__.py
│   ├── test_badge_service.py
│   ├── test_user_service.py
│   ├── test_project_service.py
│   └── ...
└── utils/
    ├── __init__.py
    └── test_auth_utils.py
```

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run specific test file
```bash
pytest tests/services/test_badge_service.py
```

### Run specific test class
```bash
pytest tests/services/test_badge_service.py::TestGetBadgeDefinitions
```

### Run specific test method
```bash
pytest tests/services/test_badge_service.py::TestGetBadgeDefinitions::test_get_all_badge_definitions_success
```

### Run with coverage (requires pytest-cov)
```bash
pip install pytest-cov
pytest --cov=backend --cov-report=html
```

### Run tests by marker
```bash
pytest -m badge      # Run only badge-related tests
pytest -m unit       # Run only unit tests
pytest -m slow       # Run only slow tests
```

## Testing Principles

### 1. Dependency Injection Pattern
All service methods accept a Supabase client as the first parameter. This makes testing easy:

```python
def test_example(mock_supabase_client):
    # Just pass the mock client directly to the service method
    result = ServiceClass.method_name(mock_supabase_client, ...)
    
    # No need to mock dependency functions!
```

### 2. Test Structure (AAA Pattern)
Every test follows the Arrange-Act-Assert pattern:

```python
def test_method_success(mock_supabase_client):
    # Arrange: Set up test data and mocks
    mock_response = MagicMock()
    mock_response.data = {...}
    mock_supabase_client.table.return_value...return_value = mock_response
    
    # Act: Call the function being tested
    result = Service.method(mock_supabase_client, "arg")
    
    # Assert: Verify the expected outcome
    assert result.field == "expected_value"
    mock_supabase_client.table.assert_called_with("table_name")
```

### 3. Comprehensive Coverage
Each service method must have tests for:
- ✅ **Happy path** - successful operation with valid inputs
- ✅ **Error cases** - expected failures (404, 401, 500, etc.)
- ✅ **Edge cases** - empty results, boundary conditions, special inputs
- ✅ **Authorization** - verify user ownership checks

### 4. Mocking External Dependencies
Always mock:
- Supabase database calls
- External API calls (GitHub, Stripe, etc.)
- Email services
- File system operations

Never make real external calls in unit tests.

## Test Fixtures

Common fixtures are defined in `conftest.py`:
- `mock_supabase_client` - Mock Supabase client
- `sample_user_id` - Standard user ID
- `sample_project_id` - Standard project ID
- `sample_badge_id` - Standard badge ID

Test-specific fixtures are defined at the top of each test file.

## Example: Adding Tests for a New Service

1. **Create service file**: `backend/services/my_service.py`
2. **Create test file**: `backend/tests/services/test_my_service.py`
3. **Import required modules**:
   ```python
   import pytest
   from unittest.mock import MagicMock
   from fastapi import HTTPException
   from backend.services.my_service import MyService
   ```
4. **Create fixtures for test data**
5. **Write test classes** organized by method
6. **Write test methods** for each scenario
7. **Run tests**: `pytest tests/services/test_my_service.py`

## Debugging Tests

### Verbose output
```bash
pytest -vv
```

### Show print statements
```bash
pytest -s
```

### Stop on first failure
```bash
pytest -x
```

### Drop into debugger on failure
```bash
pytest --pdb
```

### Run last failed tests only
```bash
pytest --lf
```

## Coverage Goals

- **Minimum**: 80% code coverage
- **Target**: 90%+ code coverage
- Focus on critical business logic
- 100% coverage for security-critical code (auth, payments)

## Continuous Integration

Tests should be run automatically on:
- Every commit
- Pull requests
- Before deployment

## Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Use descriptive names** - Test names should describe what they test
3. **One assertion per concept** - Focus each test on one behavior
4. **Fast tests** - Unit tests should run in milliseconds
5. **No flaky tests** - Tests should be deterministic
6. **Mock external dependencies** - Never rely on external services
7. **Test business logic** - Focus on logic, not implementation details
8. **Update tests with code** - Keep tests in sync with code changes

## Common Patterns

### Testing async methods
```python
@pytest.mark.asyncio
async def test_async_method(mock_supabase_client):
    result = await Service.async_method(mock_supabase_client, "arg")
    assert result is not None
```

### Testing HTTPException
```python
def test_method_not_found(mock_supabase_client):
    with pytest.raises(HTTPException) as exc_info:
        Service.method(mock_supabase_client, "invalid_id")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
```

### Mocking chained Supabase calls
```python
mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
```