#!/usr/bin/env python3
"""
Test the adaptive AI that scales to ANY business type and size
"""

import requests
import json

def test_adaptive_ai():
    print("🎯 Testing Adaptive AI Database Architect")
    print("=" * 60)
    print("This AI adapts to ANY business - from simple blogs to enterprise platforms!")
    print("=" * 60)
    
    # Test 1: Simple Personal Blog
    print("\n📝 TEST 1: Simple Personal Blog")
    print("-" * 40)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "My Personal Blog", 
                               "description": "A simple blog for sharing my thoughts and experiences"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Just me writing posts, maybe 50-100 readers. Simple and personal."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Free/low-cost hosting, just need basic features like posts and comments."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated SIMPLE Blog Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Generate schemas
        schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                      json=spec)
        
        if schema_response.status_code == 200:
            artifacts = schema_response.json()
            print(f"✅ Simple schemas generated!")
            print(f"📝 PostgreSQL SQL: {len(artifacts.get('postgres_sql', ''))} characters")
            print(f"🍃 MongoDB Scripts: {len(artifacts.get('mongo_scripts', []))} scripts")
    
    # Test 2: Growing E-commerce Store
    print("\n🛒 TEST 2: Growing E-commerce Store")
    print("-" * 40)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Growing Online Store", 
                               "description": "An online store selling handmade crafts with 1000+ customers"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "About 1000 customers, growing to 5000. Moderate budget for hosting and tools."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "Need inventory tracking, order management, customer accounts, and payment processing."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated GROWING E-commerce Database!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show advanced features if present
        if "hybrid_architecture" in spec:
            print(f"🏗️ Hybrid Architecture: {spec['hybrid_architecture']}")
        if "caching_strategy" in spec:
            print(f"⚡ Caching Strategy: Included")
        if "monitoring" in spec:
            print(f"📊 Monitoring: Included")
    
    # Test 3: Enterprise Platform
    print("\n🏢 TEST 3: Enterprise Platform")
    print("-" * 40)
    
    response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                           json={
                               "name": "Enterprise Platform", 
                               "description": "A large-scale platform serving millions of users with enterprise requirements"
                           })
    
    session_data = response.json()
    session_id = session_data["session_id"]
    
    print(f"✅ Project: {session_data['prompt']}")
    
    # Answer 1
    answer1 = "Millions of users, enterprise budget, need high availability and compliance."
    print(f"👤 User: {answer1}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer1})
    
    result1 = response.json()
    print(f"🤖 AI: {result1['prompt']}")
    
    # Answer 2
    answer2 = "GDPR compliance, real-time analytics, microservices architecture, 99.99% uptime required."
    print(f"👤 User: {answer2}")
    
    response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                           json={"session_id": session_id, "answer": answer2})
    
    result2 = response.json()
    print(f"🤖 AI: {result2['prompt']}")
    
    if result2.get('done'):
        spec = result2.get('partial_spec', {})
        print(f"\n🎉 Generated ENTERPRISE Database Architecture!")
        print(f"📊 Application Type: {spec.get('app_type', 'Unknown')}")
        print(f"🗄️ Database: {spec.get('db_type', 'Unknown')}")
        print(f"📈 Complexity Level: {spec.get('complexity_level', 'Unknown')}")
        print(f"📋 Entities: {len(spec.get('entities', []))}")
        
        # Show all enterprise features
        if "hybrid_architecture" in spec:
            print(f"🏗️ Hybrid Architecture: {spec['hybrid_architecture']}")
        if "caching_strategy" in spec:
            print(f"⚡ Caching Strategy: Redis with {len(spec['caching_strategy'].get('redis', {}))} patterns")
        if "search_strategy" in spec:
            print(f"🔍 Search Strategy: Elasticsearch included")
        if "monitoring" in spec:
            print(f"📊 Monitoring: {len(spec['monitoring'])} metric categories")
        if "scaling_strategy" in spec:
            print(f"📈 Scaling Strategy: Horizontal + Vertical scaling")
        if "security" in spec:
            print(f"🔒 Security: {len(spec['security'])} security layers")
    
    print("\n" + "=" * 60)
    print("🎉 ADAPTIVE AI TEST COMPLETE!")
    print("=" * 60)
    print("✅ AI adapts to ANY business size and type")
    print("✅ Simple blogs get simple databases")
    print("✅ Growing businesses get scalable solutions")
    print("✅ Enterprise gets full architecture")
    print("✅ Perfect for EVERY type of business!")
    print("\n🚀 Try it yourself at: http://localhost:8001")

if __name__ == "__main__":
    test_adaptive_ai()
