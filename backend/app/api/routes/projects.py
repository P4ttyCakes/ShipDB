from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from loguru import logger

from app.services.ai_agent import agent_service

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


# Chat endpoints (Gemini agent)
class ChatStartRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ChatStartResponse(BaseModel):
    session_id: str
    prompt: str


class ChatNextRequest(BaseModel):
    session_id: str
    answer: str


class ChatNextResponse(BaseModel):
    prompt: str
    done: bool
    partial_spec: Dict[str, Any]


class ChatFinishRequest(BaseModel):
    session_id: str


class ChatFinishResponse(BaseModel):
    project_id: str
    spec: Dict[str, Any]


@router.post("/new_project/start", response_model=ChatStartResponse)
async def chat_start(payload: ChatStartRequest):
    try:
        out = agent_service.start_session(payload.name, payload.description)
        return out
    except Exception as e:
        logger.exception("chat_start failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new_project/next", response_model=ChatNextResponse)
async def chat_next(payload: ChatNextRequest):
    try:
        out = agent_service.next_turn(payload.session_id, payload.answer)
        return out
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("chat_next failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new_project/finish", response_model=ChatFinishResponse)
async def chat_finish(payload: ChatFinishRequest):
    try:
        out = agent_service.finalize(payload.session_id)
        return out
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("chat_finish failed")
        raise HTTPException(status_code=500, detail=str(e))
