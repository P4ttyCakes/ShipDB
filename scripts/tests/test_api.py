#!/usr/bin/env python3
"""
Simple API Test Script
Tests the FastAPI deployment endpoint
"""

import requests
import json
import time
from pathlib import Path
import sys

# Add the app directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "backend"))

def test_api_endpoint():
    print("🌐 Testing FastAPI Deployment Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "project_id": "api_test_123",
        "database_type": "dynamodb",
        "database_name": "api_test_db",
        "schema_data": {
            "tables": [
                {
                    "name": "api_test_table",
                    "primary_key": "id"
                }
            ]
        }
    }
    
    print("📤 Sending request to API...")
    print(f"   Project ID: {test_data['project_id']}")
    print(f"   Database Type: {test_data['database_type']}")
    print(f"   Database Name: {test_data['database_name']}")
    print(f"   Tables: {len(test_data['schema_data']['tables'])}")
    
    try:
        # Send request to API
        response = requests.post(
            "http://localhost:8000/api/deploy/",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API deployment successful!")
            print(f"   Deployment ID: {result['deployment_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Database Type: {result['database_type']}")
            print(f"   Tables Created: {result['connection_info']['tables']}")
            print(f"   Region: {result['connection_info']['region']}")
            print(f"   Message: {result['message']}")
            return True
        else:
            print(f"❌ API deployment failed!")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_endpoint():
    print("\n🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    
    # Test health endpoint first
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test deployment endpoint
        deployment_ok = test_api_endpoint()
        
        if deployment_ok:
            print("\n🎉 All API Tests Passed!")
            print("✅ AWS Infrastructure API is working!")
        else:
            print("\n❌ API Tests Failed!")
    else:
        print("\n❌ Server not responding!")
    
    print("\n" + "=" * 50)
