---
trigger: model_decision
description: This rule is applied only when working on the backend FastAPI files
---

version: 1
rules:
  - description: Global Python backend conventions
    when:
      - pattern: "backend/**"
        language: "python"
    instructions: |
      You are working in the Dev Impact FastAPI backend, which follows a strict 3-tier layered architecture:
      - API Layer: `routers/`
      - Service Layer: `services/`
      - Data Access Layer: Supabase via `utils/auth_utils.get_supabase_client`.

      General rules:
      - Follow PEP 8, use type hints everywhere, and add concise docstrings for public functions and methods.
      - Keep functions focused and single-purpose; avoid large, multi-responsibility functions.
      - Never access Supabase or environment variables directly in routers; use services and `get_supabase_client` for DB.
      - Never hardcode secrets, keys, or URLs; always read from environment variables (already wired in this project).
      - Favor composition over duplication: reuse existing services, schemas, and utilities where possible.

      Error handling:
      - For expected API errors, raise `fastapi.HTTPException` with an appropriate status code and user-safe message.
      - When catching errors in services:
        - Re-raise existing `HTTPException` without wrapping.
        - Catch generic `Exception`, log or print details, and raise `HTTPException(status_code=500, detail="An unexpected error occurred")`.
      - Do not leak internal details, stack traces, Supabase errors, or secrets in API responses.

      Security & auth:
      - Assume that protected endpoints must validate authentication using existing auth utilities and dependencies.
      - Do not expose or log Supabase service role keys, JWTs, passwords, or other sensitive data.
      - Enforce authorization in services (e.g., checking `user_id` ownership) before performing operations.

  - description: FastAPI routers (API layer)
    when:
      - pattern: "backend/routers/**.py"
        language: "python"
    instructions: |
      In `routers/`, implement only HTTP request/response concerns:
      - Define FastAPI routes with clear paths, HTTP methods, and tags.
      - Use Pydantic models from `schemas/` for request bodies and responses.
      - Use FastAPI dependency injection (`Depends`) for authentication and shared logic (e.g. `auth_utils.get_access_token`).
      - Extract the authenticated user ID and other auth info using existing auth utilities, not by parsing tokens manually.

      Responsibilities of routers:
      - Validate inputs via Pydantic models and path/query params.
      - Call the appropriate service layer method.
      - Return the service result or propagate `HTTPException`.
      - Ensure routing order does not cause route skipping

      What routers must NOT do:
      - No direct Supabase queries, raw SQL, or business rules.
      - No heavy branching or multi-step workflows; delegate to services.
      - No environment variable reads; configuration should be centralized.

      Style:
      - Keep each route handler concise and readable.
      - Group endpoints by resource (auth, profiles, projects, users, user_profile).
      - Use consistent naming and URL patterns following existing routes (e.g. `/api/profiles`, `/api/projects`).

  - description: Service layer (business logic)
    when:
      - pattern: "backend/services/**.py"
        language: "python"
    instructions: |
      In `services/`, implement the business logic as stateless service classes with `@staticmethod` methods, following the existing pattern:

      - Define one service class per domain (e.g. `ProfileService`, `ProjectService`, `UserService`, `UserProfileService`).
      - Use `@staticmethod` for all public methods; do not store instance state.
      - Obtain a Supabase client via `utils.auth_utils.get_supabase_client(access_token=...)` for all DB operations.
      - Keep all database reads/writes, cross-entity orchestration, and authorization checks in the service layer.

      Responsibilities:
      - Enforce authorization (e.g. ownership checks using `user_id`).
      - Orchestrate calls to Supabase and other services.
      - Translate lower-level errors into appropriate `HTTPException`s.
      - Select only the fields needed from Supabase for performance.

      Error handling pattern:
      - Use `try/except` around DB and external calls.
      - Re-raise existing `HTTPException` as-is.
      - For unexpected errors, log the exception (string form is fine) and raise a generic 500-level `HTTPException` with `"An unexpected error occurred"`.

      Style:
      - Return Pydantic models or plain dicts consistent with the defined schemas.
      - Avoid circular dependencies between services; factor out shared logic if needed.
      - Keep method signatures explicit and typed (including return types).

  - description: Pydantic schemas (data models)
    when:
      - pattern: "backend/schemas/**.py"
        language: "python"
    instructions: |
      In `schemas/`, define all request/response models with Pydantic:

      - Use clear, descriptive model names that match the domain (e.g. `SignUpRequest`, `CreateProfileRequest`, `PublishProfileResponse`).
      - Use appropriate field types (e.g. `EmailStr`, `Optional[...]`, `datetime`, etc.).
      - Add default values and validation constraints where relevant.
      - Keep schemas focused: do not mix request and response concerns when they differ significantly.

      Conventions:
      - Place shared or nested models close to the main model they belong to.
      - Ensure response models do not expose sensitive fields (passwords, tokens, internal IDs) unless explicitly required.
      - When updating or adding endpoints, always update or introduce schemas instead of using ad-hoc dicts.

  - description: Auth utilities and Supabase client factory
    when:
      - pattern: "backend/utils/**.py"
        language: "python"
    instructions: |
      In `utils/`, keep shared concerns like authentication helpers and the Supabase client factory:

      - Use `get_supabase_client(access_token: Optional[str] = None)` as the single source of truth for creating Supabase clients.
      - When modifying the client creation logic, maintain compatibility with existing usage (auth via `postgrest.auth(access_token)`).
      - Do not place business logic here; only shared, low-level concerns (e.g. token parsing, client creation).

      Security:
      - Read Supabase URL and keys from environment variables.
      - Ensure service role key is never exposed outside the backend and never returned in responses.

  - description: SQL migrations for backend database
    when:
      - pattern: "backend/migrations/**.sql"
        language: "sql"
    instructions: |
      In `migrations/`, write SQL that is suitable for Supabase/Postgres and follows the existing sequential pattern:

      - Do not modify existing numbered migrations (e.g. `001_initial_schema.sql`, `002_published_profiles.sql`, `003_user_profiles.sql`) after they have been applied; instead, add a new migration file with the next sequence number.
      - Ensure migrations are idempotent where reasonable (use `IF NOT EXISTS` for tables, indexes, and constraints when appropriate).
      - Name tables, columns, and indexes consistently with existing schema (e.g. profiles, projects, metrics, published_profiles, user_profiles).
      - Add indexes for frequently queried fields (e.g. `username`, `user_id`), following the existing indexing style.

      Safety and style:
      - Avoid destructive changes (dropping columns/tables) unless explicitly required and clearly commented.
      - Include brief comments at the top of the file explaining the purpose of the migration.
      - Assume migrations will be run manually in Supabase SQL Editor, in order.