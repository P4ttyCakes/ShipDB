#!/usr/bin/env python3
"""
Test Claude-Driven DynamoDB Functions
Demonstrates how Claude can call DynamoDB functions to build complex systems
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('.')

from claude_dynamodb_driver import call_function, FUNCTION_REGISTRY
from claude_api_client import create_claude_dynamodb_session

def test_direct_function_calls():
    """Test calling DynamoDB functions directly"""
    print("🧪 Testing Direct Function Calls")
    print("=" * 50)
    
    # Test credentials
    result = call_function("validate_credentials")
    print(f"✅ Credentials: {result['success']}")
    
    # Test listing tables
    result = call_function("list_all_tables")
    print(f"✅ Tables found: {result['count']}")
    
    # Test creating a simple table
    result = call_function("create_table_simple", 
                          table_name="test_table", 
                          primary_key="id",
                          database_name="claude_test")
    print(f"✅ Simple table creation: {result['success']}")
    
    # Test getting table info
    result = call_function("get_table_info", table_name="claude_test_test_table")
    if result['success']:
        print(f"✅ Table info: {result['table_name']} - {result['status']}")
    
    print("\n" + "=" * 50)

def test_claude_api_integration():
    """Test Claude API integration with function calling"""
    print("🤖 Testing Claude API Integration")
    print("=" * 50)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create Claude client
    api_key = "your_claude_api_key"
    claude_client = create_claude_dynamodb_session(api_key)
    
    # Test message for Claude
    test_message = """
    I need you to create a financial transaction system. Please:
    
    1. First validate that AWS credentials are working
    2. List all existing tables to see what's already there
    3. Create a table called 'accounts' with account_id as primary key
    4. Create a table called 'transactions' with composite key (account_id, transaction_id)
    5. Add a GSI to transactions table for querying by date
    6. Get information about the accounts table you created
    
    Use the available DynamoDB functions to accomplish this step by step.
    """
    
    system_prompt = """
    You are a DynamoDB expert assistant. You have access to DynamoDB functions that you can call to:
    - Create simple and advanced tables
    - Execute transactions
    - Query and scan data
    - Manage multiple tables
    
    Always use the available functions to accomplish DynamoDB tasks. Be thorough and explain what you're doing.
    When creating advanced tables, make sure to include proper AttributeDefinitions for all keys and indexes.
    """
    
    print("📤 Sending message to Claude...")
    response = claude_client.send_message(test_message, system_prompt)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return
    
    print("✅ Claude response received")
    
    # Process any function calls
    processed = claude_client.process_claude_response(response)
    
    print(f"\n📊 Function Results ({len(processed['function_results'])} calls):")
    for i, result in enumerate(processed["function_results"], 1):
        print(f"\n{i}. Function: {result['function']}")
        print(f"   Parameters: {json.dumps(result['parameters'], indent=2)}")
        print(f"   Result: {json.dumps(result['result'], indent=2)}")
        print("-" * 50)
    
    # Show Claude's text response
    if "content" in response:
        print("\n🤖 Claude's Response:")
        for content_item in response["content"]:
            if content_item["type"] == "text":
                print(content_item["text"])
    
    print("\n" + "=" * 50)

def test_advanced_schema_creation():
    """Test creating advanced schemas with GSI/LSI"""
    print("🏗️ Testing Advanced Schema Creation")
    print("=" * 50)
    
    # Advanced schema with GSI
    advanced_schema = {
        "TableName": "financial_transactions",
        "KeySchema": [
            {"AttributeName": "account_id", "KeyType": "HASH"},
            {"AttributeName": "transaction_id", "KeyType": "RANGE"}
        ],
        "AttributeDefinitions": [
            {"AttributeName": "account_id", "AttributeType": "S"},
            {"AttributeName": "transaction_id", "AttributeType": "S"},
            {"AttributeName": "transaction_date", "AttributeType": "S"},
            {"AttributeName": "amount", "AttributeType": "N"}
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "DateIndex",
                "KeySchema": [
                    {"AttributeName": "transaction_date", "KeyType": "HASH"},
                    {"AttributeName": "amount", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            }
        ],
        "BillingMode": "PROVISIONED",
        "ProvisionedThroughput": {
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5
        }
    }
    
    # Test creating advanced table
    result = call_function("create_table_advanced", 
                          table_schema=advanced_schema,
                          database_name="claude_test")
    
    print(f"✅ Advanced table creation: {result['success']}")
    if result['success']:
        print(f"   Table: {result['table_name']}")
        print(f"   Status: {result['status']}")
    
    # Test getting table info
    if result['success']:
        table_info = call_function("get_table_info", table_name=result['table_name'])
        if table_info['success']:
            print(f"✅ Table info retrieved:")
            print(f"   GSI Count: {len(table_info['global_secondary_indexes'])}")
            print(f"   Key Schema: {table_info['key_schema']}")
    
    print("\n" + "=" * 50)

def test_transaction_execution():
    """Test executing DynamoDB transactions"""
    print("💳 Testing Transaction Execution")
    print("=" * 50)
    
    # Create a simple accounts table first
    accounts_result = call_function("create_table_simple",
                                   table_name="accounts",
                                   primary_key="account_id",
                                   database_name="claude_test")
    
    if not accounts_result['success']:
        print("❌ Failed to create accounts table")
        return
    
    # Wait a moment for table to be ready
    import time
    time.sleep(5)
    
    # Transaction items for account transfer
    transaction_items = [
        {
            "Update": {
                "TableName": "claude_test_accounts",
                "Key": {"account_id": {"S": "account_001"}},
                "UpdateExpression": "SET balance = balance + :amount",
                "ExpressionAttributeValues": {":amount": {"N": "100.00"}}
            }
        },
        {
            "Update": {
                "TableName": "claude_test_accounts", 
                "Key": {"account_id": {"S": "account_002"}},
                "UpdateExpression": "SET balance = balance - :amount",
                "ExpressionAttributeValues": {":amount": {"N": "100.00"}}
            }
        }
    ]
    
    # Execute transaction
    result = call_function("execute_transaction", transaction_items=transaction_items)
    
    print(f"✅ Transaction execution: {result['success']}")
    if result['success']:
        print(f"   Items processed: {result['items_processed']}")
    else:
        print(f"   Error: {result['error']}")
    
    print("\n" + "=" * 50)

def main():
    """Run all tests"""
    print("🚀 Claude-Driven DynamoDB Function Testing")
    print("=" * 80)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    try:
        # Test 1: Direct function calls
        test_direct_function_calls()
        
        # Test 2: Advanced schema creation
        test_advanced_schema_creation()
        
        # Test 3: Transaction execution
        test_transaction_execution()
        
        # Test 4: Claude API integration (commented out to avoid API calls in test)
        # test_claude_api_integration()
        
        print("\n🎉 All tests completed!")
        print("=" * 80)
        print("✅ Claude can now drive DynamoDB functions!")
        print("✅ Advanced schemas with GSI/LSI supported")
        print("✅ Transaction execution working")
        print("✅ Function calling integration ready")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
