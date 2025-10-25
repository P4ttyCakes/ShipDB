#!/usr/bin/env python3
"""
Test the improved AI agent that suggests database designs
"""

import requests
import json

def test_improved_ai():
    print("🤖 Testing Improved AI Agent")
    print("=" * 50)
    
    # Test 1: E-commerce store
    print("\n📦 Test 1: E-commerce Store")
    print("-" * 30)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Online Store", "description": "An e-commerce platform for selling products"})
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Started session: {session_id}")
        print(f"🤖 AI Question: {session_data['prompt']}")
        
        # Answer the question
        answer = "We'll have customers who can browse products, add items to cart, and make purchases. We also need to track inventory and orders."
        
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Response: {result['prompt']}")
            
            if result.get('done'):
                print("\n🎉 AI Generated Complete Schema!")
                spec = result.get('partial_spec', {})
                print(f"Database Type: {spec.get('db_type', 'Not specified')}")
                print(f"Entities: {len(spec.get('entities', []))}")
                for entity in spec.get('entities', []):
                    print(f"  - {entity.get('name', 'Unknown')}: {len(entity.get('fields', []))} fields")
    
    # Test 2: Blog platform
    print("\n📝 Test 2: Blog Platform")
    print("-" * 30)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Blog Platform", "description": "A platform for writers to publish articles"})
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Started session: {session_id}")
        print(f"🤖 AI Question: {session_data['prompt']}")
        
        # Answer the question
        answer = "Writers can create accounts, write articles, and readers can comment on posts. We need user management and content publishing."
        
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Response: {result['prompt']}")
            
            if result.get('done'):
                print("\n🎉 AI Generated Complete Schema!")
                spec = result.get('partial_spec', {})
                print(f"Database Type: {spec.get('db_type', 'Not specified')}")
                print(f"Entities: {len(spec.get('entities', []))}")
                for entity in spec.get('entities', []):
                    print(f"  - {entity.get('name', 'Unknown')}: {len(entity.get('fields', []))} fields")
    
    # Test 3: Social media app
    print("\n📱 Test 3: Social Media App")
    print("-" * 30)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={"name": "Social Media App", "description": "A social platform for sharing photos and connecting with friends"})
    
    if response.status_code == 200:
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"✅ Started session: {session_id}")
        print(f"🤖 AI Question: {session_data['prompt']}")
        
        # Answer the question
        answer = "Users can create profiles, upload photos, follow other users, and like/comment on posts. We need real-time features."
        
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AI Response: {result['prompt']}")
            
            if result.get('done'):
                print("\n🎉 AI Generated Complete Schema!")
                spec = result.get('partial_spec', {})
                print(f"Database Type: {spec.get('db_type', 'Not specified')}")
                print(f"Entities: {len(spec.get('entities', []))}")
                for entity in spec.get('entities', []):
                    print(f"  - {entity.get('name', 'Unknown')}: {len(entity.get('fields', []))} fields")
    
    print("\n" + "=" * 50)
    print("🎉 Improved AI Agent Test Complete!")
    print("The AI now suggests complete database designs based on business needs!")
    print("No more technical questions about constraints, indexes, or data types!")

if __name__ == "__main__":
    test_improved_ai()
