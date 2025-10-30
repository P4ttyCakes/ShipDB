from fastapi import APIRouter, HTTPException
from fastapi import Body
from loguru import logger
from typing import Any, Dict

from backend.app.services.schema_generator import generate_all, validate_spec, to_postgres_sql
from backend.app.services import ai_agent

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


@router.post("/suggestions")
async def get_ai_suggestions(request: Dict[str, Any] = Body(...)):
    """Get AI suggestions for improving the database schema."""
    try:
        schema = request.get("schema")
        
        if not schema:
            raise HTTPException(status_code=400, detail="Missing schema in request")
        
        # Generate PostgreSQL SQL from the schema
        postgres_sql = to_postgres_sql(schema)
        
        # Call AI agent to get suggestions
        logger.info("Generating AI suggestions for schema improvements")
        suggestions = ai_agent.agent_service.generate_schema_suggestions(postgres_sql, schema)
        
        return {
            "option_1": suggestions.get("option_1"),
            "option_2": suggestions.get("option_2")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("AI suggestions generation failed")
        raise HTTPException(status_code=500, detail=str(e))
