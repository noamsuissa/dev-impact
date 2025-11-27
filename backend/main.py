from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import github_auth, profile
from dotenv import load_dotenv
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

# Initialize rate limiter - applies to all routes globally
limiter = Limiter(key_func=get_remote_address, default_limits=os.getenv("RATE_LIMIT_DEFAULT_LIMITS", "100/minute,1000/hour").split(","))

app = FastAPI(
    title="Dev Impact API",
    description="Backend API for Dev Impact application with GitHub OAuth",
    version="1.0.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - allow all origins for development
cors_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
# Strip whitespace from each origin and filter out empty ones, and do not allow '*' in prod
cors_origins = [o.strip() for o in cors_origins_str.split(",") if o.strip()]
if "*" in cors_origins:
    raise RuntimeError("Wildcard '*' for allowed CORS origins is not permitted in production. Please specify allowed origins explicitly.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(github_auth.router)
app.include_router(profile.router)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

