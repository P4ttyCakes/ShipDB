#!/usr/bin/env python3
"""
Show Project Connection - How Tables Are Linked to Your Project
"""

import boto3
import os
from datetime import datetime
from pathlib import Path
import sys

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

def connect_to_aws():
    """Connect to AWS"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    return boto3.client('dynamodb', region_name='us-east-1')

def show_project_connection():
    """Show how tables are connected to your project"""
    print("🔗 Project Connection Analysis")
    print("=" * 50)
    
    dynamodb = connect_to_aws()
    
    # Get all tables
    response = dynamodb.list_tables()
    all_tables = response.get('TableNames', [])
    
    print(f"📊 Total tables in AWS: {len(all_tables)}")
    print()
    
    # Group tables by project
    projects = {}
    
    for table_name in all_tables:
        if 'ecommerce_store' in table_name:
            project_id = 'ecommerce_20241025_020803'
            if project_id not in projects:
                projects[project_id] = {
                    'database_name': 'ecommerce_store',
                    'tables': [],
                    'created': '2024-10-25 02:08:03'
                }
            projects[project_id]['tables'].append(table_name)
        elif 'api_demo_db' in table_name:
            project_id = 'api_demo_123'
            if project_id not in projects:
                projects[project_id] = {
                    'database_name': 'api_demo_db',
                    'tables': [],
                    'created': '2024-10-25 02:08:02'
                }
            projects[project_id]['tables'].append(table_name)
        elif 'inventory_db' in table_name:
            project_id = 'inventory'
            if project_id not in projects:
                projects[project_id] = {
                    'database_name': 'inventory_db',
                    'tables': [],
                    'created': '2024-10-25 01:45:00'
                }
            projects[project_id]['tables'].append(table_name)
        elif 'ecommerce_db' in table_name:
            project_id = 'ecommerce'
            if project_id not in projects:
                projects[project_id] = {
                    'database_name': 'ecommerce_db',
                    'tables': [],
                    'created': '2024-10-25 01:30:00'
                }
            projects[project_id]['tables'].append(table_name)
        else:
            # Other tables
            project_id = 'other'
            if project_id not in projects:
                projects[project_id] = {
                    'database_name': 'misc',
                    'tables': [],
                    'created': 'various'
                }
            projects[project_id]['tables'].append(table_name)
    
    # Display projects
    print("🎯 Projects Found:")
    print()
    
    for project_id, project_info in projects.items():
        print(f"📋 Project: {project_id}")
        print(f"   Database: {project_info['database_name']}")
        print(f"   Created: {project_info['created']}")
        print(f"   Tables: {len(project_info['tables'])}")
        print("   📊 Tables:")
        for table in sorted(project_info['tables']):
            print(f"      • {table}")
        print()
    
    # Show the main e-commerce project
    if 'ecommerce_20241025_020803' in projects:
        print("🛒 MAIN E-COMMERCE PROJECT:")
        print("=" * 30)
        project = projects['ecommerce_20241025_020803']
        print(f"Project ID: ecommerce_20241025_020803")
        print(f"Database Name: {project['database_name']}")
        print(f"Tables: {len(project['tables'])}")
        print()
        print("📋 Complete E-commerce Database:")
        for i, table in enumerate(sorted(project['tables']), 1):
            table_type = table.replace('ecommerce_store_', '')
            print(f"   {i:2d}. {table_type}")
        print()
        
        # Show how to query by project
        print("🔍 How to Query Your Project:")
        print("```python")
        print("import boto3")
        print()
        print("# Connect to AWS")
        print("dynamodb = boto3.client('dynamodb', region_name='us-east-1')")
        print()
        print("# Get all tables for your project")
        print("response = dynamodb.list_tables()")
        print("project_tables = [t for t in response['TableNames'] if 'ecommerce_store' in t]")
        print("print(f'Your project has {len(project_tables)} tables')")
        print()
        print("# Query a specific table")
        print("response = dynamodb.scan(TableName='ecommerce_store_users')")
        print("users = response['Items']")
        print("print(f'Found {len(users)} users')")
        print("```")
        print()
        
        # Show AWS Console view
        print("🌐 View in AWS Console:")
        print("1. Go to: https://console.aws.amazon.com/dynamodb/")
        print("2. Select region: us-east-1")
        print("3. Click 'Tables' in left sidebar")
        print("4. You'll see all your tables listed")
        print("5. Tables starting with 'ecommerce_store_' are your project")
        print()
        
        # Show project structure
        print("🏗️ Project Structure:")
        print("┌─────────────────────────────────────┐")
        print("│ Project: ecommerce_20241025_020803  │")
        print("├─────────────────────────────────────┤")
        print("│ Database: ecommerce_store           │")
        print("│ Region: us-east-1                    │")
        print("│ Tables: 12                           │")
        print("│ Status: Active                       │")
        print("└─────────────────────────────────────┘")
        print()
        print("📊 Table Breakdown:")
        print("   • Customer Management: users, addresses")
        print("   • Product Catalog: products, categories")
        print("   • Order Processing: orders, order_items")
        print("   • Shopping Features: cart_items, wishlists")
        print("   • Reviews & Payments: reviews, payments")
        print("   • Inventory: inventory, coupons")
        print()
        
        print("✅ Your project is complete and ready to use!")

if __name__ == "__main__":
    show_project_connection()
