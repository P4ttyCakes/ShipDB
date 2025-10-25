#!/usr/bin/env python3
"""
Simple API test script for ShipDB
Run this after starting the backend to verify endpoints work
"""

import requests
import json
import sys

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing ShipDB API endpoints...")
    print("=" * 40)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test project creation endpoint
    try:
        test_project = {
            "name": "Test Project",
            "description": "A test project for verification"
        }
        response = requests.post(f"{base_url}/api/projects/new", json=test_project)
        if response.status_code == 200:
            print("✅ Project creation endpoint: OK")
            project_data = response.json()
            print(f"   Created project: {project_data['name']} (ID: {project_data['project_id']})")
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Project creation error: {e}")
    
    print("\n🎉 API test complete!")
    print("\nNote: Some endpoints may require API keys to be configured.")
    print("See CONFIGURATION.md for setup instructions.")
    
    return True

if __name__ == "__main__":
    test_api()
