#!/usr/bin/env python3
"""
Simple test to debug the AI agent
"""

import requests
import json

def simple_test():
    print("🧪 Simple AI Test")
    print("=" * 30)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Test Rental", "description": "Rental property platform"})
    
    if response.status_code != 200:
        print(f"❌ Start error: {response.status_code}")
        print(response.text)
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✅ Started: {session_id}")
    print(f"🤖 Q1: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Renters looking for properties"
    print(f"👤 A1: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    if response.status_code != 200:
        print(f"❌ Next error: {response.status_code}")
        print(response.text)
        return
    
    result1 = response.json()
    print(f"🤖 Q2: {result1['prompt']}")
    print(f"Done: {result1.get('done', False)}")
    
    if not result1.get('done'):
        # Answer 2
        answer2 = "Properties with price, location, bedrooms, agent contact"
        print(f"👤 A2: {answer2}")
        
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer2})
        
        if response.status_code != 200:
            print(f"❌ Next error: {response.status_code}")
            print(response.text)
            return
        
        result2 = response.json()
        print(f"🤖 Q3: {result2['prompt']}")
        print(f"Done: {result2.get('done', False)}")
        
        if result2.get('done'):
            spec = result2.get('partial_spec', {})
            print(f"\n🎉 Complete spec generated!")
            print(f"App type: {spec.get('app_type', 'None')}")
            print(f"DB type: {spec.get('db_type', 'None')}")
            print(f"Entities: {len(spec.get('entities', []))}")
            
            # Test schema generation
            print(f"\n🔧 Testing schema generation...")
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                          json=spec)
            
            if schema_response.status_code == 200:
                print("✅ Schema generation successful!")
            else:
                print(f"❌ Schema generation failed: {schema_response.status_code}")
                print(f"Error: {schema_response.text}")
        else:
            print("❌ Still not done")

if __name__ == "__main__":
    simple_test()
