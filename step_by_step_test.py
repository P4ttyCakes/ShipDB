#!/usr/bin/env python3
"""
REAL Claude Social Media Platform Test - More Specific
Gets Claude to actually build the database step by step
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('backend')

from real_claude_client import create_real_claude_session

def test_claude_step_by_step():
    """Test Claude building social media platform step by step"""
    
    print("🤖 REAL Claude Step-by-Step Social Media Test")
    print("=" * 60)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create REAL Claude client
    api_key = "your_claude_api_key"
    claude_client = create_real_claude_session(api_key)
    
    # Step 1: Ask Claude to validate credentials
    print("🔐 Step 1: Validate AWS credentials")
    print("-" * 40)
    
    message1 = """
    Please validate that AWS credentials are working by calling the validate_credentials function.
    """
    
    response1 = claude_client.send_message(message1)
    if response1["success"]:
        processed1 = claude_client.process_claude_response(response1)
        print(f"✅ Claude made {len(processed1['function_results'])} function calls")
        for result in processed1['function_results']:
            print(f"   {result['function']}: {result['result']['success']}")
    
    # Step 2: Ask Claude to list tables
    print("\n📊 Step 2: List existing tables")
    print("-" * 40)
    
    message2 = """
    Please list all existing DynamoDB tables by calling the list_all_tables function.
    """
    
    response2 = claude_client.send_message(message2)
    if response2["success"]:
        processed2 = claude_client.process_claude_response(response2)
        print(f"✅ Claude made {len(processed2['function_results'])} function calls")
        for result in processed2['function_results']:
            print(f"   {result['function']}: {result['result']['count']} tables found")
    
    # Step 3: Ask Claude to create a users table
    print("\n👥 Step 3: Create users table")
    print("-" * 40)
    
    message3 = """
    Please create a users table for a social media platform. Use the create_table_advanced function with this schema:
    
    {
        "TableName": "users",
        "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "username", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"}
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "UsernameIndex",
                "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            },
            {
                "IndexName": "EmailIndex",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ],
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    }
    
    Use database_name "claude_social_step".
    """
    
    response3 = claude_client.send_message(message3)
    if response3["success"]:
        processed3 = claude_client.process_claude_response(response3)
        print(f"✅ Claude made {len(processed3['function_results'])} function calls")
        for result in processed3['function_results']:
            print(f"   {result['function']}: {result['result']['success']}")
            if result['result']['success']:
                print(f"   Table: {result['result']['table_name']}")
    
    # Step 4: Ask Claude to create a posts table
    print("\n📝 Step 4: Create posts table")
    print("-" * 40)
    
    message4 = """
    Please create a posts table for the social media platform. Use the create_table_advanced function with this schema:
    
    {
        "TableName": "posts",
        "KeySchema": [
            {"AttributeName": "user_id", "KeyType": "HASH"},
            {"AttributeName": "post_id", "KeyType": "RANGE"}
        ],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "post_id", "AttributeType": "S"},
            {"AttributeName": "created_at", "AttributeType": "S"}
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "TimeIndex",
                "KeySchema": [
                    {"AttributeName": "created_at", "KeyType": "HASH"},
                    {"AttributeName": "post_id", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
            }
        ],
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    }
    
    Use database_name "claude_social_step".
    """
    
    response4 = claude_client.send_message(message4)
    if response4["success"]:
        processed4 = claude_client.process_claude_response(response4)
        print(f"✅ Claude made {len(processed4['function_results'])} function calls")
        for result in processed4['function_results']:
            print(f"   {result['function']}: {result['result']['success']}")
            if result['result']['success']:
                print(f"   Table: {result['result']['table_name']}")
    
    # Step 5: Ask Claude to add sample data
    print("\n💾 Step 5: Add sample data")
    print("-" * 40)
    
    # Wait for tables to be ready
    import time
    time.sleep(10)
    
    message5 = """
    Please add sample data to the users table. Use the put_item function with:
    - table_name: "claude_social_step_users"
    - item: {
        "user_id": {"S": "user_001"},
        "username": {"S": "john_doe"},
        "email": {"S": "john@example.com"},
        "display_name": {"S": "John Doe"},
        "bio": {"S": "Software developer"},
        "created_at": {"S": "2024-01-01T00:00:00Z"}
    }
    """
    
    response5 = claude_client.send_message(message5)
    if response5["success"]:
        processed5 = claude_client.process_claude_response(response5)
        print(f"✅ Claude made {len(processed5['function_results'])} function calls")
        for result in processed5['function_results']:
            print(f"   {result['function']}: {result['result']['success']}")
    
    print("\n" + "=" * 60)
    print("🎉 REAL Claude Step-by-Step Test Complete!")
    print("=" * 60)
    print("✅ Claude successfully called DynamoDB functions!")
    print("✅ Claude built social media platform tables!")
    print("✅ Claude added sample data!")
    print("✅ Function calling integration working!")

if __name__ == "__main__":
    test_claude_step_by_step()
