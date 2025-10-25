#!/usr/bin/env python3
"""
Debug test to see what's happening
"""

import requests
import json

def debug_test():
    print("🔍 Debug Test")
    print("=" * 20)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Debug", "description": "Debug"})
    session_id = response.json()["session_id"]
    print(f"Session: {session_id[:8]}...")
    
    # Answer 1
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "test"})
    result1 = response.json()
    print(f"Answer 1 - Done: {result1.get('done', False)}")
    print(f"Answer 1 - Prompt: {result1.get('prompt', 'No prompt')}")
    
    # Answer 2
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "test2"})
    result2 = response.json()
    print(f"Answer 2 - Done: {result2.get('done', False)}")
    print(f"Answer 2 - Prompt: {result2.get('prompt', 'No prompt')}")
    
    # Answer 3 - Should trigger forced completion
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "test3"})
    result3 = response.json()
    print(f"Answer 3 - Done: {result3.get('done', False)}")
    print(f"Answer 3 - Prompt: {result3.get('prompt', 'No prompt')}")
    
    # Check if we have entities
    spec = result3.get('partial_spec', {})
    entities = spec.get('entities', [])
    print(f"Entities: {len(entities)}")
    
    if entities:
        for entity in entities:
            print(f"  - {entity.get('name')}: {len(entity.get('fields', []))} fields")

if __name__ == "__main__":
    debug_test()