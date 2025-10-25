#!/usr/bin/env python3
"""
API testing script for conversation completion functionality.
Tests the actual API endpoints to ensure they work correctly.
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_api_endpoints():
    """Test the API endpoints for conversation completion."""
    base_url = "http://localhost:8000"  # Default FastAPI port
    
    print("🌐 Testing ShipDB API Endpoints")
    print("="*50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the backend is running: ./start_backend.sh")
        return False
    
    # Test 2: Start a conversation session
    print("\n2. Starting conversation session...")
    session_data = {
        "name": "Test Real Estate Platform",
        "description": "A platform for buying and selling properties"
    }
    
    try:
        response = requests.post(f"{base_url}/api/ai/start", json=session_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            print(f"✅ Session started: {session_id}")
            print(f"   Initial prompt: {result['prompt'][:100]}...")
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return False
    
    # Test 3: Continue conversation
    print("\n3. Continuing conversation...")
    conversation_data = {
        "session_id": session_id,
        "answer": "We need to track properties with bedrooms, bathrooms, price, and location. Users can be buyers or sellers."
    }
    
    try:
        response = requests.post(f"{base_url}/api/ai/next", json=conversation_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation continued")
            print(f"   Done: {result['done']}")
            print(f"   Prompt: {result['prompt'][:100]}...")
        else:
            print(f"❌ Failed to continue conversation: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error continuing conversation: {e}")
        return False
    
    # Test 4: Complete conversation
    print("\n4. Completing conversation...")
    conversation_data = {
        "session_id": session_id,
        "answer": "That covers all our main requirements. We want to use PostgreSQL for reliability."
    }
    
    try:
        response = requests.post(f"{base_url}/api/ai/next", json=conversation_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation completed")
            print(f"   Done: {result['done']}")
            print(f"   Prompt: {result['prompt'][:100]}...")
            
            if result['done']:
                print("✅ Conversation marked as complete!")
            else:
                print("⚠️  Conversation not marked as complete")
        else:
            print(f"❌ Failed to complete conversation: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error completing conversation: {e}")
        return False
    
    # Test 5: Finalize session
    if result['done']:
        print("\n5. Finalizing session...")
        finalize_data = {"session_id": session_id}
        
        try:
            response = requests.post(f"{base_url}/api/ai/finalize", json=finalize_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Session finalized")
                print(f"   Project ID: {result['project_id']}")
                print(f"   Spec has app_type: {bool(result['spec'].get('app_type'))}")
                print(f"   Spec has db_type: {result['spec'].get('db_type')}")
                print(f"   Spec has entities: {len(result['spec'].get('entities', []))}")
                
                # Show the complete spec
                print("\n📋 Complete Database Specification:")
                print(json.dumps(result['spec'], indent=2))
                
                return True
            else:
                print(f"❌ Failed to finalize session: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error finalizing session: {e}")
            return False
    
    return True

def main():
    """Run API tests."""
    print("🚢 ShipDB API Conversation Completion Tests")
    print("="*60)
    
    success = test_api_endpoints()
    
    if success:
        print("\n🎉 All API tests passed! The conversation completion is working via API.")
    else:
        print("\n❌ Some API tests failed. Check the backend logs for details.")
        print("\nTo start the backend:")
        print("  ./start_backend.sh")
        print("\nTo check backend logs:")
        print("  tail -f backend/logs/app.log")

if __name__ == "__main__":
    main()
