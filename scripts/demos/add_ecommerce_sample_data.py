#!/usr/bin/env python3
"""
E-commerce Sample Data Generator
Adds realistic sample data to your e-commerce database
"""

import boto3
import os
import json
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

def connect_to_database():
    """Connect to the e-commerce database"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    return boto3.client('dynamodb', region_name='us-east-1')

def add_sample_categories(dynamodb):
    """Add product categories"""
    print("📂 Adding product categories...")
    
    categories = [
        {"category_id": "cat_electronics", "name": "Electronics", "description": "Electronic devices and gadgets"},
        {"category_id": "cat_clothing", "name": "Clothing", "description": "Fashion and apparel"},
        {"category_id": "cat_home", "name": "Home & Garden", "description": "Home improvement and garden supplies"},
        {"category_id": "cat_sports", "name": "Sports & Outdoors", "description": "Sports equipment and outdoor gear"},
        {"category_id": "cat_books", "name": "Books", "description": "Books and educational materials"},
        {"category_id": "cat_beauty", "name": "Beauty & Health", "description": "Beauty products and health items"}
    ]
    
    for cat in categories:
        dynamodb.put_item(
            TableName='ecommerce_store_categories',
            Item={
                'category_id': {'S': cat['category_id']},
                'name': {'S': cat['name']},
                'description': {'S': cat['description']},
                'status': {'S': 'active'},
                'created_at': {'S': datetime.now().isoformat()}
            }
        )
    
    print(f"✅ Added {len(categories)} categories")

def add_sample_products(dynamodb):
    """Add sample products"""
    print("📦 Adding sample products...")
    
    products = [
        {
            "product_id": "prod_001",
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation",
            "price": 99.99,
            "category_id": "cat_electronics",
            "stock_quantity": 50,
            "brand": "TechSound",
            "rating": 4.5
        },
        {
            "product_id": "prod_002", 
            "name": "Cotton T-Shirt",
            "description": "Comfortable 100% cotton t-shirt in various colors",
            "price": 19.99,
            "category_id": "cat_clothing",
            "stock_quantity": 100,
            "brand": "ComfortWear",
            "rating": 4.2
        },
        {
            "product_id": "prod_003",
            "name": "Smart Home Speaker",
            "description": "Voice-controlled smart speaker with AI assistant",
            "price": 149.99,
            "category_id": "cat_electronics", 
            "stock_quantity": 25,
            "brand": "SmartHome",
            "rating": 4.7
        },
        {
            "product_id": "prod_004",
            "name": "Yoga Mat",
            "description": "Non-slip yoga mat for home workouts",
            "price": 29.99,
            "category_id": "cat_sports",
            "stock_quantity": 75,
            "brand": "FlexFit",
            "rating": 4.3
        },
        {
            "product_id": "prod_005",
            "name": "Programming Book",
            "description": "Complete guide to Python programming",
            "price": 49.99,
            "category_id": "cat_books",
            "stock_quantity": 30,
            "brand": "TechBooks",
            "rating": 4.8
        }
    ]
    
    for prod in products:
        dynamodb.put_item(
            TableName='ecommerce_store_products',
            Item={
                'product_id': {'S': prod['product_id']},
                'name': {'S': prod['name']},
                'description': {'S': prod['description']},
                'price': {'N': str(prod['price'])},
                'category_id': {'S': prod['category_id']},
                'stock_quantity': {'N': str(prod['stock_quantity'])},
                'brand': {'S': prod['brand']},
                'rating': {'N': str(prod['rating'])},
                'status': {'S': 'active'},
                'created_at': {'S': datetime.now().isoformat()}
            }
        )
    
    print(f"✅ Added {len(products)} products")

def add_sample_users(dynamodb):
    """Add sample customers"""
    print("👥 Adding sample customers...")
    
    users = [
        {
            "user_id": "user_001",
            "email": "john.doe@email.com",
            "name": "John Doe",
            "phone": "+1234567890",
            "status": "active"
        },
        {
            "user_id": "user_002", 
            "email": "jane.smith@email.com",
            "name": "Jane Smith",
            "phone": "+1234567891",
            "status": "active"
        },
        {
            "user_id": "user_003",
            "email": "bob.wilson@email.com", 
            "name": "Bob Wilson",
            "phone": "+1234567892",
            "status": "active"
        }
    ]
    
    for user in users:
        dynamodb.put_item(
            TableName='ecommerce_store_users',
            Item={
                'user_id': {'S': user['user_id']},
                'email': {'S': user['email']},
                'name': {'S': user['name']},
                'phone': {'S': user['phone']},
                'status': {'S': user['status']},
                'created_at': {'S': datetime.now().isoformat()}
            }
        )
    
    print(f"✅ Added {len(users)} customers")

def add_sample_orders(dynamodb):
    """Add sample orders"""
    print("📋 Adding sample orders...")
    
    orders = [
        {
            "order_id": "order_001",
            "user_id": "user_001",
            "total_amount": 119.98,
            "status": "completed",
            "shipping_address": "123 Main St, New York, NY 10001"
        },
        {
            "order_id": "order_002",
            "user_id": "user_002", 
            "total_amount": 199.98,
            "status": "shipped",
            "shipping_address": "456 Oak Ave, Los Angeles, CA 90210"
        },
        {
            "order_id": "order_003",
            "user_id": "user_003",
            "total_amount": 79.98,
            "status": "pending",
            "shipping_address": "789 Pine St, Chicago, IL 60601"
        }
    ]
    
    for order in orders:
        dynamodb.put_item(
            TableName='ecommerce_store_orders',
            Item={
                'order_id': {'S': order['order_id']},
                'user_id': {'S': order['user_id']},
                'total_amount': {'N': str(order['total_amount'])},
                'status': {'S': order['status']},
                'shipping_address': {'S': order['shipping_address']},
                'created_at': {'S': datetime.now().isoformat()}
            }
        )
    
    print(f"✅ Added {len(orders)} orders")

def add_sample_order_items(dynamodb):
    """Add sample order items"""
    print("🛒 Adding order items...")
    
    order_items = [
        {
            "order_item_id": "item_001",
            "order_id": "order_001",
            "product_id": "prod_001",
            "quantity": 1,
            "unit_price": 99.99,
            "total_price": 99.99
        },
        {
            "order_item_id": "item_002",
            "order_id": "order_001", 
            "product_id": "prod_002",
            "quantity": 1,
            "unit_price": 19.99,
            "total_price": 19.99
        },
        {
            "order_item_id": "item_003",
            "order_id": "order_002",
            "product_id": "prod_003",
            "quantity": 1,
            "unit_price": 149.99,
            "total_price": 149.99
        },
        {
            "order_item_id": "item_004",
            "order_id": "order_002",
            "product_id": "prod_004",
            "quantity": 1,
            "unit_price": 29.99,
            "total_price": 29.99
        },
        {
            "order_item_id": "item_005",
            "order_id": "order_003",
            "product_id": "prod_005",
            "quantity": 1,
            "unit_price": 49.99,
            "total_price": 49.99
        },
        {
            "order_item_id": "item_006",
            "order_id": "order_003",
            "product_id": "prod_002",
            "quantity": 1,
            "unit_price": 19.99,
            "total_price": 19.99
        }
    ]
    
    for item in order_items:
        dynamodb.put_item(
            TableName='ecommerce_store_order_items',
            Item={
                'order_item_id': {'S': item['order_item_id']},
                'order_id': {'S': item['order_id']},
                'product_id': {'S': item['product_id']},
                'quantity': {'N': str(item['quantity'])},
                'unit_price': {'N': str(item['unit_price'])},
                'total_price': {'N': str(item['total_price'])}
            }
        )
    
    print(f"✅ Added {len(order_items)} order items")

def add_sample_reviews(dynamodb):
    """Add sample product reviews"""
    print("⭐ Adding product reviews...")
    
    reviews = [
        {
            "review_id": "review_001",
            "product_id": "prod_001",
            "user_id": "user_001",
            "rating": 5,
            "comment": "Excellent sound quality! Highly recommended.",
            "status": "approved"
        },
        {
            "review_id": "review_002",
            "product_id": "prod_002", 
            "user_id": "user_002",
            "rating": 4,
            "comment": "Great quality t-shirt, very comfortable.",
            "status": "approved"
        },
        {
            "review_id": "review_003",
            "product_id": "prod_003",
            "user_id": "user_001",
            "rating": 5,
            "comment": "Amazing smart speaker! Voice recognition is perfect.",
            "status": "approved"
        }
    ]
    
    for review in reviews:
        dynamodb.put_item(
            TableName='ecommerce_store_reviews',
            Item={
                'review_id': {'S': review['review_id']},
                'product_id': {'S': review['product_id']},
                'user_id': {'S': review['user_id']},
                'rating': {'N': str(review['rating'])},
                'comment': {'S': review['comment']},
                'status': {'S': review['status']},
                'created_at': {'S': datetime.now().isoformat()}
            }
        )
    
    print(f"✅ Added {len(reviews)} reviews")

def show_sample_queries(dynamodb):
    """Show example queries"""
    print("\n🔍 Sample Database Queries:")
    print("=" * 50)
    
    # Get all products
    print("\n📦 All Products:")
    response = dynamodb.scan(TableName='ecommerce_store_products')
    for item in response['Items']:
        print(f"   • {item['name']['S']} - ${item['price']['N']}")
    
    # Get orders for a user
    print("\n📋 Orders for John Doe (user_001):")
    response = dynamodb.scan(
        TableName='ecommerce_store_orders',
        FilterExpression='user_id = :user_id',
        ExpressionAttributeValues={':user_id': {'S': 'user_001'}}
    )
    for item in response['Items']:
        print(f"   • Order {item['order_id']['S']}: ${item['total_amount']['N']} - {item['status']['S']}")
    
    # Get reviews for a product
    print("\n⭐ Reviews for Wireless Headphones:")
    response = dynamodb.scan(
        TableName='ecommerce_store_reviews',
        FilterExpression='product_id = :product_id',
        ExpressionAttributeValues={':product_id': {'S': 'prod_001'}}
    )
    for item in response['Items']:
        print(f"   • {item['rating']['N']}/5 stars: {item['comment']['S']}")

def main():
    print("🛒 E-commerce Sample Data Generator")
    print("=" * 50)
    
    # Connect to database
    dynamodb = connect_to_database()
    
    # Add sample data
    add_sample_categories(dynamodb)
    add_sample_products(dynamodb)
    add_sample_users(dynamodb)
    add_sample_orders(dynamodb)
    add_sample_order_items(dynamodb)
    add_sample_reviews(dynamodb)
    
    # Show sample queries
    show_sample_queries(dynamodb)
    
    print("\n🎉 Sample data added successfully!")
    print("\n💡 Your e-commerce database now has:")
    print("   • 6 product categories")
    print("   • 5 sample products")
    print("   • 3 customer accounts")
    print("   • 3 orders with items")
    print("   • 3 product reviews")
    print("\n🚀 Ready to build your e-commerce application!")

if __name__ == "__main__":
    main()
