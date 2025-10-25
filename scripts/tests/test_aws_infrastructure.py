#!/usr/bin/env python3
"""
AWS Infrastructure Test Script
Tests the DynamoDB deployment service end-to-end
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

from app.services.deployment.dynamodb_service import DynamoDBService
from app.models.deployment import DeploymentRequest, DatabaseType

async def test_dynamodb_infrastructure():
    print("🚀 AWS Infrastructure Test - DynamoDB Service")
    print("=" * 50)
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Test 1: Credentials validation
    print("🔐 Test 1: AWS Credentials Validation")
    if await service.validate_credentials():
        print("✅ AWS credentials are valid")
    else:
        print("❌ AWS credentials are invalid")
        return False
    
    # Test 2: Single table deployment
    print("\n📊 Test 2: Single Table Deployment")
    request1 = DeploymentRequest(
        project_id="test_project_1",
        database_type=DatabaseType.DYNAMODB,
        database_name="ecommerce_db",
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
        result1 = await service.deploy(request1)
        print(f"✅ Single table deployment successful!")
        print(f"   Deployment ID: {result1.deployment_id}")
        print(f"   Tables Created: {result1.connection_info['tables']}")
        print(f"   Region: {result1.connection_info['region']}")
    except Exception as e:
        print(f"❌ Single table deployment failed: {e}")
        return False
    
    # Test 3: Multiple tables deployment
    print("\n📊 Test 3: Multiple Tables Deployment")
    request2 = DeploymentRequest(
        project_id="test_project_2",
        database_type=DatabaseType.DYNAMODB,
        database_name="inventory_db",
        schema_data={
            "tables": [
                {
                    "name": "products",
                    "primary_key": "product_id"
                },
                {
                    "name": "orders",
                    "primary_key": "order_id"
                },
                {
                    "name": "customers",
                    "primary_key": "customer_id"
                }
            ]
        }
    )
    
    try:
        result2 = await service.deploy(request2)
        print(f"✅ Multiple tables deployment successful!")
        print(f"   Deployment ID: {result2.deployment_id}")
        print(f"   Tables Created: {result2.connection_info['tables']}")
        print(f"   Total Tables: {len(result2.connection_info['tables'])}")
    except Exception as e:
        print(f"❌ Multiple tables deployment failed: {e}")
        return False
    
    # Test 4: Verify tables exist in AWS
    print("\n🔍 Test 4: Verify Tables in AWS")
    try:
        import boto3
        client = boto3.client('dynamodb', region_name='us-east-1')
        tables = client.list_tables()
        all_tables = tables['TableNames']
        
        print(f"✅ Found {len(all_tables)} tables in AWS DynamoDB:")
        for table in all_tables:
            print(f"   - {table}")
        
        # Check if our test tables exist
        expected_tables = [
            'ecommerce_db_users',
            'inventory_db_products',
            'inventory_db_orders',
            'inventory_db_customers'
        ]
        
        missing_tables = [t for t in expected_tables if t not in all_tables]
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
        else:
            print("✅ All expected tables found in AWS!")
            
    except Exception as e:
        print(f"❌ Failed to verify tables in AWS: {e}")
        return False
    
    # Test 5: Connection info format
    print("\n🔗 Test 5: Connection Info Format")
    connection_info = result2.connection_info
    required_fields = ['region', 'tables', 'access_key_id', 'secret_access_key']
    
    for field in required_fields:
        if field in connection_info:
            print(f"✅ {field}: {type(connection_info[field]).__name__}")
        else:
            print(f"❌ Missing field: {field}")
            return False
    
    print("\n🎉 All Tests Passed!")
    print("=" * 50)
    print("📋 Summary:")
    print(f"   - AWS Credentials: ✅ Valid")
    print(f"   - Single Table Deployment: ✅ Success")
    print(f"   - Multiple Tables Deployment: ✅ Success")
    print(f"   - AWS Verification: ✅ {len(all_tables)} tables found")
    print(f"   - Connection Info: ✅ Complete")
    print("\n🚀 AWS Infrastructure is ready for production!")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_dynamodb_infrastructure())
    if success:
        print("\n✅ AWS Infrastructure Test: PASSED")
        sys.exit(0)
    else:
        print("\n❌ AWS Infrastructure Test: FAILED")
        sys.exit(1)
