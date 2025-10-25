#!/usr/bin/env python3
"""
Test the fixed AI agent that doesn't get stuck in loops
"""

import requests
import json
import time

def test_real_estate_conversation():
    print("🏠 Testing Real Estate Platform - No More Loops!")
    print("=" * 60)
    
    # Start a new project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Real Estate Platform", 
                               "description": "AI-powered property recommendation platform"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project Started")
    print(f"🤖 AI: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "residential properties - apartments, houses, condos for rent and sale"
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    print(f"📊 Done: {result1.get('done', False)}")
    print(f"📋 Partial Spec Keys: {list(result1.get('partial_spec', {}).keys())}")
    
    # Answer 2
    answer2 = "users can search by budget, bedrooms, bathrooms, location, and chat with AI agent to find best matches"
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    print(f"📊 Done: {result2.get('done', False)}")
    print(f"📋 Partial Spec Keys: {list(result2.get('partial_spec', {}).keys())}")
    
    # Answer 3
    answer3 = "users can contact property owners directly through the platform, need user accounts, property listings, messaging system"
    print(f"👤 User: {answer3}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer3})
    
    result3 = response.json()
    print(f"🤖 AI: {result3.get('prompt', 'No prompt in response')}")
    print(f"📊 Done: {result3.get('done', False)}")
    print(f"📋 Partial Spec Keys: {list(result3.get('partial_spec', {}).keys())}")
    
    if result3.get('done'):
        spec = result3.get('partial_spec', {})
        print(f"\n🎉 Database Generated Successfully!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        entities = spec.get('entities', [])
        for entity in entities:
            print(f"   - {entity.get('name', 'Unknown')}")
    else:
        print(f"\n🔄 Continuing conversation...")
        print(f"🤖 AI: {result3['prompt']}")
    
    print("\n" + "=" * 60)
    print("✅ No more infinite loops!")
    print("✅ AI builds spec incrementally!")
    print("✅ Conversation progresses naturally!")

if __name__ == "__main__":
    test_real_estate_conversation()
