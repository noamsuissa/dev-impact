from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import github_auth, profile, auth, user, projects, user_profile, waitlist
from dotenv import load_dotenv
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn
import re
import logging
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Check if we're in production (disable API docs)
is_production = os.getenv("ENVIRONMENT", "").lower() in ["production", "prod"]

# Validate and parse rate limit configuration
def validate_rate_limit_string(rate_limit_str: str) -> list:
    """
    Validate rate limit string format and return list of limits.
    Format should be like "100/minute,1000/hour"
    """
    if not rate_limit_str:
        return ["100/minute", "1000/hour"]
    
    limits = []
    for limit in rate_limit_str.split(","):
        limit = limit.strip()
        if not limit:
            continue
        
        # Validate format: number/unit
        parts = limit.split("/")
        if len(parts) != 2:
            logger.warning(f"Invalid rate limit format: {limit}, skipping")
            continue
        
        try:
            count = int(parts[0])
            unit = parts[1].strip().lower()
            
            # Validate unit is one of the supported units
            valid_units = ["second", "minute", "hour", "day"]
            if unit not in valid_units and unit not in [u + "s" for u in valid_units]:
                logger.warning(f"Invalid rate limit unit: {unit}, skipping limit: {limit}")
                continue
            
            if count <= 0:
                logger.warning(f"Rate limit count must be positive: {count}, skipping limit: {limit}")
                continue
            
            limits.append(limit)
        except ValueError:
            logger.warning(f"Invalid rate limit count: {parts[0]}, skipping limit: {limit}")
            continue
    
    # Fallback to defaults if no valid limits found
    if not limits:
        logger.warning("No valid rate limits found, using defaults: 100/minute,1000/hour")
        return ["100/minute", "1000/hour"]
    
    return limits

# Initialize rate limiter with validation
rate_limit_str = os.getenv("RATE_LIMIT_DEFAULT_LIMITS", "100/minute,1000/hour")
validated_limits = validate_rate_limit_string(rate_limit_str)
logger.info(f"Rate limiter configured with limits: {validated_limits}")

try:
    limiter = Limiter(key_func=get_remote_address, default_limits=validated_limits)
except Exception as e:
    logger.error(f"Failed to initialize rate limiter: {e}, continuing without rate limiting")
    # Create a no-op limiter if initialization fails
    limiter = None

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
print(f"DEBUG: CORS_ALLOWED_ORIGINS env var = '{cors_origins_str}'")
print(f"DEBUG: CORS_ALLOWED_ORIGIN_REGEX env var = '{cors_origin_regex}'")

# Strip whitespace from each origin and filter out empty ones
cors_origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]

# Validate and log CORS configuration
if not cors_origins:
    print("WARNING: No CORS origins configured! Set CORS_ALLOWED_ORIGINS environment variable.")
    # Default to localhost for development
    cors_origins = ["http://localhost:5173"]
elif "*" in cors_origins:
    raise RuntimeError("Wildcard '*' for allowed CORS origins is not permitted. Please specify allowed origins explicitly.")

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
app.include_router(profile.router)
app.include_router(user_profile.router)
app.include_router(waitlist.router)


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


# Suppress threading errors from slowapi that can cause OverflowError
# This is a workaround for a known issue in slowapi where invalid timestamps
# can be passed to threading.Timer, causing OverflowError
def handle_threading_exception(args):
    """Handle exceptions in threads to prevent crashes"""
    # args is a threading.ExceptHookArgs named tuple
    exc_type = args.exc_type
    exc_value = args.exc_value
    exc_traceback = args.exc_traceback
    thread = args.thread
    
    # Only log non-OverflowError exceptions or OverflowErrors that aren't from slowapi timers
    # OverflowError from slowapi timers are expected and can be safely ignored
    if exc_type == OverflowError and "timestamp out of range" in str(exc_value):
        logger.debug(f"Ignoring slowapi threading OverflowError in thread {thread.name}: {exc_value}")
        return
    
    # Log other threading errors
    logger.error(
        f"Unhandled exception in thread {thread.name}: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback)
    )

# Set up exception handler for threading
threading.excepthook = handle_threading_exception

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)

