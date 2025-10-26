from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from loguru import logger
import sys
import os

# Add parent directory to path to import claude_supabase_driver
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))
from claude_supabase_driver import call_supabase_function

router = APIRouter()


class DeployRequest(BaseModel):
    sql: str  # PostgreSQL DDL statements


class DeployResponse(BaseModel):
    success: bool
    message: str
    tables_created: list[str]
    method: str
    rls_enabled: bool


@router.post("/postgres", response_model=DeployResponse)
async def deploy_postgres_to_supabase(request: DeployRequest):
    """Deploy PostgreSQL DDL to Supabase with automatic RLS enablement"""
    try:
        logger.info("Starting PostgreSQL deployment to Supabase")
        
        # Call the deployment function
        result = call_supabase_function('create_table', table_schema=request.sql)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=result.get('error', 'Deployment failed')
            )
        
        return DeployResponse(
            success=True,
            message=result.get('message', 'Deployment successful'),
            tables_created=result.get('tables_created', []),
            method=result.get('method', 'unknown'),
            rls_enabled=result.get('rls_enabled', False)
        )
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

