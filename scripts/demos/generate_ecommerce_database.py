#!/usr/bin/env python3
"""
E-commerce Database Generator
Creates a comprehensive e-commerce database with all necessary tables
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
    print("🛒" + "="*70 + "🛒")
    print("🛒" + " "*25 + "E-COMMERCE DATABASE GENERATOR" + " "*25 + "🛒")
    print("🛒" + " "*20 + "Complete Online Store Infrastructure" + " "*20 + "🛒")
    print("🛒" + "="*70 + "🛒")
    print()

def print_section(title):
    print(f"\n📋 {title}")
    print("-" * 60)

async def generate_ecommerce_database():
    print_banner()
    
    # Set environment variables
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    service = DynamoDBService()
    
    # Comprehensive E-commerce Schema
    print_section("E-commerce Database Schema")
    
    ecommerce_schema = {
        "tables": [
            {
                "name": "users",
                "primary_key": "user_id",
                "description": "Customer accounts and profiles"
            },
            {
                "name": "products",
                "primary_key": "product_id", 
                "description": "Product catalog and inventory"
            },
            {
                "name": "categories",
                "primary_key": "category_id",
                "description": "Product categories and subcategories"
            },
            {
                "name": "orders",
                "primary_key": "order_id",
                "description": "Customer orders and order status"
            },
            {
                "name": "order_items",
                "primary_key": "order_item_id",
                "description": "Individual items within orders"
            },
            {
                "name": "cart_items",
                "primary_key": "cart_item_id",
                "description": "Shopping cart contents"
            },
            {
                "name": "reviews",
                "primary_key": "review_id",
                "description": "Product reviews and ratings"
            },
            {
                "name": "addresses",
                "primary_key": "address_id",
                "description": "Customer shipping and billing addresses"
            },
            {
                "name": "payments",
                "primary_key": "payment_id",
                "description": "Payment transactions and methods"
            },
            {
                "name": "inventory",
                "primary_key": "inventory_id",
                "description": "Product stock levels and warehouse data"
            },
            {
                "name": "coupons",
                "primary_key": "coupon_id",
                "description": "Discount codes and promotional offers"
            },
            {
                "name": "wishlists",
                "primary_key": "wishlist_item_id",
                "description": "Customer wishlists and saved items"
            }
        ]
    }
    
    print("🏪 Complete E-commerce Database Structure:")
    print(json.dumps(ecommerce_schema, indent=2))
    
    # Deploy the database
    print_section("Deploying E-commerce Database to AWS")
    print("☁️  Creating comprehensive e-commerce infrastructure...")
    
    request = DeploymentRequest(
        project_id=f"ecommerce_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        database_type=DatabaseType.DYNAMODB,
        database_name="ecommerce_store",
        schema_data=ecommerce_schema
    )
    
    try:
        result = await service.deploy(request)
        print("✅ E-commerce database deployed successfully!")
        print()
        
        # Show results
        print_section("Deployment Results")
        print(f"🎯 Deployment ID: {result.deployment_id}")
        print(f"📊 Status: {result.status}")
        print(f"🌍 Region: {result.connection_info['region']}")
        print(f"📋 Tables Created: {len(result.connection_info['tables'])}")
        print()
        
        print("📋 E-commerce Tables Created:")
        for i, table in enumerate(result.connection_info['tables'], 1):
            print(f"   {i:2d}. {table}")
        print()
        
        # Show connection info
        print_section("Database Connection Information")
        print("🔗 Your e-commerce database is ready!")
        print()
        print("📝 AWS Credentials:")
        print(f"   Access Key ID: {result.connection_info['access_key_id']}")
        print(f"   Secret Key: {result.connection_info['secret_access_key'][:8]}...")
        print(f"   Region: {result.connection_info['region']}")
        print()
        
        # Show sample data structure
        print_section("Sample Data Structure")
        print("📊 Here's how to structure your data:")
        print()
        
        sample_data = {
            "users": {
                "user_id": "user_001",
                "email": "customer@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "active"
            },
            "products": {
                "product_id": "prod_001",
                "name": "Wireless Headphones",
                "description": "High-quality wireless headphones",
                "price": 99.99,
                "category_id": "cat_electronics",
                "stock_quantity": 50,
                "status": "active"
            },
            "orders": {
                "order_id": "order_001",
                "user_id": "user_001",
                "total_amount": 199.98,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z",
                "shipping_address_id": "addr_001"
            },
            "order_items": {
                "order_item_id": "item_001",
                "order_id": "order_001",
                "product_id": "prod_001",
                "quantity": 2,
                "unit_price": 99.99,
                "total_price": 199.98
            }
        }
        
        print("📝 Sample Data Examples:")
        for table, data in sample_data.items():
            print(f"\n🔹 {table.upper()} Table:")
            print(json.dumps(data, indent=4))
        
        # Show Python usage
        print_section("Python Usage Examples")
        print("🐍 How to use your e-commerce database:")
        print()
        
        python_code = '''
import boto3
import json

# Connect to your e-commerce database
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id='your_aws_access_key',
    aws_secret_access_key='your_aws_secret_key',
    region_name='us-east-1'
)

# Add a new customer
def add_customer(user_id, email, name):
    dynamodb.put_item(
        TableName='ecommerce_store_users',
        Item={
            'user_id': {'S': user_id},
            'email': {'S': email},
            'name': {'S': name},
            'status': {'S': 'active'},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Add a product
def add_product(product_id, name, price, category):
    dynamodb.put_item(
        TableName='ecommerce_store_products',
        Item={
            'product_id': {'S': product_id},
            'name': {'S': name},
            'price': {'N': str(price)},
            'category_id': {'S': category},
            'stock_quantity': {'N': '100'},
            'status': {'S': 'active'}
        }
    )

# Create an order
def create_order(order_id, user_id, total_amount):
    dynamodb.put_item(
        TableName='ecommerce_store_orders',
        Item={
            'order_id': {'S': order_id},
            'user_id': {'S': user_id},
            'total_amount': {'N': str(total_amount)},
            'status': {'S': 'pending'},
            'created_at': {'S': '2024-01-01T00:00:00Z'}
        }
    )

# Query orders for a user
def get_user_orders(user_id):
    response = dynamodb.scan(
        TableName='ecommerce_store_orders',
        FilterExpression='user_id = :user_id',
        ExpressionAttributeValues={':user_id': {'S': user_id}}
    )
    return response['Items']

# Get all products
def get_all_products():
    response = dynamodb.scan(TableName='ecommerce_store_products')
    return response['Items']
'''
        
        print("```python")
        print(python_code)
        print("```")
        
        # Show business logic examples
        print_section("E-commerce Business Logic")
        print("💼 Common e-commerce operations:")
        print()
        print("🛒 Shopping Cart Operations:")
        print("   • Add items to cart")
        print("   • Update quantities")
        print("   • Remove items")
        print("   • Calculate totals")
        print()
        print("📦 Order Management:")
        print("   • Create orders from cart")
        print("   • Track order status")
        print("   • Process payments")
        print("   • Update inventory")
        print()
        print("👥 Customer Management:")
        print("   • User registration/login")
        print("   • Profile management")
        print("   • Order history")
        print("   • Wishlist management")
        print()
        print("📊 Analytics & Reporting:")
        print("   • Sales reports")
        print("   • Inventory tracking")
        print("   • Customer analytics")
        print("   • Product performance")
        
        # Verify in AWS
        print_section("AWS Verification")
        print("🔍 Verifying tables in AWS DynamoDB...")
        
        import boto3
        client = boto3.client('dynamodb', region_name='us-east-1')
        tables = client.list_tables()
        
        ecommerce_tables = [t for t in tables['TableNames'] if 'ecommerce_store' in t]
        
        print(f"✅ Found {len(ecommerce_tables)} e-commerce tables in AWS:")
        for table in sorted(ecommerce_tables):
            print(f"   🎯 {table}")
        
        print(f"\n📊 Total tables in AWS: {len(tables['TableNames'])}")
        
        # Final summary
        print_section("E-commerce Database Complete!")
        print("🎉 Your complete e-commerce database is ready!")
        print()
        print("✅ What you have:")
        print(f"   • {len(ecommerce_tables)} database tables")
        print("   • Complete customer management")
        print("   • Product catalog system")
        print("   • Order processing system")
        print("   • Shopping cart functionality")
        print("   • Payment tracking")
        print("   • Inventory management")
        print("   • Review system")
        print("   • Coupon system")
        print("   • Wishlist functionality")
        print()
        print("🚀 Ready for:")
        print("   • Online store development")
        print("   • Mobile app backend")
        print("   • API development")
        print("   • Analytics and reporting")
        print("   • Integration with payment processors")
        print()
        print("💡 Next steps:")
        print("   1. Add sample data to test your tables")
        print("   2. Build your frontend application")
        print("   3. Integrate with payment processors")
        print("   4. Add search and filtering")
        print("   5. Implement user authentication")
        
        return result
        
    except Exception as e:
        print(f"❌ E-commerce database deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(generate_ecommerce_database())
