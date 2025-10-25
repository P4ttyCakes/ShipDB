#!/usr/bin/env python3
"""
Test frontend integration with backend
"""

import requests
import time

def test_frontend_integration():
    print("🧪 Testing Frontend Integration")
    print("=" * 40)
    
    # Test 1: Frontend is accessible
    try:
        response = requests.get("http://localhost:8001")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False
    
    # Test 2: Backend is accessible
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    # Test 3: API endpoints work
    try:
        response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                               json={"name": "Test Project", "description": "Test"})
        if response.status_code == 200:
            print("✅ API endpoints working")
            session_id = response.json()["session_id"]
            print(f"   Session ID: {session_id}")
        else:
            print(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API error: {e}")
        return False
    
    print("\n🎉 Frontend Integration Test Complete!")
    print("=" * 40)
    print("✅ Frontend: http://localhost:8001")
    print("✅ Backend: http://localhost:8000")
    print("✅ API: Working")
    print("\n🚀 You can now use the frontend to create projects!")
    print("   1. Go to http://localhost:8001")
    print("   2. Click 'Start New Project'")
    print("   3. Fill out the form")
    print("   4. Have a conversation with the AI")
    print("   5. Get your generated schema!")
    
    return True

if __name__ == "__main__":
    test_frontend_integration()
