from fastapi import APIRouter, HTTPException
from fastapi import Body
from loguru import logger
from typing import Any, Dict

from app.services.schema_generator import generate_all, validate_spec

router = APIRouter()


@router.post("/generate")
async def generate_schema(spec: Dict[str, Any] = Body(...)):
    """Generate database schema artifacts from a provided ProjectSpec-like dict."""
    try:
        ok, errors = validate_spec(spec)
        if not ok:
            raise HTTPException(status_code=422, detail={"errors": errors})
        artifacts = generate_all(spec)
        return artifacts
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Schema generation failed")
        raise HTTPException(status_code=500, detail=str(e))
