#!/usr/bin/env python3
"""
Quick test to verify schema generation works
"""

import requests
import json

def quick_test():
    print("🔧 Quick Schema Generation Test")
    print("=" * 40)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Real Estate", "description": "Property management"})
    session_id = response.json()["session_id"]
    print(f"✅ Started: {response.json()['prompt']}")
    
    # Answer 1
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "residential"})
    print(f"✅ Answer 1: {response.json()['prompt']}")
    
    # Answer 2 - This should trigger completion
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": "i want users to find properties by bedrooms, bathrooms, location, budget"})
    
    result = response.json()
    print(f"✅ Answer 2: {result['prompt']}")
    print(f"📊 Done: {result.get('done', False)}")
    
    if result.get('done'):
        spec = result.get('partial_spec', {})
        print(f"🎉 SUCCESS! Entities: {len(spec.get('entities', []))}")
        
        # Test schema generation
        schema_response = requests.post("http://localhost:8000/api/schema/generate", json=spec)
        if schema_response.status_code == 200:
            artifacts = schema_response.json()
            print(f"✅ Schema generated! PostgreSQL: {len(artifacts.get('postgres_sql', ''))} chars")
        else:
            print(f"❌ Schema failed: {schema_response.status_code}")
    else:
        print("❌ Still not done - need to fix completion logic")

if __name__ == "__main__":
    quick_test()
