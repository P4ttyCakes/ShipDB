import boto3
from typing import List
try:  # when run from backend/
    from app.core.config import settings
    from app.services.deployment.base import BaseDeploymentService
    from app.models.deployment import DeploymentRequest, DeploymentResponse
except ImportError:  # when run from repo root
    from backend.app.core.config import settings
    from backend.app.services.deployment.base import BaseDeploymentService
    from backend.app.models.deployment import DeploymentRequest, DeploymentResponse
from loguru import logger


class DynamoDBService(BaseDeploymentService):
    def __init__(self):
        self.dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def _ensure_table(self, table_def: dict, table_name: str) -> None:
        """Create the table if it doesn't already exist, then block until it's ACTIVE."""
        try:
            self.dynamodb.describe_table(TableName=table_name)
            logger.info(f"DynamoDB table already exists: {table_name}")
            return
        except self.dynamodb.exceptions.ResourceNotFoundException:
            pass

        self.dynamodb.create_table(**table_def)
        waiter = self.dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        logger.info(f"Created DynamoDB table: {table_name}")

    async def deploy(self, request: DeploymentRequest) -> DeploymentResponse:
        tables_created = []

        # Handle both formats: simplified and full DynamoDB API format
        if isinstance(request.schema_data, list):
            # Full DynamoDB API format (AI's superior format)
            logger.info(f"Processing full DynamoDB schema with {len(request.schema_data)} tables")

            for table_def in request.schema_data:
                # Update table name to include database prefix
                original_table_name = table_def['TableName']
                table_name = f"{request.database_name}_{original_table_name}"
                table_def['TableName'] = table_name

                # Add project tags
                if 'Tags' not in table_def:
                    table_def['Tags'] = []
                table_def['Tags'].extend([
                    {'Key': 'Project', 'Value': request.project_id},
                    {'Key': 'ManagedBy', 'Value': 'ShipDB'},
                    {'Key': 'OriginalName', 'Value': original_table_name}
                ])

                try:
                    self._ensure_table(table_def, table_name)
                    tables_created.append(table_name)
                except Exception as e:
                    logger.error(f"Error creating table {table_name}: {e}")
                    raise

        else:
            # Simplified format (backward compatibility)
            logger.info("Processing simplified schema format")

            for table_def in request.schema_data.get('tables', []):
                table_name = f"{request.database_name}_{table_def['name']}"

                # Create table with on-demand billing (simplified format)
                self._ensure_table(
                    {
                        'TableName': table_name,
                        'KeySchema': [
                            {'AttributeName': table_def['primary_key'], 'KeyType': 'HASH'}
                        ],
                        'AttributeDefinitions': [
                            {'AttributeName': table_def['primary_key'], 'AttributeType': 'S'}
                        ],
                        'BillingMode': 'PAY_PER_REQUEST',
                        'Tags': [
                            {'Key': 'Project', 'Value': request.project_id},
                            {'Key': 'ManagedBy', 'Value': 'ShipDB'}
                        ]
                    },
                    table_name,
                )

                tables_created.append(table_name)

        return DeploymentResponse(
            deployment_id=request.database_name,
            status="deployed",
            database_type="dynamodb",
            connection_info={
                "region": settings.AWS_REGION,
                "tables": tables_created
            },
            message=f"Created {len(tables_created)} DynamoDB tables"
        )

    async def teardown(self, database_name: str) -> List[str]:
        """Delete all ShipDB-managed tables belonging to this deployment."""
        prefix = f"{database_name}_"
        deleted = []
        paginator = self.dynamodb.get_paginator('list_tables')
        for page in paginator.paginate():
            for table_name in page['TableNames']:
                if not table_name.startswith(prefix):
                    continue
                arn = self.dynamodb.describe_table(TableName=table_name)['Table']['TableArn']
                tags = self.dynamodb.list_tags_of_resource(ResourceArn=arn).get('Tags', [])
                # Only delete tables ShipDB created, never a coincidentally-named table
                if not any(t['Key'] == 'ManagedBy' and t['Value'] == 'ShipDB' for t in tags):
                    logger.warning(f"Skipping {table_name}: not tagged ManagedBy=ShipDB")
                    continue
                self.dynamodb.delete_table(TableName=table_name)
                deleted.append(table_name)
                logger.info(f"Deleted DynamoDB table: {table_name}")
        return deleted

    async def validate_credentials(self) -> bool:
        try:
            self.dynamodb.list_tables()
            return True
        except Exception as e:
            logger.error(f"DynamoDB credentials validation failed: {e}")
            return False
