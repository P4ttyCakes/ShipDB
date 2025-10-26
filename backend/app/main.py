from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import deploy

# Initialize FastAPI app
app = FastAPI(
    title="Supabase Deployment API",
    description="Deploy PostgreSQL schemas to Supabase with automatic RLS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include deployment router
app.include_router(deploy.router, prefix="/api", tags=["deploy"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supabase Deployment API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
