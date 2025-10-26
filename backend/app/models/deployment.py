from pydantic import BaseModel
from typing import Optional, Dict, Any, Union, List
from enum import Enum


class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    DYNAMODB = "dynamodb"


class DeploymentRequest(BaseModel):
    project_id: str
    database_type: DatabaseType
    database_name: str
    schema_data: Union[Dict[str, Any], List[Dict[str, Any]]]  # Support both simplified and full DynamoDB formats
    region: Optional[str] = "us-east-1"
    

class DeploymentResponse(BaseModel):
    deployment_id: str
    status: str
    database_type: str
    connection_info: Dict[str, Any]
    message: str
