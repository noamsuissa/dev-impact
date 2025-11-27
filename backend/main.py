from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import github_auth, profile
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Dev Impact API",
    description="Backend API for Dev Impact application with GitHub OAuth",
    version="1.0.0",
)

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

