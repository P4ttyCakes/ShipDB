from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    status: str
    created_at: str


@router.post("/new", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new database project"""
    project_id = str(uuid.uuid4())
    
    return {
        "project_id": project_id,
        "name": project.name,
        "status": "created",
        "created_at": "2025-01-01T00:00:00Z"
    }


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    return {
        "project_id": project_id,
        "name": "My Project",
        "status": "active"
    }
