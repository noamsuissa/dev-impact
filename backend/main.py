from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import uvicorn
import re
import logging
import threading
from .middleware.traceloop import setup_traceloop
from .middleware.rate_limiter import setup_rate_limiter, handle_threading_exception

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Traceloop for LLM observability BEFORE importing routers
# This ensures LiteLLM is instrumented before it's used
setup_traceloop()

# Initialize rate limiter
limiter = setup_rate_limiter()

# Import routers AFTER middleware initialization
from .routers import (
    github_auth,
    auth,
    user,
    projects,
    portfolios,
    waitlist,
    subscription,
    webhook,
    llm,
)

# Check if we're in production (disable API docs)
is_production = os.getenv("ENVIRONMENT", "").lower() in ["production", "prod"]

app = FastAPI(
    title="Dev Impact API",
    description="Backend API for Dev Impact application with GitHub OAuth",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# Add rate limiter to app state (only if initialized successfully)
if limiter is not None:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
else:
    logger.warning("Rate limiter not initialized, rate limiting disabled")

# Configure CORS
cors_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
cors_origin_regex = os.getenv("CORS_ALLOWED_ORIGIN_REGEX", "")

# Strip whitespace from each origin and filter out empty ones
cors_origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]

# Validate and log CORS configuration
if not cors_origins:
    print(
        "WARNING: No CORS origins configured! Set CORS_ALLOWED_ORIGINS environment variable."
    )
    # Default to localhost for development
    cors_origins = ["http://localhost:5173"]
elif "*" in cors_origins:
    raise RuntimeError(
        "Wildcard '*' for allowed CORS origins is not permitted. Please specify allowed origins explicitly."
    )

print(f"INFO: CORS allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=re.compile(cors_origin_regex),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(projects.router)
app.include_router(github_auth.router)
app.include_router(portfolios.router)
app.include_router(waitlist.router)
app.include_router(subscription.router)
app.include_router(webhook.router)
app.include_router(llm.router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Dev Impact API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Set up exception handler for threading
threading.excepthook = handle_threading_exception

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
