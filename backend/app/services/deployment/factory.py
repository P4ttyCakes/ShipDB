from app.models.deployment import DatabaseType, DeploymentRequest
from .postgresql_service import PostgreSQLRDSService
from .dynamodb_service import DynamoDBService
from .supabase_service import SupabaseDeploymentService


class DeploymentFactory:
    @staticmethod
    def get_service(db_type: DatabaseType):
        services = {
            DatabaseType.POSTGRESQL: PostgreSQLRDSService(),
            DatabaseType.DYNAMODB: DynamoDBService(),
            DatabaseType.SUPABASE: SupabaseDeploymentService()
        }
        return services.get(db_type)

