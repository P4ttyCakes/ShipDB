#!/usr/bin/env python3
"""
Test the complete flow with schema generation
"""

import requests
import json

def test_complete_flow_with_schema():
    print("🔄 Testing Complete Flow with Schema Generation")
    print("=" * 60)
    
    # Start a project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Property Management", 
                               "description": "Residential rental property management"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project Started")
    print(f"🤖 AI: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "real estate"
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result1.get('done', False)}")
    
    # Answer 2
    answer2 = "property management"
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result2.get('done', False)}")
    
    # Answer 3
    answer3 = "residential"
    print(f"👤 User: {answer3}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer3})
    
    result3 = response.json()
    print(f"🤖 AI: {result3.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result3.get('done', False)}")
    
    # Answer 4
    answer4 = "rental properties"
    print(f"👤 User: {answer4}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer4})
    
    result4 = response.json()
    print(f"🤖 AI: {result4.get('prompt', 'No prompt')}")
    print(f"📊 Done: {result4.get('done', False)}")
    
    # Answer 5 - Completion trigger
    answer5 = "ok create it"
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
                print(f"⚡ DynamoDB Tables: {len(artifacts.get('dynamodb_tables', []))} tables")
                
                # Show a snippet of the PostgreSQL SQL
                postgres_sql = artifacts.get('postgres_sql', '')
                if postgres_sql:
                    print(f"\n📝 PostgreSQL SQL Preview:")
                    print(postgres_sql[:300] + "..." if len(postgres_sql) > 300 else postgres_sql)
            else:
                print(f"❌ Schema generation failed: {schema_response.status_code}")
                print(f"Response: {schema_response.text}")
                
        except Exception as e:
            print(f"❌ Schema generation error: {e}")
    else:
        print("🔄 Still not complete - AI needs more information")
    
    print("\n" + "=" * 60)
    print("✅ Complete flow test finished!")
    print("🌐 Open http://localhost:8001 to test the web interface")

if __name__ == "__main__":
    test_complete_flow_with_schema()
