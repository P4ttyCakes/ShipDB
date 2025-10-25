#!/usr/bin/env python3
"""
Test the rental property use case specifically
"""

import requests
import json

def test_rental_property():
    print("🏠 Testing Rental Property Database Generation")
    print("=" * 50)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Rental Property Platform", 
                               "description": "An application that allows users to give preferences for properties and have the agent suggest rental properties that work best under the users preferences. Additionally the agent should have access to the rental property agents email address, and be able to contact the owner for further information."
                           })
    
    if response.status_code != 200:
        print(f"❌ Error starting project: {response.status_code}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project started: {session_id}")
    print(f"🤖 AI Question: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Users will be renters looking for properties. They'll input their preferences like budget, location, number of bedrooms, etc. The system will match them with available rental properties and provide contact information for property agents."
    print(f"\n👤 User Answer: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return
    
    result1 = response.json()
    print(f"\n🤖 AI Response: {result1['prompt']}")
    print(f"Done: {result1.get('done', False)}")
    
    if not result1.get('done'):
        # Answer 2
        answer2 = "Properties should have details like price, location, bedrooms, bathrooms, amenities, photos, and agent contact info. Users should be able to save favorites and track their search history."
        print(f"\n👤 User Answer: {answer2}")
        
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer2})
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return
        
        result2 = response.json()
        print(f"\n🤖 AI Response: {result2['prompt']}")
        print(f"Done: {result2.get('done', False)}")
        
        if result2.get('done'):
            spec = result2.get('partial_spec', {})
            print(f"\n🎉 Complete Database Schema Generated!")
            print(f"App Type: {spec.get('app_type', 'Not specified')}")
            print(f"Database Type: {spec.get('db_type', 'Not specified')}")
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
            print(f"\n🔧 Testing Schema Generation...")
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                          json=spec)
            
            if schema_response.status_code == 200:
                artifacts = schema_response.json()
                print("✅ Schema generation successful!")
                print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
                print(f"📋 JSON Schema: {len(artifacts.get('json_schema', {}))} properties")
            else:
                print(f"❌ Schema generation failed: {schema_response.status_code}")
                print(f"Error: {schema_response.text}")
        else:
            print("❌ AI still not generating complete spec")
    else:
        print("❌ AI marked as done too early")

if __name__ == "__main__":
    test_rental_property()
