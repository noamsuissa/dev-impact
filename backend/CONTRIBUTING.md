# Contributing to Dev Impact Backend

Thank you for your interest in contributing to the Dev Impact backend! This document provides guidelines for contributing code that adheres to our design patterns and architecture.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Design Pattern Guidelines](#design-pattern-guidelines)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [File Organization](#file-organization)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Follow the established patterns and conventions
- Write clear, maintainable code

## Design Pattern Guidelines

This project follows specific design patterns. **All contributions must adhere to these patterns** to maintain consistency and code quality.

### 1. Layered Architecture Pattern

**Rule**: Always maintain clear separation between layers.

#### ✅ DO:
- Put HTTP request/response handling in `routers/`
- Put business logic in `services/`
- Put data validation models in `schemas/`
- Put shared utilities in `utils/`

#### ❌ DON'T:
- Put database queries directly in routers
- Put HTTP-specific code in services
- Put business logic in schemas
- Mix concerns across layers

**Example - Adding a new feature:**

```python
# ✅ CORRECT: Router handles HTTP, calls service
# routers/example.py
@router.post("/example", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    user_id = auth_utils.get_user_id_from_token(authorization)
    result = await ExampleService.create_example(user_id, request.data)
    return result

# ✅ CORRECT: Service contains business logic
# services/example_service.py
class ExampleService:
    @staticmethod
    async def create_example(user_id: str, data: dict) -> ExampleResponse:
        # Business logic here
        supabase = get_supabase_client()
        # Database operations
        return ExampleResponse(...)
```

### 2. Service Pattern (Static Methods)

**Rule**: All service classes use static methods only.

#### ✅ DO:
```python
class ExampleService:
    @staticmethod
    async def create_example(user_id: str, data: dict):
        # Implementation
        pass
    
    @staticmethod
    async def get_example(example_id: str):
        # Implementation
        pass
```

#### ❌ DON'T:
```python
# Don't use instance methods
class ExampleService:
    def __init__(self):
        self.client = get_supabase_client()  # ❌ No instance state
    
    async def create_example(self, user_id: str):  # ❌ Instance method
        pass

# Don't use class methods
class ExampleService:
    @classmethod
    async def create_example(cls, user_id: str):  # ❌ Class method
        pass
```

**Why**: Services are stateless. Static methods make this explicit and simplify testing.

### 3. Schema/Model Pattern

**Rule**: Use Pydantic models for all request/response validation.

#### ✅ DO:
```python
# schemas/example.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class ExampleRequest(BaseModel):
    """Example request schema"""
    name: str
    email: EmailStr
    description: Optional[str] = None

class ExampleResponse(BaseModel):
    """Example response schema"""
    id: str
    name: str
    created_at: str
```

#### ❌ DON'T:
```python
# Don't use dicts for request/response
@router.post("/example")
async def create_example(data: dict):  # ❌ No validation
    pass

# Don't skip schema definitions
@router.post("/example")
async def create_example(name: str, email: str):  # ❌ No model
    pass
```

**Guidelines:**
- Always define request and response schemas
- Use appropriate Pydantic field types (`EmailStr`, `Optional`, etc.)
- Add docstrings to schemas
- Use descriptive field names

### 4. Error Handling Pattern

**Rule**: Follow consistent error handling across all services.

#### ✅ DO:
```python
try:
    # Operation
    result = supabase.table("example").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create example")
    return result.data[0]
except HTTPException:
    raise  # Re-raise known HTTP exceptions
except Exception as e:
    print(f"Error in create_example: {e}")
    raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

#### ❌ DON'T:
```python
# Don't catch and swallow errors
try:
    result = operation()
except Exception:
    pass  # ❌ Silent failure

# Don't expose internal errors
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # ❌ May expose sensitive info

# Don't use generic error messages for known errors
except ValueError:
    raise HTTPException(status_code=500, detail="Error")  # ❌ Should be 400 with specific message
```

**Error Handling Checklist:**
- [ ] Catch `HTTPException` and re-raise (don't modify)
- [ ] Catch generic `Exception` for unexpected errors
- [ ] Log errors before raising
- [ ] Use appropriate HTTP status codes (400, 401, 403, 404, 500)
- [ ] Return user-friendly error messages
- [ ] Don't expose internal implementation details

### 5. Dependency Injection Pattern

**Rule**: Use FastAPI's `Depends()` for authentication and shared logic.

#### ✅ DO:
```python
from fastapi import Depends
from utils import auth_utils

@router.get("/protected")
async def protected_endpoint(
    authorization: str = Depends(auth_utils.get_access_token)
):
    user_id = auth_utils.get_user_id_from_token(authorization)
    # Use user_id
```

#### ❌ DON'T:
```python
# Don't manually parse headers
@router.get("/protected")
async def protected_endpoint(authorization: Optional[str] = Header(None)):
    if not authorization:  # ❌ Duplicate logic
        raise HTTPException(status_code=401)
    token = authorization.replace("Bearer ", "")
    # ...

# Don't skip authentication checks
@router.get("/protected")
async def protected_endpoint():  # ❌ No auth check
    # ...
```

**Guidelines:**
- Use `auth_utils.get_access_token` for protected endpoints
- Extract user_id using `auth_utils.get_user_id_from_token()`
- Create reusable dependencies for common patterns

### 6. Repository Pattern (Supabase Client)

**Rule**: Always use `get_supabase_client()` from `utils/auth_utils.py`.

#### ✅ DO:
```python
from utils.auth_utils import get_supabase_client

supabase = get_supabase_client(access_token=token)
result = supabase.table("example").select("*").execute()
```

#### ❌ DON'T:
```python
# Don't create clients directly
from supabase import create_client
supabase = create_client(url, key)  # ❌ Bypasses factory

# Don't hardcode credentials
supabase = create_client("https://...", "key...")  # ❌ Hardcoded values
```

**Guidelines:**
- Always use `get_supabase_client()` factory function
- Pass `access_token` when you need user-scoped operations
- Don't pass `access_token` for admin operations (uses service role key)

### 7. File Organization Pattern

**Rule**: Follow the established directory structure.

#### Directory Structure:
```
routers/          # One file per domain (auth, profile, projects, etc.)
services/         # One file per domain, or subdirectory for complex domains
schemas/          # One file per domain, matching router/service names
utils/            # Shared utilities (one file per utility category)
```

#### ✅ DO:
- Create new router file for new domain: `routers/new_feature.py`
- Create matching service: `services/new_feature_service.py`
- Create matching schemas: `schemas/new_feature.py`
- Keep related code together

#### ❌ DON'T:
- Don't put everything in one file
- Don't mix domains in single files
- Don't create deep nested structures unnecessarily

**Example - Adding a "Comments" feature:**
```
routers/
  └── comments.py          # Comment endpoints
services/
  └── comment_service.py   # Comment business logic
schemas/
  └── comment.py          # Comment request/response models
```

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your values
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming:**
- `feat/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

### 3. Make Changes

Follow the design patterns outlined above. When adding new code:

1. **Start with Schemas**: Define your data models first
   ```python
   # schemas/your_feature.py
   class YourFeatureRequest(BaseModel):
       field: str
   ```

2. **Create Service**: Implement business logic
   ```python
   # services/your_feature_service.py
   class YourFeatureService:
       @staticmethod
       async def create_feature(data: dict):
           # Logic here
           pass
   ```

3. **Add Router**: Create API endpoints
   ```python
   # routers/your_feature.py
   @router.post("/your-feature", response_model=YourFeatureResponse)
   async def create_feature(request: YourFeatureRequest):
       return await YourFeatureService.create_feature(request.model_dump())
   ```

4. **Register Router**: Add to `main.py`
   ```python
   from routers import your_feature
   app.include_router(your_feature.router)
   ```

### 4. Test Your Changes

```bash
# Start the server
python main.py

# Test endpoints using:
# - Swagger UI: http://localhost:3000/docs
# - curl commands
# - Postman/Insomnia
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request with:
- Clear description of changes
- Reference to related issues
- Screenshots (if UI changes)
- Checklist of completed items

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return types
- Maximum line length: **100 characters** (soft limit)
- Use **4 spaces** for indentation (no tabs)

### Code Formatting

```python
# ✅ Good: Type hints, clear names, docstring
async def create_profile(
    user_id: str,
    profile_data: dict,
    access_token: str
) -> ProfileResponse:
    """
    Create a new user profile.
    
    Args:
        user_id: The user's ID
        profile_data: Profile data dictionary
        access_token: User's access token
        
    Returns:
        ProfileResponse containing created profile
        
    Raises:
        HTTPException: If profile creation fails
    """
    # Implementation
    pass
```

### Naming Conventions

- **Files**: `snake_case.py` (e.g., `user_profile.py`)
- **Classes**: `PascalCase` (e.g., `UserProfileService`)
- **Functions/Methods**: `snake_case` (e.g., `get_user_profile`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- **Variables**: `snake_case` (e.g., `user_id`)

### Documentation

**All public functions must have docstrings:**

```python
@staticmethod
async def publish_profile(
    username: str,
    profile_id: str,
    user_id: str,
    token: str
) -> PublishProfileResponse:
    """
    Publish or update a user profile in Supabase.
    
    Args:
        username: The user's username
        profile_id: The profile ID to publish
        user_id: The authenticated user's ID
        token: The user's auth token
        
    Returns:
        PublishProfileResponse with success status, username, profile_slug, and URL
        
    Raises:
        HTTPException: If username is invalid, profile not found, or publish fails
    """
    # Implementation
```

## File Organization

### Router Files

```python
"""
[Domain] Router - Handle [domain] endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from schemas.[domain] import RequestModel, ResponseModel
from services.[domain]_service import DomainService
from utils import auth_utils

router = APIRouter(
    prefix="/api/[domain]",
    tags=["[domain]"],
)

@router.post("", response_model=ResponseModel)
async def create_resource(
    request: RequestModel,
    authorization: str = Depends(auth_utils.get_access_token)
):
    """Create a new resource"""
    user_id = auth_utils.get_user_id_from_token(authorization)
    result = await DomainService.create_resource(user_id, request.model_dump())
    return result
```

### Service Files

```python
"""
[Domain] Service - Handle [domain] business logic and Supabase operations
"""
from typing import Optional
from fastapi import HTTPException
from utils.auth_utils import get_supabase_client
from schemas.[domain] import ResponseModel

class DomainService:
    """Service for handling [domain] operations."""
    
    @staticmethod
    async def create_resource(user_id: str, data: dict) -> ResponseModel:
        """
        Create a new resource.
        
        Args:
            user_id: User's ID
            data: Resource data
            
        Returns:
            ResponseModel containing created resource
        """
        try:
            supabase = get_supabase_client()
            # Business logic and database operations
            result = supabase.table("resources").insert(data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create resource")
            return ResponseModel(**result.data[0])
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in create_resource: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

### Schema Files

```python
"""
[Domain] Schemas - Pydantic models for [domain]
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateRequest(BaseModel):
    """Create request schema"""
    field: str
    optional_field: Optional[str] = None

class Response(BaseModel):
    """Response schema"""
    id: str
    field: str
    created_at: str
```

## Testing Guidelines

### Writing Tests

When adding tests (test suite to be implemented):

1. **Test Services**: Test business logic independently
2. **Test Routers**: Test HTTP layer with mocked services
3. **Test Schemas**: Test validation logic
4. **Test Error Cases**: Test error handling paths

### Test Structure

```python
# tests/services/test_example_service.py
import pytest
from services.example_service import ExampleService

class TestExampleService:
    @pytest.mark.asyncio
    async def test_create_example_success(self):
        # Test successful creation
        pass
    
    @pytest.mark.asyncio
    async def test_create_example_invalid_data(self):
        # Test error handling
        pass
```

## Pull Request Process

### Before Submitting

- [ ] Code follows all design patterns
- [ ] All functions have docstrings
- [ ] Type hints are used throughout
- [ ] Error handling follows the pattern
- [ ] No hardcoded values (use environment variables)
- [ ] Code is tested manually
- [ ] No console.log/print statements (except for error logging)
- [ ] Environment variables documented in `.env.example` if new ones added

### PR Checklist

- [ ] Clear description of changes
- [ ] Related issue referenced (if applicable)
- [ ] Code follows project patterns
- [ ] No breaking changes (or clearly documented)
- [ ] Documentation updated (if needed)
- [ ] Environment variables documented (if added)

### Review Process

1. **Automated Checks**: CI/CD will run (when implemented)
2. **Code Review**: Maintainers will review for:
   - Adherence to design patterns
   - Code quality and style
   - Security considerations
   - Performance implications
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR will be merged

## Common Mistakes to Avoid

### ❌ Anti-Patterns

1. **Putting business logic in routers**
   ```python
   # ❌ WRONG
   @router.post("/example")
   async def create_example(request: ExampleRequest):
       supabase = get_supabase_client()
       result = supabase.table("example").insert(...).execute()
       # Business logic here
       return result
   ```

2. **Using instance methods in services**
   ```python
   # ❌ WRONG
   class ExampleService:
       def create_example(self, data):
           pass
   ```

3. **Skipping schema definitions**
   ```python
   # ❌ WRONG
   @router.post("/example")
   async def create_example(data: dict):
       pass
   ```

4. **Inconsistent error handling**
   ```python
   # ❌ WRONG
   try:
       operation()
   except Exception as e:
       return {"error": str(e)}  # Should raise HTTPException
   ```

5. **Creating Supabase clients directly**
   ```python
   # ❌ WRONG
   from supabase import create_client
   client = create_client(url, key)
   ```

## Getting Help

- **Questions**: Open a discussion or ask in PR comments
- **Bugs**: Open an issue with detailed description
- **Feature Requests**: Open an issue with use case description

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Dev Impact! 🚀
