from fastapi import APIRouter, HTTPException, Body
from typing import Any, Dict, Optional
from pydantic import BaseModel
from loguru import logger

from app.services.deployment.manager import deploy as deploy_manager

router = APIRouter()


class DeployRequest(BaseModel):
    db_type: str
    aws: Optional[Dict[str, Any]] = None
    artifacts: Optional[Dict[str, Any]] = None
    spec: Optional[Dict[str, Any]] = None


@router.post("/{project_id}")
async def deploy_project(project_id: str, payload: DeployRequest = Body(...)):
    """Deploy database resources to AWS for the given project.

    Supports DynamoDB now; PostgreSQL and MongoDB are stubs.
    """
    try:
        if not payload.db_type:
            raise HTTPException(status_code=422, detail="db_type is required")
        result = deploy_manager(payload.db_type, payload.model_dump())
        return {"project_id": project_id, **result}
    except HTTPException:
        raise
    except NotImplementedError as nie:
        raise HTTPException(status_code=501, detail=str(nie))
    except Exception as e:
        logger.exception("Deployment failed")
        raise HTTPException(status_code=500, detail=str(e))
