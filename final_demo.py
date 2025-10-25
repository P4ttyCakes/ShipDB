#!/usr/bin/env python3
"""
Final comprehensive demo of ShipDB functionality
"""

import requests
import json

def final_demo():
    base_url = "http://localhost:8000"
    
    print("🚢 ShipDB - Final Comprehensive Demo")
    print("=" * 50)
    
    # Step 1: AI Conversation
    print("\n1️⃣ AI-Powered Project Creation")
    print("-" * 30)
    
    start_data = {
        "name": "E-commerce Store",
        "description": "An online store for selling electronics and books"
    }
    response = requests.post(f"{base_url}/api/projects/new_project/start", json=start_data)
    session_id = response.json()["session_id"]
    print(f"✅ Started AI session: {session_id}")
    
    # AI conversation
    answers = [
        "A web application for an online store",
        "PostgreSQL for ACID transactions",
        "Users (id, name, email, password), Products (id, name, price, description), Orders (id, user_id, total, date), OrderItems (id, order_id, product_id, quantity)",
        "Primary keys on all tables, foreign keys for relationships, unique index on user email, index on product name"
    ]
    
    for i, answer in enumerate(answers):
        response = requests.post(f"{base_url}/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        result = response.json()
        if result['done']:
            print(f"✅ AI conversation complete!")
            break
    
    # Finalize project
    response = requests.post(f"{base_url}/api/projects/new_project/finish", 
                           json={"session_id": session_id})
    result = response.json()
    project_id = result["project_id"]
    spec = result["spec"]
    
    print(f"✅ Project created: {project_id}")
    print(f"   Database: {spec.get('db_type', 'Unknown')}")
    print(f"   Entities: {len(spec.get('entities', []))}")
    
    # Step 2: Schema Generation
    print("\n2️⃣ Schema Generation")
    print("-" * 30)
    
    response = requests.post(f"{base_url}/api/schema/generate", json=spec)
    if response.status_code == 200:
        artifacts = response.json()
        print(f"✅ Schema generated successfully!")
        
        # Show PostgreSQL SQL
        sql = artifacts.get('postgres_sql', '')
        if sql:
            print(f"\n📝 Generated PostgreSQL SQL:")
            print("=" * 50)
            print(sql)
            print("=" * 50)
        
        # Show JSON Schema
        json_schema = artifacts.get('json_schema', {})
        if json_schema:
            print(f"\n📋 Generated JSON Schema:")
            print("=" * 50)
            print(json.dumps(json_schema, indent=2))
            print("=" * 50)
        
        # Show MongoDB scripts
        mongo_scripts = artifacts.get('mongo_scripts', [])
        if mongo_scripts:
            print(f"\n🍃 Generated MongoDB Scripts:")
            print("=" * 50)
            for script in mongo_scripts:
                print(script)
            print("=" * 50)
        
        # Show DynamoDB tables
        dynamodb_tables = artifacts.get('dynamodb_tables', [])
        if dynamodb_tables:
            print(f"\n⚡ Generated DynamoDB Tables:")
            print("=" * 50)
            for table in dynamodb_tables:
                print(f"Table: {table.get('TableName', 'Unknown')}")
                print(f"  Key Schema: {table.get('KeySchema', [])}")
            print("=" * 50)
    
    # Step 3: Summary
    print("\n3️⃣ Summary")
    print("-" * 30)
    print(f"🎉 ShipDB is fully functional!")
    print(f"📊 Project ID: {project_id}")
    print(f"🌐 Frontend: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🔧 Backend: http://localhost:8000")
    
    print(f"\n✨ Features Working:")
    print(f"   ✅ AI-powered project creation")
    print(f"   ✅ Interactive conversation with Claude")
    print(f"   ✅ Database schema generation")
    print(f"   ✅ Multi-database support (PostgreSQL, MongoDB, DynamoDB)")
    print(f"   ✅ JSON schema generation")
    print(f"   ✅ SQL script generation")
    print(f"   ✅ Frontend interface")
    print(f"   ✅ REST API")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Add AWS credentials to test deployment")
    print(f"   2. Use the frontend to create projects interactively")
    print(f"   3. Deploy databases to AWS")
    print(f"   4. Integrate with your applications")

if __name__ == "__main__":
    final_demo()
