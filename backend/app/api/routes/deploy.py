from fastapi import APIRouter, HTTPException
from backend.app.models.deployment import DeploymentRequest, DeploymentResponse
from backend.app.services.deployment.factory import DeploymentFactory
from backend.app.core.config import settings
from loguru import logger
import os

router = APIRouter()

@router.post("/", response_model=DeploymentResponse)
async def deploy_database(request: DeploymentRequest):
    """Deploy database to AWS cloud"""
    try:
        # Use AWS credentials from settings
        os.environ['AWS_ACCESS_KEY_ID'] = settings.AWS_ACCESS_KEY_ID or 'your_aws_access_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = settings.AWS_SECRET_ACCESS_KEY or 'your_aws_secret_key'
        os.environ['AWS_REGION'] = request.region or settings.AWS_REGION
        
        # Get appropriate deployment service
        service = DeploymentFactory.get_service(request.database_type)
        
        # Validate credentials
        if not await service.validate_credentials():
            raise HTTPException(
                status_code=400, 
                detail="Invalid cloud provider credentials"
            )
        
        # Execute deployment
        logger.info(f"Starting deployment for project {request.project_id}")
        result = await service.deploy(request)
        
        logger.success(f"Deployment completed: {result.deployment_id}")
        return result
        
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Check deployment status"""
    # Simple status check for hackathon
    return {"deployment_id": deployment_id, "status": "running"}
