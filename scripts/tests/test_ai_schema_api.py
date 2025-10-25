#!/usr/bin/env python3
"""
Test AI Schema via API - Test the API endpoint with AI-generated schema
"""

import requests
import json
import time

def test_ai_schema_api():
    print("🌐 Testing AI Schema via API Endpoint")
    print("=" * 50)
    
    # Your exact AI-generated schema
    ai_schema = [
        {
            "TableName": "customers",
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
                "ReadCapacityUnits": 3,
                "WriteCapacityUnits": 3
            }
        },
        {
            "TableName": "inventory",
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
                "ReadCapacityUnits": 3,
                "WriteCapacityUnits": 3
            }
        }
    ]
    
    print("🤖 AI Schema to Deploy:")
    print(json.dumps(ai_schema, indent=2))
    print()
    
    # API payload
    payload = {
        "project_id": "ai_api_test_123",
        "database_type": "dynamodb",
        "database_name": "ai_api_test_db",
        "schema_data": ai_schema  # ← Direct AI output!
    }
    
    print("📡 Sending to API...")
    print(f"   Endpoint: http://localhost:8000/api/deploy/")
    print(f"   Project: {payload['project_id']}")
    print(f"   Database: {payload['database_name']}")
    print(f"   Tables: {len(ai_schema)}")
    print()
    
    try:
        response = requests.post(
            "http://localhost:8000/api/deploy/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Deployment Successful!")
            print()
            print("📊 Results:")
            print(f"   Deployment ID: {result['deployment_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Database Type: {result['database_type']}")
            print(f"   Tables Created: {len(result['connection_info']['tables'])}")
            print()
            print("📋 Created Tables:")
            for i, table in enumerate(result['connection_info']['tables'], 1):
                print(f"   {i}. {table}")
            print()
            print("🔗 Connection Info:")
            print(f"   Region: {result['connection_info']['region']}")
            print(f"   Access Key: {result['connection_info']['access_key_id']}")
            print(f"   Secret Key: {result['connection_info']['secret_access_key'][:8]}...")
            print()
            print("🎉 Your AI schema works perfectly with the API!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running!")
        print("   Run: cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_schema_api()
