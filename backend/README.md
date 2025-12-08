# Dev Impact Backend API

A FastAPI-based backend service for the Dev Impact application, providing authentication, user management, profile publishing, and project management capabilities.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Design Patterns](#design-patterns)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Development](#development)

## Overview

The Dev Impact backend is built with FastAPI and uses Supabase as the database and authentication provider. It follows a layered architecture pattern with clear separation of concerns between routing, business logic, and data access.

### Key Features

- **Authentication & Authorization**: Email/password authentication with MFA support
- **GitHub OAuth Integration**: Seamless GitHub authentication
- **User Profiles**: Multi-profile support with publishing capabilities
- **Project Management**: CRUD operations for impact projects with metrics
- **Rate Limiting**: Built-in rate limiting for API protection
- **CORS Support**: Configurable CORS for frontend integration

## Architecture

The backend follows a **3-tier layered architecture**:

```
┌─────────────────────────────────────┐
│         API Layer (Routers)        │  ← HTTP request/response handling
├─────────────────────────────────────┤
│      Business Logic (Services)      │  ← Core business logic
├─────────────────────────────────────┤
│   Data Access (Supabase Client)     │  ← Database operations
└─────────────────────────────────────┘
```

### Layer Responsibilities

1. **Routers** (`routers/`): Handle HTTP requests, validate inputs via schemas, call services, return responses
2. **Services** (`services/`): Contain business logic, orchestrate data operations, handle errors
3. **Schemas** (`schemas/`): Define request/response models using Pydantic for validation
4. **Utils** (`utils/`): Shared utilities (auth helpers, Supabase client factory)

## Design Patterns

### 1. Layered Architecture Pattern

The codebase is organized into distinct layers with clear responsibilities:

- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Dependency Direction**: Routers → Services → Utils → Supabase
- **Testability**: Each layer can be tested independently

**Example Flow:**
```
HTTP Request → Router → Service → Supabase → Database
                ↓         ↓
            Schema    Business Logic
            Validation
```

### 2. Service Pattern (Static Service Classes)

All business logic is encapsulated in service classes with static methods:

```python
class ProfileService:
    @staticmethod
    async def publish_profile(username: str, profile_id: str, user_id: str, token: str):
        # Business logic here
        pass
```

**Benefits:**
- No state management needed (stateless services)
- Easy to test (no instantiation required)
- Clear namespace for related operations
- Consistent pattern across all services

**Usage:**
```python
# In routers
result = await ProfileService.publish_profile(username, profile_id, user_id, token)
```

### 3. Repository Pattern (via Supabase Client)

Services interact with the database through a Supabase client abstraction:

```python
supabase = get_supabase_client(access_token=token)
result = supabase.table("profiles").select("*").execute()
```

**Benefits:**
- Database abstraction (can swap implementations)
- Centralized database access logic
- Consistent error handling

### 4. Schema/Model Pattern (Pydantic)

Request and response validation using Pydantic models:

```python
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: Optional[str] = None
```

**Benefits:**
- Automatic request validation
- Type safety
- Self-documenting API
- Serialization/deserialization

### 5. Dependency Injection Pattern

FastAPI's dependency injection for authentication and shared logic:

```python
@router.post("/profile")
async def create_profile(
    request: CreateProfileRequest,
    authorization: str = Depends(auth_utils.get_access_token)
):
    user_id = auth_utils.get_user_id_from_token(authorization)
    # ...
```

**Benefits:**
- Reusable authentication logic
- Clean route handlers
- Easy to test (can mock dependencies)

### 6. Error Handling Pattern

Consistent error handling using HTTPException:

```python
try:
    # Operation
    pass
except HTTPException:
    raise  # Re-raise known exceptions
except Exception as e:
    print(f"Error: {e}")
    raise HTTPException(status_code=500, detail="An unexpected error occurred")
```

**Pattern:**
- Catch and re-raise `HTTPException` (known errors)
- Catch generic `Exception` for unexpected errors
- Log errors before raising
- Return user-friendly error messages

### 7. Factory Pattern (Supabase Client)

Centralized client creation in `utils/auth_utils.py`:

```python
def get_supabase_client(access_token: Optional[str] = None) -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    client = create_client(url, key)
    if access_token:
        client.postgrest.auth(access_token)
    return client
```

**Benefits:**
- Single source of truth for client creation
- Consistent configuration
- Easy to modify client behavior globally

## Project Structure

```
backend/
├── main.py                 # FastAPI app initialization and configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
│
├── routers/               # API route handlers (API Layer)
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── github_auth.py    # GitHub OAuth endpoints
│   ├── profile.py        # Profile publishing endpoints
│   ├── projects.py       # Project CRUD endpoints
│   ├── user.py           # User management endpoints
│   └── user_profile.py   # User profile endpoints
│
├── services/              # Business logic (Service Layer)
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication business logic
│   │   └── mfa_service.py     # MFA business logic
│   ├── github_service.py      # GitHub integration logic
│   ├── profile_service.py     # Profile publishing logic
│   ├── project_service.py     # Project management logic
│   ├── user_profile_service.py # User profile logic
│   └── user_service.py        # User management logic
│
├── schemas/               # Pydantic models (Data Models)
│   ├── __init__.py
│   ├── auth.py           # Authentication schemas
│   ├── github_auth.py    # GitHub OAuth schemas
│   ├── profile.py        # Profile schemas
│   ├── project.py        # Project schemas
│   ├── user_profile.py   # User profile schemas
│   └── user.py           # User schemas
│
├── utils/                 # Shared utilities
│   ├── __init__.py
│   └── auth_utils.py     # Authentication utilities, Supabase client factory
│
└── migrations/            # Database migration scripts
    ├── 001_initial_schema.sql
    ├── 002_published_profiles.sql
    └── 003_user_profiles.sql
```

## Getting Started

### Prerequisites

- Python 3.9+
- Supabase account and project
- GitHub OAuth app (for GitHub authentication)

### Installation

1. **Clone the repository** (if not already done)

2. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

6. **Run database migrations:**
   - Open Supabase SQL Editor
   - Run migrations in order: `001_initial_schema.sql`, `002_published_profiles.sql`, `003_user_profiles.sql`

7. **Start the development server:**
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload --host 0.0.0.0 --port 3000
   ```

8. **Access API documentation:**
   - Swagger UI: http://localhost:3000/docs
   - ReDoc: http://localhost:3000/redoc

## API Documentation

### Base URL

- Development: `http://localhost:3000`
- Production: Configure via environment variables

### Authentication

Most endpoints require authentication via Bearer token:

```http
Authorization: Bearer <access_token>
```

### Main Endpoints

#### Authentication (`/api/auth`)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Sign in user
- `POST /api/auth/signout` - Sign out user
- `GET /api/auth/session` - Get current session
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/update-password` - Update password
- `POST /api/auth/mfa/enroll` - Enroll in MFA
- `POST /api/auth/mfa/verify` - Verify MFA enrollment
- `GET /api/auth/mfa/factors` - List MFA factors
- `DELETE /api/auth/mfa/factors/{factor_id}` - Remove MFA factor

#### Profiles (`/api/profiles`)
- `POST /api/profiles` - Publish/update profile
- `GET /api/profiles/check/{username}` - Check username availability
- `GET /api/profiles/{username}` - Get published profile
- `GET /api/profiles/{username}/{profile_slug}` - Get profile by slug
- `DELETE /api/profiles/{username}/{profile_slug}` - Unpublish profile
- `GET /api/profiles` - List all published profiles

#### Projects (`/api/projects`)
- `GET /api/projects` - List user's projects
- `GET /api/projects/{project_id}` - Get project by ID
- `POST /api/projects` - Create new project
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project

#### Users (`/api/users`)
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `DELETE /api/users/account` - Delete user account

### Response Format

All endpoints return JSON. Success responses follow the schema defined in `schemas/`. Error responses:

```json
{
  "detail": "Error message"
}
```

## Environment Variables

See `.env.example` for all required variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `ENVIRONMENT` | Environment name (production/prod disables docs) | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Yes |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | Yes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | Yes |
| `CORS_ALLOWED_ORIGIN_REGEX` | Regex for allowed origins | No |
| `RATE_LIMIT_DEFAULT_LIMITS` | Rate limit config (e.g., "100/minute,1000/hour") | No |
| `AUTH_REDIRECT_URL` | Redirect URL for auth flows | Yes |
| `BASE_DOMAIN` | Base domain for profile subdomains | Yes |

## Database Migrations

Migrations are SQL files in `migrations/` directory. Run them in order:

1. `001_initial_schema.sql` - Creates core tables (profiles, projects, metrics)
2. `002_published_profiles.sql` - Adds published profiles table
3. `003_user_profiles.sql` - Adds user_profiles table for multi-profile support

**To apply migrations:**
1. Open Supabase Dashboard → SQL Editor
2. Copy and paste migration SQL
3. Run the query
4. Verify tables are created

## Development

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and return types
- Document all public functions with docstrings
- Keep functions focused and single-purpose

### Adding New Features

1. **Create Schema** (`schemas/`): Define request/response models
2. **Create Service** (`services/`): Implement business logic
3. **Create Router** (`routers/`): Add API endpoints
4. **Register Router** (`main.py`): Include router in FastAPI app
5. **Add Tests**: Write tests for new functionality

### Testing

```bash
# Run tests (when test suite is added)
pytest

# Run with coverage
pytest --cov=.
```

### Debugging

- Enable debug logging by setting `ENVIRONMENT` to non-production value
- Check Supabase logs in Supabase Dashboard
- Use FastAPI's interactive docs at `/docs` for testing endpoints

### Common Tasks

**Add a new endpoint:**
1. Add route handler in appropriate router file
2. Create/use existing service method
3. Define request/response schemas
4. Add authentication if needed

**Add a new service:**
1. Create service class in `services/`
2. Add static methods for operations
3. Use `get_supabase_client()` for database access
4. Handle errors appropriately

**Add a new schema:**
1. Create Pydantic model in appropriate schema file
2. Use appropriate field types (EmailStr, etc.)
3. Add validators if needed

## Security Considerations

- **Authentication**: All protected endpoints require valid Bearer token
- **Authorization**: Services verify user ownership before operations
- **Rate Limiting**: Global rate limiting via slowapi
- **CORS**: Strict CORS configuration (no wildcards)
- **Input Validation**: Pydantic schemas validate all inputs
- **Error Messages**: Generic error messages to prevent information leakage
- **Service Role Key**: Used only server-side, never exposed to clients

## Performance

- **Database Indexing**: Key fields are indexed (username, user_id, etc.)
- **Query Optimization**: Use select() to fetch only needed fields
- **Connection Pooling**: Supabase client handles connection pooling
- **Rate Limiting**: Prevents abuse and ensures fair usage

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed contribution guidelines and how to adhere to the design patterns outlined in this document.

## License

See [LICENSE](../LICENSE) file in the root directory.
