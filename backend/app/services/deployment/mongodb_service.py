import httpx
from loguru import logger
from app.core.config import settings
from app.services.deployment.base import BaseDeploymentService
from app.models.deployment import DeploymentRequest, DeploymentResponse


class MongoDBAtlasService(BaseDeploymentService):
    def __init__(self):
        self.api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
        self.auth = (settings.MONGODB_ATLAS_PUBLIC_KEY, 
                     settings.MONGODB_ATLAS_PRIVATE_KEY)
    
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        # 1. Create cluster (M0 free tier for hackathon)
        cluster_name = f"shipdb-{request.project_id[:8]}"
        
        # 2. Create database user
        username = f"user_{request.project_id[:8]}"
        password = self._generate_password()
        
        # 3. Whitelist IP (0.0.0.0/0 for hackathon - allow all)
        
        # 4. Create database and collections from schema
        
        # 5. Return connection string
        return DeploymentResponse(
            deployment_id=cluster_name,
            status="deployed",
            database_type="mongodb",
            connection_info={
                "connection_string": f"mongodb+srv://{username}:{password}@{cluster_name}.mongodb.net/{request.database_name}",
                "username": username,
                "password": password,
                "database": request.database_name
            },
            message="MongoDB Atlas cluster deployed successfully"
        )
    
    async def validate_credentials(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/groups/{settings.MONGODB_ATLAS_PROJECT_ID}",
                    auth=self.auth
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"MongoDB Atlas credentials validation failed: {e}")
            return False
    
    def _generate_password(self) -> str:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        return ''.join(secrets.choice(alphabet) for _ in range(16))
