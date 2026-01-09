# Backend Tests

Comprehensive test suite for the refactored backend with dependency injection.

## Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── unit/                            # Unit tests with mocked dependencies
│   ├── test_integrations/          # Tests for integration clients
│   │   ├── test_stripe_client.py   # Stripe SDK wrapper tests
│   │   └── test_email_client.py    # Email/SMTP client tests
│   └── test_services/              # Tests for business services
│       ├── test_user_service.py    # User service tests
│       ├── test_subscription_service.py
│       └── test_waitlist_service.py
└── integration/                     # Integration tests (future)
```

## Running Tests

### Run all tests
```bash
cd backend
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_services/test_user_service.py
```

### Run tests by marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with coverage
```bash
pytest --cov=backend --cov-report=html
```

### Run specific test
```bash
pytest tests/unit/test_services/test_user_service.py::TestUserService::test_delete_account
```

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

### Configuration Fixtures
- `stripe_config` - Mock Stripe configuration
- `email_config` - Mock Email configuration
- `github_config` - Mock GitHub configuration
- `llm_config` - Mock LLM configuration

### Client Fixtures
- `mock_supabase_client` - Mocked Supabase database client
- `mock_stripe_client` - Mocked Stripe integration client
- `mock_email_client` - Mocked Email client
- `mock_github_client` - Mocked GitHub client
- `mock_llm_client` - Mocked LLM client

### Service Fixtures
- `user_service` - UserService with mocked dependencies
- `subscription_service` - SubscriptionService with mocked Stripe
- `waitlist_service` - WaitlistService with mocked Email
- `portfolio_service` - PortfolioService instance
- `project_service` - ProjectService instance
- `auth_service` - AuthService instance
- `mfa_service` - MFAService instance

## Writing Tests

### Example: Testing a Service with Dependencies

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestUserService:
    """Test suite for UserService"""

    @pytest.mark.asyncio
    async def test_delete_account(self, user_service, mock_supabase_client, mock_stripe_client):
        """Test deleting user account"""
        # Setup mocks
        mock_stripe_client.cancel_subscription = AsyncMock()

        # Execute
        result = await user_service.delete_account(
            mock_supabase_client,
            "user_123"
        )

        # Assert
        assert result.success is True
        mock_stripe_client.cancel_subscription.assert_called_once()
```

### Example: Testing an Integration Client

```python
@pytest.mark.asyncio
@patch('backend.integrations.stripe_client.stripe.checkout.Session.create')
async def test_create_checkout_session(self, mock_stripe_create, stripe_config):
    """Test Stripe checkout session creation"""
    # Setup mock
    mock_stripe_create.return_value = Mock(id="cs_123", url="https://checkout")

    # Execute
    client = StripeClient(stripe_config)
    result = await client.create_checkout_session(...)

    # Assert
    assert result["session_id"] == "cs_123"
```

## Test Philosophy

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Mocking**: All external dependencies are mocked
- **Speed**: Fast execution
- **Focus**: Business logic and error handling

### Integration Tests (Future)
- **Purpose**: Test interaction between components
- **Mocking**: Minimal mocking, use test database
- **Speed**: Slower execution
- **Focus**: End-to-end workflows

## Benefits of Current Test Structure

1. **Tests the DI Architecture**: Validates dependency injection works correctly
2. **Fast Execution**: All external calls are mocked
3. **Isolation**: Tests don't depend on external services
4. **Coverage**: Tests both success and error paths
5. **Documentation**: Tests serve as usage examples
6. **Refactoring Safety**: Tests ensure behavior remains consistent

## Next Steps

1. Add more service tests (Portfolio, Project, Auth, MFA)
2. Add integration tests with test database
3. Add router/endpoint tests with TestClient
4. Set up CI/CD to run tests automatically
5. Add code coverage requirements

## Dependencies

Required packages (should be in requirements.txt):
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
```
