from app.models.deployment import DatabaseType, DeploymentRequest
from .postgresql_service import PostgreSQLRDSService
from .dynamodb_service import DynamoDBService


class DeploymentFactory:
    @staticmethod
    def get_service(db_type: DatabaseType):
        services = {
            DatabaseType.POSTGRESQL: PostgreSQLRDSService(),
            DatabaseType.DYNAMODB: DynamoDBService()
        }
        return services.get(db_type)

