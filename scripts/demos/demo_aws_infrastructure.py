#!/usr/bin/env python3
"""
AWS Infrastructure Demo - See It In Action!
This script demonstrates the complete AWS infrastructure working
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

from app.services.deployment.dynamodb_service import DynamoDBService
from app.models.deployment import DeploymentRequest, DatabaseType

def print_banner():
    print("🚀" + "="*60 + "🚀")
    print("🚀" + " "*20 + "SHIPDB AWS INFRASTRUCTURE" + " "*20 + "🚀")
    print("🚀" + " "*15 + "See It In Action Demo" + " "*15 + "🚀")
    print("🚀" + "="*60 + "🚀")
    print()

def print_step(step_num, title):
    print(f"📋 Step {step_num}: {title}")
    print("-" * 50)

async def demo_aws_infrastructure():
    print_banner()
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Step 1: Show what we're building
    print_step(1, "Building an E-commerce Database")
    print("🏪 We're going to create a complete e-commerce database with:")
    print("   • Users table (customer data)")
    print("   • Products table (inventory)")
    print("   • Orders table (purchase history)")
    print("   • Categories table (product organization)")
    print()
    
    # Step 2: Show the schema
    print_step(2, "Database Schema")
    schema = {
        "tables": [
            {
                "name": "users",
                "primary_key": "user_id",
                "description": "Customer information"
            },
            {
                "name": "products", 
                "primary_key": "product_id",
                "description": "Product catalog"
            },
            {
                "name": "orders",
                "primary_key": "order_id", 
                "description": "Order history"
            },
            {
                "name": "categories",
                "primary_key": "category_id",
                "description": "Product categories"
            }
        ]
    }
    
    print("📊 Schema Definition:")
    print(json.dumps(schema, indent=2))
    print()
    
    # Step 3: Deploy the database
    print_step(3, "Deploying to AWS DynamoDB")
    print("☁️  Creating database infrastructure...")
    
    request = DeploymentRequest(
        project_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        database_type=DatabaseType.DYNAMODB,
        database_name="ecommerce_demo",
        schema_data=schema
    )
    
    try:
        result = await service.deploy(request)
        print("✅ Database deployed successfully!")
        print()
        
        # Step 4: Show the results
        print_step(4, "Deployment Results")
        print(f"🎯 Deployment ID: {result.deployment_id}")
        print(f"📊 Status: {result.status}")
        print(f"🌍 Region: {result.connection_info['region']}")
        print(f"📋 Tables Created: {len(result.connection_info['tables'])}")
        print()
        
        print("📋 Created Tables:")
        for i, table in enumerate(result.connection_info['tables'], 1):
            print(f"   {i}. {table}")
        print()
        
        # Step 5: Show connection info
        print_step(5, "Connection Information")
        print("🔗 Your database is ready! Here's how to connect:")
        print()
        print("📝 AWS Credentials:")
        print(f"   Access Key ID: {result.connection_info['access_key_id']}")
        print(f"   Secret Key: {result.connection_info['secret_access_key'][:8]}...")
        print(f"   Region: {result.connection_info['region']}")
        print()
        
        print("🐍 Python Connection Code:")
        print("```python")
        print("import boto3")
        print()
        print("# Connect to DynamoDB")
        print("dynamodb = boto3.client(")
        print("    'dynamodb',")
        print(f"    aws_access_key_id='{result.connection_info['access_key_id']}',")
        print(f"    aws_secret_access_key='{result.connection_info['secret_access_key']}',")
        print(f"    region_name='{result.connection_info['region']}'")
        print(")")
        print()
        print("# List your tables")
        print("tables = dynamodb.list_tables()")
        print("print('Your tables:', tables['TableNames'])")
        print("```")
        print()
        
        # Step 6: Verify in AWS
        print_step(6, "Verification in AWS")
        print("🔍 Let's verify the tables exist in AWS...")
        
        import boto3
        client = boto3.client('dynamodb', region_name='us-east-1')
        tables = client.list_tables()
        
        print(f"✅ Found {len(tables['TableNames'])} total tables in AWS DynamoDB")
        print("📋 All Tables:")
        for table in sorted(tables['TableNames']):
            if 'ecommerce_demo' in table:
                print(f"   🎯 {table} (Your new tables!)")
            else:
                print(f"   📊 {table}")
        print()
        
        # Step 7: Show what's next
        print_step(7, "What's Next?")
        print("🚀 Your AWS infrastructure is ready!")
        print()
        print("📋 Next Steps:")
        print("   1. Person 1 (AI Agent) can now send schemas to this system")
        print("   2. Person 3 (Frontend) can display connection info to users")
        print("   3. Users can start building their applications immediately")
        print()
        print("🔧 Integration Points:")
        print("   • API Endpoint: POST /api/deploy/")
        print("   • Input: DeploymentRequest with schema_data")
        print("   • Output: DeploymentResponse with connection_info")
        print()
        
        print("🎉 Demo Complete! AWS Infrastructure is working perfectly!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demo_aws_infrastructure())
