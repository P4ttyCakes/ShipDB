#!/usr/bin/env python3
"""
Test the fix for AI getting stuck in conversations
"""

import requests
import json

def test_real_estate_stuck_fix():
    print("🏠 Testing Real Estate - No More Getting Stuck!")
    print("=" * 60)
    
    # Start a project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Real Estate Platform", 
                               "description": "AI-powered property recommendation platform"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project Started")
    print(f"🤖 AI: {session_data['prompt']}")
    
    # Answer 1 - Comprehensive answer
    answer1 = "all of the above"
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result1.get('done', False)}")
    
    # Answer 2 - More comprehensive answer
    answer2 = "number of bedrooms and bathrooms, max budget, location, square footage, etc"
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result2.get('done', False)}")
    
    # Answer 3 - Even more comprehensive
    answer3 = "owner contact information"
    print(f"👤 User: {answer3}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer3})
    
    result3 = response.json()
    print(f"🤖 AI: {result3.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result3.get('done', False)}")
    
    # Answer 4 - Completion trigger
    answer4 = "the user should directly be able to contact the owner of the property through the agent. The agent should have access to all types of rental data, whatever you think is important for making a decision on renting/buying a house"
    print(f"👤 User: {answer4}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer4})
    
    result4 = response.json()
    print(f"🤖 AI: {result4.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result4.get('done', False)}")
    
    # Answer 5 - Final completion trigger
    answer5 = "whatever you think is necessary"
    print(f"👤 User: {answer5}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer5})
    
    result5 = response.json()
    print(f"🤖 AI: {result5.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result5.get('done', False)}")
    
    if result5.get('done'):
        spec = result5.get('partial_spec', {})
        print(f"\n🎉 Conversation Complete!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        entities = spec.get('entities', [])
        for entity in entities:
            print(f"   - {entity.get('name', 'Unknown')}: {len(entity.get('fields', []))} fields")
        
        # Test schema generation
        print("\n🔧 Testing Schema Generation...")
        try:
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                         json=spec)
            
            if schema_response.status_code == 200:
                artifacts = schema_response.json()
                print("✅ Schema generated successfully!")
                print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
                print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
            else:
                print(f"❌ Schema generation failed: {schema_response.status_code}")
                print(f"Response: {schema_response.text}")
                
        except Exception as e:
            print(f"❌ Schema generation error: {e}")
    else:
        print("🔄 Still not complete - AI needs more information")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_real_estate_stuck_fix()
