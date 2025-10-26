from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

try:
    from app.core.config import settings  # when run from backend/
except ImportError:  # when run from repo root
    from backend.app.core.config import settings

try:
    from app.api.routes import projects, schema, deploy, visualization
except ImportError:
    from backend.app.api.routes import projects, schema, deploy, visualization

# Initialize FastAPI app
app = FastAPI(
    title="ShipDB API",
    description="Instant Cloud Database Deployment",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(schema.router, prefix="/api/schema", tags=["schema"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["deploy"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ShipDB API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
