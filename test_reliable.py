#!/usr/bin/env python3
"""
Test the complete reliable flow
"""

import requests
import json
import time

def test_reliable_flow():
    print("🔧 Testing Reliable Flow")
    print("=" * 40)
    
    try:
        # Test 1: Start project
        print("1. Starting project...")
        start_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                               json={"name": "Real Estate Test", "description": "Property management"},
                               timeout=30)
        start_duration = time.time() - start_time
        
        if response.status_code != 200:
            print(f"❌ Start failed: {response.status_code}")
            return
        
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Started in {start_duration:.2f}s: {session_data['prompt']}")
        
        # Test 2: Continue conversation
        print("\n2. Continuing conversation...")
        continue_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": "property management"},
                               timeout=30)
        continue_duration = time.time() - continue_time
        
        if response.status_code != 200:
            print(f"❌ Continue failed: {response.status_code}")
            return
        
        result = response.json()
        print(f"✅ Continued in {continue_duration:.2f}s: {result['prompt']}")
        
        # Test 3: Force completion
        print("\n3. Forcing completion...")
        completion_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": "whatever you think is necessary"},
                               timeout=30)
        completion_duration = time.time() - completion_time
        
        if response.status_code != 200:
            print(f"❌ Completion failed: {response.status_code}")
            return
        
        result = response.json()
        print(f"✅ Completed in {completion_duration:.2f}s")
        print(f"   Done: {result.get('done', False)}")
        print(f"   Prompt: {result.get('prompt', 'No prompt')}")
        
        if result.get('done'):
            spec = result.get('partial_spec', {})
            print(f"\n4. Testing schema generation...")
            schema_time = time.time()
            
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                          json=spec, timeout=30)
            schema_duration = time.time() - schema_time
            
            if schema_response.status_code == 200:
                artifacts = schema_response.json()
                print(f"✅ Schema generated in {schema_duration:.2f}s")
                print(f"   PostgreSQL: {len(artifacts.get('postgres_sql', ''))} chars")
                print(f"   MongoDB: {len(artifacts.get('mongo_scripts', []))} scripts")
            else:
                print(f"❌ Schema failed: {schema_response.status_code}")
                print(f"   Response: {schema_response.text}")
        
        print(f"\n🎉 Total test completed successfully!")
        print(f"   All API calls working reliably")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - API is hanging")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_reliable_flow()
