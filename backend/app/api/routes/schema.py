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


@router.post("/update")
async def update_schema(request: Dict[str, Any] = Body(...)):
    """Update the schema from visualization edits."""
    try:
        project_id = request.get("project_id")
        schema = request.get("schema")
        
        if not project_id or not schema:
            raise HTTPException(status_code=400, detail="Missing project_id or schema")
        
        logger.info(f"Updating schema for project {project_id}")
        
        # Generate updated artifacts from the modified schema
        try:
            ok, errors = validate_spec(schema)
            if not ok:
                logger.warning(f"Schema validation errors: {errors}")
                # Still process even with validation errors for manual edits
        except Exception as e:
            logger.warning(f"Could not validate schema: {e}")
        
        # Generate all artifacts from the updated schema
        artifacts = generate_all(schema)
        
        logger.info(f"Successfully updated schema for project {project_id}")
        
        return {
            "message": "Schema updated successfully",
            "artifacts": artifacts
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Schema update failed")
        raise HTTPException(status_code=500, detail=str(e))
