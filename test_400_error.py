#!/usr/bin/env python3
"""
Test to reproduce and fix the 400 error
"""

import requests
import json

def test_400_error():
    print("🔍 Testing for 400 Error")
    print("=" * 40)
    
    try:
        # Start a project
        response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                               json={
                                   "name": "Test Project", 
                                   "description": "Test description"
                               })
        
        if response.status_code != 200:
            print(f"❌ Start failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Project started: {session_id}")
        print(f"🤖 AI: {session_data['prompt']}")
        
        # Test the next endpoint
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={
                                   "session_id": session_id, 
                                   "answer": "This is a test answer"
                               })
        
        if response.status_code != 200:
            print(f"❌ Next failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        print(f"✅ Next successful")
        print(f"🤖 AI: {result['prompt']}")
        print(f"📊 Done: {result.get('done', False)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_400_error()
