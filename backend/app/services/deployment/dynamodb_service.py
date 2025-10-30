import boto3
import os
from backend.app.services.deployment.base import BaseDeploymentService
from backend.app.models.deployment import DeploymentRequest, DeploymentResponse
from loguru import logger


class DynamoDBService(BaseDeploymentService):
    def __init__(self):
        # Use environment variables directly
        self.dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
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
                    # Create table using full DynamoDB API parameters
                    self.dynamodb.create_table(**table_def)
                    logger.info(f"Created DynamoDB table: {table_name}")
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
                self.dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {'AttributeName': table_def['primary_key'], 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': table_def['primary_key'], 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST',
                    Tags=[
                        {'Key': 'Project', 'Value': request.project_id},
                        {'Key': 'ManagedBy', 'Value': 'ShipDB'}
                    ]
                )
                
                logger.info(f"Created DynamoDB table: {table_name}")
                tables_created.append(table_name)
        
        return DeploymentResponse(
            deployment_id=request.database_name,
            status="deployed",
            database_type="dynamodb",
            connection_info={
                "region": os.getenv('AWS_REGION', 'us-east-1'),
                "tables": tables_created,
                "access_key_id": os.getenv('AWS_ACCESS_KEY_ID'),
                "secret_access_key": os.getenv('AWS_SECRET_ACCESS_KEY')
            },
            message=f"Created {len(tables_created)} DynamoDB tables"
        )
    
    async def validate_credentials(self) -> bool:
        try:
            self.dynamodb.list_tables()
            return True
        except Exception as e:
            logger.error(f"DynamoDB credentials validation failed: {e}")
            return False
