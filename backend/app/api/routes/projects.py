from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from loguru import logger

from app.services.ai_agent import agent_service
from app.services.schema_generator import generate_all

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
        logger.info(f"Starting new session: name='{payload.name}', description='{payload.description}'")
        out = agent_service.start_session(payload.name, payload.description)
        logger.info(f"Session started successfully: session_id='{out.get('session_id')}'")
        return out
    except Exception as e:
        logger.exception("chat_start failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new_project/next", response_model=ChatNextResponse)
async def chat_next(payload: ChatNextRequest):
    try:
        # Validate input
        session_id_str = str(payload.session_id) if payload.session_id else ""
        answer_str = str(payload.answer) if payload.answer else ""
        logger.info(f"Received chat_next request: session_id='{session_id_str}', answer_length={len(answer_str)}")
        
        if not session_id_str.strip() or not answer_str.strip():
            logger.error(f"Validation failed: session_id_empty={not session_id_str.strip()}, answer_empty={not answer_str.strip()}")
            raise HTTPException(status_code=400, detail=f"session_id and answer are required (session_id='{session_id_str}', answer='{answer_str[:50]}')")
        
        logger.info(f"Calling agent_service.next_turn with session_id='{session_id_str}', answer='{answer_str[:100]}...'")
        try:
            out = agent_service.next_turn(session_id_str, answer_str)
            logger.info(f"agent_service.next_turn succeeded")
        except ValueError as ve:
            logger.error(f"agent_service.next_turn failed with ValueError: {ve}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.exception(f"agent_service.next_turn failed: {e}")
            raise
        
        # Ensure valid response structure
        if not isinstance(out, dict):
            raise HTTPException(status_code=500, detail="Invalid response from agent service")
        
        # Ensure required fields exist
        if "prompt" not in out:
            out["prompt"] = "Please continue..."
        if "done" not in out:
            out["done"] = False
        if "partial_spec" not in out:
            out["partial_spec"] = {}
        
        return out
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("chat_next failed")
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable. Please try again.")


@router.post("/new_project/finish", response_model=ChatFinishResponse)
async def chat_finish(payload: ChatFinishRequest):
    try:
        out = agent_service.finalize(payload.session_id)
        spec = out.get("spec", {})
        
        # Try to generate all schema formats, but don't fail if it doesn't work
        try:
            generated_schemas = generate_all(spec)
            # Merge generated schemas into the spec
            final_spec = {**spec, **generated_schemas}
        except Exception as schema_error:
            logger.warning(f"Schema generation failed: {schema_error}. Returning spec without generated schemas.")
            # Return spec without generated schemas if generation fails
            final_spec = spec
        
        return {"project_id": out["project_id"], "spec": final_spec}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("chat_finish failed")
        raise HTTPException(status_code=500, detail=str(e))
