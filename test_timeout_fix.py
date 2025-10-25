#!/usr/bin/env python3
"""
Test timeout fix
"""

import requests
import time

def test_timeout_fix():
    print("🔧 Testing Timeout Fix")
    print("=" * 30)
    
    # Start project
    start_time = time.time()
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Test Fund", "description": "Investment fund"},
                           timeout=10)
    start_duration = time.time() - start_time
    print(f"✅ Start: {start_duration:.2f}s")
    
    session_id = response.json()["session_id"]
    
    # Answer 1
    answer1_time = time.time()
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "stocks"},
                           timeout=10)
    answer1_duration = time.time() - answer1_time
    print(f"✅ Answer 1: {answer1_duration:.2f}s")
    
    # Answer 2
    answer2_time = time.time()
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "individual stocks, private equity"},
                           timeout=10)
    answer2_duration = time.time() - answer2_time
    print(f"✅ Answer 2: {answer2_duration:.2f}s")
    
    # Answer 3 - Should trigger completion
    answer3_time = time.time()
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "investor details, total money, distributions"},
                           timeout=10)
    answer3_duration = time.time() - answer3_time
    print(f"✅ Answer 3: {answer3_duration:.2f}s")
    
    result = response.json()
    print(f"📊 Done: {result.get('done', False)}")
    print(f"🤖 Response: {result.get('prompt', 'No prompt')}")
    
    if result.get('done'):
        spec = result.get('partial_spec', {})
        entities = spec.get('entities', [])
        print(f"🎉 SUCCESS! Entities: {len(entities)}")
        for entity in entities:
            print(f"   - {entity.get('name')}: {len(entity.get('fields', []))} fields")
    else:
        print("❌ Still not completing")

if __name__ == "__main__":
    test_timeout_fix()
