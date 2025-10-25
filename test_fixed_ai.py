#!/usr/bin/env python3
"""
Test the fixed AI agent with rental property
"""

import requests
import json

def test_fixed_ai():
    print("🏠 Testing Fixed AI Agent")
    print("=" * 40)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Rental Property Platform", "description": "A platform for matching renters with rental properties"})
    
    if response.status_code != 200:
        print(f"❌ Start error: {response.status_code}")
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
            
            for entity in spec.get('entities', []):
                print(f"\n📁 {entity.get('name', 'Unknown')}:")
                for field in entity.get('fields', []):
                    field_info = f"    - {field.get('name', 'Unknown')} ({field.get('type', 'Unknown')})"
                    if field.get('required'):
                        field_info += " [REQUIRED]"
                    if field.get('primary_key'):
                        field_info += " [PRIMARY KEY]"
                    if field.get('foreign_key'):
                        fk = field.get('foreign_key')
                        field_info += f" [FK to {fk.get('table', 'Unknown')}.{fk.get('field', 'Unknown')}]"
                    print(field_info)
            
            # Test schema generation
            print(f"\n🔧 Testing schema generation...")
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                          json=spec)
            
            if schema_response.status_code == 200:
                artifacts = schema_response.json()
                print("✅ Schema generation successful!")
                print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
                print(f"📋 JSON Schema: {len(artifacts.get('json_schema', {}))} properties")
                print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
                print(f"⚡ DynamoDB Tables: {len(artifacts.get('dynamodb_tables', []))} tables")
            else:
                print(f"❌ Schema generation failed: {schema_response.status_code}")
                print(f"Error: {schema_response.text}")
        else:
            print("❌ Still not done after 3 questions")

if __name__ == "__main__":
    test_fixed_ai()
