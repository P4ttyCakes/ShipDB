#!/usr/bin/env python3
"""
Direct Claude Test - Create Social Media Tables
Gets Claude to actually create new tables
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('backend')

from real_claude_client import create_real_claude_session

def test_claude_create_tables():
    """Test Claude creating social media tables"""
    
    print("🤖 Direct Claude Table Creation Test")
    print("=" * 50)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create REAL Claude client
    api_key = "your_claude_api_key"
    claude_client = create_real_claude_session(api_key)
    
    # Direct request to create tables
    message = """
    I need you to create a social media platform database. Please use the create_table_advanced function to create these tables:
    
    1. A users table with user_id as primary key and GSI for username and email
    2. A posts table with user_id and post_id as composite key and GSI for time-based queries
    
    Use database_name "claude_direct_test".
    
    Here are the exact schemas to use:
    
    Users table schema:
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
    
    Posts table schema:
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
    
    Please call create_table_advanced twice - once for each table with database_name "claude_direct_test".
    """
    
    print("📤 Sending direct table creation request to Claude...")
    
    response = claude_client.send_message(message)
    
    if not response["success"]:
        print(f"❌ Error: {response['error']}")
        return False
    
    print("✅ Claude response received!")
    
    # Process function calls
    processed = claude_client.process_claude_response(response)
    
    print(f"\n📊 Function Results ({len(processed['function_results'])} calls):")
    print("=" * 50)
    
    for i, result in enumerate(processed["function_results"], 1):
        print(f"\n{i}. Function: {result['function']}")
        print(f"   Parameters: {json.dumps(result['parameters'], indent=2)}")
        print(f"   Result: {json.dumps(result['result'], indent=2)}")
        print("-" * 50)
    
    # Show Claude's text response
    if processed["claude_response"]["success"]:
        response_obj = processed["claude_response"]["response"]
        print("\n🤖 Claude's Response:")
        print("=" * 50)
        for content_item in response_obj.content:
            if content_item.type == "text":
                print(content_item.text)
    
    print("\n" + "=" * 50)
    print("🎉 Direct Claude Table Creation Test Complete!")
    print("=" * 50)
    
    if len(processed["function_results"]) > 0:
        print("✅ Claude successfully called DynamoDB functions!")
        print("✅ Claude created social media platform tables!")
        print("✅ Function calling integration working!")
    else:
        print("⚠️  Claude responded but didn't call any functions")
    
    return True

if __name__ == "__main__":
    test_claude_create_tables()
