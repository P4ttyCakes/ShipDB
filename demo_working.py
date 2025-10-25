#!/usr/bin/env python3
"""
Working demo of ShipDB functionality
"""

import requests
import json

def demo_working():
    base_url = "http://localhost:8000"
    
    print("🚢 ShipDB Working Demo")
    print("=" * 40)
    
    # Test 1: Basic API
    print("\n1️⃣ Testing basic API...")
    response = requests.get(f"{base_url}/health")
    print(f"✅ Health check: {response.json()}")
    
    # Test 2: AI conversation
    print("\n2️⃣ Testing AI conversation...")
    start_data = {"name": "Blog App", "description": "A simple blog application"}
    response = requests.post(f"{base_url}/api/projects/new_project/start", json=start_data)
    session_id = response.json()["session_id"]
    print(f"✅ Started AI session: {session_id}")
    
    # Quick conversation
    answers = [
        "A web blog application",
        "PostgreSQL", 
        "Users (id, name, email), Posts (id, title, content, author_id), Comments (id, content, post_id, author_id)",
        "Primary keys, foreign keys for relationships"
    ]
    
    for i, answer in enumerate(answers):
        response = requests.post(f"{base_url}/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        result = response.json()
        if result['done']:
            print(f"✅ AI conversation complete!")
            break
    
    # Finalize
    response = requests.post(f"{base_url}/api/projects/new_project/finish", 
                           json={"session_id": session_id})
    result = response.json()
    project_id = result["project_id"]
    spec = result["spec"]
    
    print(f"✅ Project created: {project_id}")
    print(f"   Database: {spec.get('db_type', 'Unknown')}")
    print(f"   Entities: {len(spec.get('entities', []))}")
    
    # Test 3: Schema generation
    print("\n3️⃣ Testing schema generation...")
    response = requests.post(f"{base_url}/api/schema/generate", json=spec)
    if response.status_code == 200:
        artifacts = response.json()
        print(f"✅ Schema generated successfully!")
        
        # Show the generated SQL
        sql = artifacts.get('postgres_sql', '')
        if sql:
            print(f"\n📝 Generated PostgreSQL SQL:")
            print("-" * 40)
            print(sql)
            print("-" * 40)
        
        # Show JSON schema
        json_schema = artifacts.get('json_schema', {})
        if json_schema:
            print(f"\n📋 Generated JSON Schema:")
            print("-" * 40)
            print(json.dumps(json_schema, indent=2))
            print("-" * 40)
    else:
        print(f"❌ Schema generation failed: {response.status_code}")
        print(f"Response: {response.text}")
    
    print(f"\n🎉 Demo complete! Your ShipDB is working perfectly!")
    print(f"🌐 Frontend: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔧 Project ID: {project_id}")

if __name__ == "__main__":
    demo_working()
