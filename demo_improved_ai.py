#!/usr/bin/env python3
"""
Demo the improved AI agent experience
"""

import requests
import json
import time

def demo_improved_experience():
    print("🚀 ShipDB Improved AI Experience Demo")
    print("=" * 60)
    print("This demo shows how the AI now asks business questions")
    print("instead of technical database questions!")
    print("=" * 60)
    
    # Demo: E-commerce store
    print("\n📦 DEMO: Creating an E-commerce Store Database")
    print("-" * 50)
    
    # Start project
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "My Online Store", 
                               "description": "An e-commerce platform for selling handmade crafts and art supplies"
                           })
    
    if response.status_code != 200:
        print(f"❌ Error starting project: {response.status_code}")
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project started successfully!")
    print(f"📝 Session ID: {session_id}")
    print(f"\n🤖 AI Question: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "We'll have customers who browse products, add items to cart, and make purchases. We also need to track inventory levels and manage orders."
    print(f"\n👤 User Answer: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return
    
    result1 = response.json()
    print(f"\n🤖 AI Response: {result1['prompt']}")
    
    if result1.get('done'):
        print("\n🎉 AI Generated Complete Database Schema!")
        spec = result1.get('partial_spec', {})
        print(f"\n📊 Database Type: {spec.get('db_type', 'Not specified')}")
        print(f"📋 Entities Created: {len(spec.get('entities', []))}")
        
        for entity in spec.get('entities', []):
            print(f"\n  📁 {entity.get('name', 'Unknown')}:")
            for field in entity.get('fields', []):
                field_info = f"    - {field.get('name', 'Unknown')} ({field.get('type', 'Unknown')})"
                if field.get('primary_key'):
                    field_info += " [PRIMARY KEY]"
                if field.get('foreign_key'):
                    fk = field.get('foreign_key')
                    field_info += f" [FK to {fk.get('table', 'Unknown')}.{fk.get('field', 'Unknown')}]"
                print(field_info)
        
        # Generate schemas
        print(f"\n🔧 Generating Database Schemas...")
        schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                      json=spec)
        
        if schema_response.status_code == 200:
            artifacts = schema_response.json()
            print("✅ Schemas generated successfully!")
            print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
            print(f"📋 JSON Schema: {len(artifacts.get('json_schema', {}))} properties")
            print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
            print(f"⚡ DynamoDB Tables: {len(artifacts.get('dynamodb_tables', []))} tables")
        else:
            print(f"❌ Schema generation failed: {schema_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("✅ The AI now asks business-focused questions")
    print("✅ No technical database knowledge required")
    print("✅ Complete schemas generated automatically")
    print("✅ Ready for deployment!")
    print("\n🚀 Try it yourself at: http://localhost:8001")

if __name__ == "__main__":
    demo_improved_experience()
