import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append('.')

from app.services.deployment.dynamodb_service import DynamoDBService
from app.models.deployment import DeploymentRequest, DatabaseType

async def test_dynamodb():
    print("🧪 Testing DynamoDB Service...")
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Test credentials
    print("🔐 Testing AWS credentials...")
    if await service.validate_credentials():
        print("✅ AWS credentials valid")
    else:
        print("❌ AWS credentials invalid")
        return
    
    # Test deployment with mock schema
    print("🚀 Testing DynamoDB table creation...")
    request = DeploymentRequest(
        project_id="test123",
        database_type=DatabaseType.DYNAMODB,
        database_name="test_db",
        schema_data={
            "tables": [
                {
                    "name": "users",
                    "primary_key": "user_id"
                }
            ]
        }
    )
    
    try:
        result = await service.deploy(request)
        print("✅ DynamoDB deployment successful!")
        print(f"📊 Deployment ID: {result.deployment_id}")
        print(f"📊 Status: {result.status}")
        print(f"📊 Tables Created: {result.connection_info['tables']}")
        print(f"📊 Region: {result.connection_info['region']}")
        print(f"📊 Message: {result.message}")
    except Exception as e:
        print(f"❌ DynamoDB deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dynamodb())
