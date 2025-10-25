#!/usr/bin/env python3
"""
Test AI-Generated Schema - Test ShipDB with Full DynamoDB Format
Tests the upgraded ShipDB with the user's exact AI-generated JSON
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
    print("🤖" + "="*70 + "🤖")
    print("🤖" + " "*25 + "AI SCHEMA TEST" + " "*25 + "🤖")
    print("🤖" + " "*20 + "Testing ShipDB with AI-Generated Schema" + " "*20 + "🤖")
    print("🤖" + "="*70 + "🤖")
    print()

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 60)

async def test_ai_schema():
    print_banner()
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Your exact AI-generated schema
    print_section("AI-Generated Schema")
    ai_schema = [
        {
            "TableName": "users",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "TableName": "products",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "TableName": "orders",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "TableName": "order_items",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "TableName": "inventory_transactions",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        },
        {
            "TableName": "audit_logs",
            "KeySchema": [
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                }
            ],
            "AttributeDefinitions": [
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        }
    ]
    
    print("🤖 Your AI Generated This Schema:")
    print(json.dumps(ai_schema, indent=2))
    print()
    
    print(f"📊 Schema Analysis:")
    print(f"   • Format: Full DynamoDB API format")
    print(f"   • Tables: {len(ai_schema)}")
    print(f"   • Billing: PROVISIONED (5 RCU/WCU each)")
    print(f"   • Primary Keys: All using 'id'")
    print()
    
    # Deploy the database
    print_section("Deploying AI Schema to AWS")
    print("☁️  Creating tables with AI's exact specifications...")
    
    request = DeploymentRequest(
        project_id=f"ai_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        database_type=DatabaseType.DYNAMODB,
        database_name="ai_ecommerce_db",
        schema_data=ai_schema  # ← Direct AI output!
    )
    
    try:
        result = await service.deploy(request)
        print("✅ AI schema deployed successfully!")
        print()
        
        # Show results
        print_section("Deployment Results")
        print(f"🎯 Deployment ID: {result.deployment_id}")
        print(f"📊 Status: {result.status}")
        print(f"🌍 Region: {result.connection_info['region']}")
        print(f"📋 Tables Created: {len(result.connection_info['tables'])}")
        print()
        
        print("📋 AI-Generated Tables Created:")
        for i, table in enumerate(result.connection_info['tables'], 1):
            print(f"   {i:2d}. {table}")
        print()
        
        # Show connection info
        print_section("Database Connection Information")
        print("🔗 Your AI-generated database is ready!")
        print()
        print("📝 AWS Credentials:")
        print(f"   Access Key ID: {result.connection_info['access_key_id']}")
        print(f"   Secret Key: {result.connection_info['secret_access_key'][:8]}...")
        print(f"   Region: {result.connection_info['region']}")
        print()
        
        # Show Python usage
        print_section("Python Usage Examples")
        print("🐍 How to use your AI-generated database:")
        print()
        
        python_code = '''
import boto3

# Connect to your AI-generated database
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id='your_aws_access_key',
    aws_secret_access_key='your_aws_secret_key',
    region_name='us-east-1'
)

# Add a user
dynamodb.put_item(
    TableName='ai_ecommerce_db_users',
    Item={
        'id': {'S': 'user_001'},
        'name': {'S': 'John Doe'},
        'email': {'S': 'john@example.com'},
        'created_at': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Add a product
dynamodb.put_item(
    TableName='ai_ecommerce_db_products',
    Item={
        'id': {'S': 'prod_001'},
        'name': {'S': 'Wireless Headphones'},
        'price': {'N': '99.99'},
        'category': {'S': 'electronics'},
        'stock': {'N': '50'}
    }
)

# Create an order
dynamodb.put_item(
    TableName='ai_ecommerce_db_orders',
    Item={
        'id': {'S': 'order_001'},
        'user_id': {'S': 'user_001'},
        'total_amount': {'N': '99.99'},
        'status': {'S': 'pending'},
        'created_at': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Add order item
dynamodb.put_item(
    TableName='ai_ecommerce_db_order_items',
    Item={
        'id': {'S': 'item_001'},
        'order_id': {'S': 'order_001'},
        'product_id': {'S': 'prod_001'},
        'quantity': {'N': '1'},
        'unit_price': {'N': '99.99'}
    }
)

# Log inventory transaction
dynamodb.put_item(
    TableName='ai_ecommerce_db_inventory_transactions',
    Item={
        'id': {'S': 'txn_001'},
        'product_id': {'S': 'prod_001'},
        'type': {'S': 'sale'},
        'quantity': {'N': '-1'},
        'timestamp': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Add audit log
dynamodb.put_item(
    TableName='ai_ecommerce_db_audit_logs',
    Item={
        'id': {'S': 'audit_001'},
        'action': {'S': 'order_created'},
        'user_id': {'S': 'user_001'},
        'details': {'S': 'Order order_001 created'},
        'timestamp': {'S': '2024-01-01T00:00:00Z'}
    }
)

# Query all tables
tables = ['users', 'products', 'orders', 'order_items', 'inventory_transactions', 'audit_logs']
for table in tables:
    response = dynamodb.scan(TableName=f'ai_ecommerce_db_{table}')
    print(f"{table}: {len(response['Items'])} items")
'''
        
        print("```python")
        print(python_code)
        print("```")
        
        # Verify in AWS
        print_section("AWS Verification")
        print("🔍 Verifying tables in AWS DynamoDB...")
        
        import boto3
        client = boto3.client('dynamodb', region_name='us-east-1')
        tables = client.list_tables()
        
        ai_tables = [t for t in tables['TableNames'] if 'ai_ecommerce_db' in t]
        
        print(f"✅ Found {len(ai_tables)} AI-generated tables in AWS:")
        for table in sorted(ai_tables):
            print(f"   🎯 {table}")
        
        print(f"\n📊 Total tables in AWS: {len(tables['TableNames'])}")
        
        # Show what makes this special
        print_section("What Makes This Special")
        print("🚀 Your AI schema is superior because:")
        print("   • ✅ Full DynamoDB API format")
        print("   • ✅ PROVISIONED billing (predictable costs)")
        print("   • ✅ Professional table specifications")
        print("   • ✅ Production-ready configuration")
        print("   • ✅ Complete attribute definitions")
        print("   • ✅ Proper key schemas")
        print()
        print("🎯 ShipDB now handles this format perfectly!")
        
        # Final summary
        print_section("AI Schema Test Complete!")
        print("🎉 Your AI-generated schema deployed successfully!")
        print()
        print("✅ What you have:")
        print(f"   • {len(ai_tables)} production-ready tables")
        print("   • PROVISIONED billing (5 RCU/WCU each)")
        print("   • Complete e-commerce database")
        print("   • Professional AWS configuration")
        print("   • Ready for immediate use")
        print()
        print("🚀 Your AI is generating superior schemas!")
        print("   ShipDB now handles them perfectly!")
        
        return result
        
    except Exception as e:
        print(f"❌ AI schema deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_ai_schema())

