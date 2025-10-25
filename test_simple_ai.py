#!/usr/bin/env python3
"""
Simple test to see what the AI generates and fix the schema bug
"""

import requests
import json

def test_simple_ai():
    base_url = "http://localhost:8000"
    
    print("🤖 Simple AI Test")
    print("=" * 30)
    
    # Start project
    start_data = {"name": "Simple Test", "description": "A simple test project"}
    response = requests.post(f"{base_url}/api/projects/new_project/start", json=start_data)
    session_id = response.json()["session_id"]
    print(f"✅ Started session: {session_id}")
    
    # Answer questions
    answers = [
        "A blog application",
        "PostgreSQL",
        "Users, Posts, Comments. Users have id, name, email. Posts have id, title, content, author_id. Comments have id, content, post_id, author_id.",
        "Primary keys on all tables, foreign keys for relationships, index on post title."
    ]
    
    for i, answer in enumerate(answers):
        response = requests.post(f"{base_url}/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        result = response.json()
        print(f"✅ Answer {i+1}: {result['prompt'][:50]}...")
        if result['done']:
            print(f"🎉 Done! Spec keys: {list(result['partial_spec'].keys())}")
            print(f"📊 Full spec: {json.dumps(result['partial_spec'], indent=2)}")
            break
    
    # Finalize
    response = requests.post(f"{base_url}/api/projects/new_project/finish", 
                           json={"session_id": session_id})
    result = response.json()
    project_id = result["project_id"]
    spec = result["spec"]
    
    print(f"\n📋 Final Spec:")
    print(json.dumps(spec, indent=2))
    
    # Test schema generation
    print(f"\n🔧 Testing schema generation...")
    try:
        response = requests.post(f"{base_url}/api/schema/generate", json=spec)
        if response.status_code == 200:
            artifacts = response.json()
            print(f"✅ Schema generated! Keys: {list(artifacts.keys())}")
        else:
            print(f"❌ Schema generation failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_ai()
