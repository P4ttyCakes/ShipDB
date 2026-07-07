from abc import ABC, abstractmethod
try:  # when run from backend/
    from app.models.deployment import DeploymentRequest, DeploymentResponse
except ImportError:  # when run from repo root
    from backend.app.models.deployment import DeploymentRequest, DeploymentResponse


class BaseDeploymentService(ABC):
    @abstractmethod
    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        """Deploy database infrastructure"""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate cloud provider credentials"""
        pass
