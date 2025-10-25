#!/usr/bin/env python3
"""
Claude DynamoDB Driver Demo
Shows how Claude can call DynamoDB functions to build complex systems
"""

import os
import json
from claude_dynamodb_driver import call_function

def demo_claude_driven_dynamodb():
    """Demonstrate how Claude can drive DynamoDB operations"""
    
    print("🤖 Claude-Driven DynamoDB Demo")
    print("=" * 60)
    print("This demonstrates how Claude can call DynamoDB functions")
    print("to build complex financial and analytics systems.")
    print("=" * 60)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    print("\n🔐 Step 1: Validate AWS Credentials")
    print("-" * 40)
    result = call_function("validate_credentials")
    print(f"✅ Credentials valid: {result['success']}")
    
    print("\n📊 Step 2: List Existing Tables")
    print("-" * 40)
    result = call_function("list_all_tables")
    print(f"✅ Found {result['count']} tables")
    
    print("\n🏗️ Step 3: Create Financial System Tables")
    print("-" * 40)
    
    # Claude would generate these schemas based on requirements
    financial_schemas = [
        {
            "TableName": "accounts",
            "KeySchema": [{"AttributeName": "account_id", "KeyType": "HASH"}],
            "AttributeDefinitions": [{"AttributeName": "account_id", "AttributeType": "S"}],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        },
        {
            "TableName": "transactions",
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
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
                }
            ],
            "BillingMode": "PROVISIONED",
            "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        }
    ]
    
    # Claude calls create_multiple_tables function
    result = call_function("create_multiple_tables", 
                         schemas=financial_schemas, 
                         database_name="claude_financial")
    
    print(f"✅ Created {len(result['successful_tables'])}/{result['total_tables']} tables")
    for table in result['successful_tables']:
        print(f"   📋 {table}")
    
    print("\n💳 Step 4: Execute Financial Transaction")
    print("-" * 40)
    
    # Wait for tables to be ready
    import time
    time.sleep(10)
    
    # Claude generates transaction for account transfer
    transaction_items = [
        {
            "Put": {
                "TableName": "claude_financial_accounts",
                "Item": {
                    "account_id": {"S": "account_001"},
                    "balance": {"N": "1000.00"},
                    "account_type": {"S": "checking"},
                    "created_at": {"S": "2024-01-01T00:00:00Z"}
                }
            }
        },
        {
            "Put": {
                "TableName": "claude_financial_accounts",
                "Item": {
                    "account_id": {"S": "account_002"},
                    "balance": {"N": "500.00"},
                    "account_type": {"S": "savings"},
                    "created_at": {"S": "2024-01-01T00:00:00Z"}
                }
            }
        },
        {
            "Put": {
                "TableName": "claude_financial_transactions",
                "Item": {
                    "account_id": {"S": "account_001"},
                    "transaction_id": {"S": "txn_001"},
                    "amount": {"N": "100.00"},
                    "transaction_type": {"S": "transfer"},
                    "transaction_date": {"S": "2024-01-01"},
                    "description": {"S": "Transfer to account_002"}
                }
            }
        }
    ]
    
    # Claude calls execute_transaction function
    result = call_function("execute_transaction", transaction_items=transaction_items)
    print(f"✅ Transaction executed: {result['success']}")
    if result['success']:
        print(f"   📊 Items processed: {result['items_processed']}")
    
    print("\n📈 Step 5: Analytics Query")
    print("-" * 40)
    
    # Claude generates analytics query
    query_result = call_function("query_table",
                                table_name="claude_financial_transactions",
                                key_condition_expression="account_id = :account_id",
                                expression_attribute_values={":account_id": {"S": "account_001"}})
    
    print(f"✅ Query executed: {query_result['success']}")
    if query_result['success']:
        print(f"   📊 Items found: {query_result['count']}")
    
    print("\n🔍 Step 6: Table Information")
    print("-" * 40)
    
    # Claude gets table info to understand structure
    table_info = call_function("get_table_info", table_name="claude_financial_transactions")
    if table_info['success']:
        print(f"✅ Table: {table_info['table_name']}")
        print(f"   📊 Status: {table_info['status']}")
        print(f"   📊 GSI Count: {len(table_info['global_secondary_indexes'])}")
        print(f"   📊 Key Schema: {table_info['key_schema']}")
    
    print("\n" + "=" * 60)
    print("🎉 Claude Successfully Drove DynamoDB Operations!")
    print("=" * 60)
    print("✅ Created complex financial system")
    print("✅ Executed atomic transactions")
    print("✅ Performed analytics queries")
    print("✅ Managed table structures")
    print("=" * 60)
    
    print("\n🤖 How Claude Uses These Functions:")
    print("-" * 40)
    print("1. Claude receives requirements (e.g., 'Build a financial system')")
    print("2. Claude generates appropriate schemas with GSI/LSI")
    print("3. Claude calls create_multiple_tables() with the schemas")
    print("4. Claude generates transaction logic")
    print("5. Claude calls execute_transaction() for atomic operations")
    print("6. Claude creates analytics queries")
    print("7. Claude calls query_table() for complex searches")
    print("8. Claude manages the entire system through function calls")
    
    print("\n🚀 Available Functions for Claude:")
    print("-" * 40)
    from claude_dynamodb_driver import FUNCTION_REGISTRY
    for func_name in FUNCTION_REGISTRY.keys():
        print(f"   🔧 {func_name}")

if __name__ == "__main__":
    demo_claude_driven_dynamodb()
