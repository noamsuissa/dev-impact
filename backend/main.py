from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import github_auth, profiles
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Dev Impact API",
    description="Backend API for Dev Impact application with GitHub OAuth",
    version="1.0.0",
)

# Configure CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(github_auth.router)
app.include_router(profiles.router)


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

