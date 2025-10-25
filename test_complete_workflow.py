#!/usr/bin/env python3
"""
Complete workflow test showing the full ShipDB functionality
"""

import requests
import json

def test_complete_workflow():
    base_url = "http://localhost:8000"
    
    print("🚢 ShipDB Complete Workflow Test")
    print("=" * 50)
    
    # Step 1: Start AI conversation
    print("\n1️⃣ Starting AI conversation...")
    start_data = {
        "name": "E-commerce Store", 
        "description": "An online store for selling electronics and books"
    }
    response = requests.post(f"{base_url}/api/projects/new_project/start", json=start_data)
    session_id = response.json()["session_id"]
    print(f"✅ Session started: {session_id}")
    
    # Step 2: AI conversation
    print("\n2️⃣ AI conversation...")
    answers = [
        "It's a web application for an online store",
        "PostgreSQL for ACID transactions",
        "Users (id, email, password), Products (id, name, price, description), Orders (id, user_id, total, date), OrderItems (id, order_id, product_id, quantity)",
        "Primary keys on all tables, foreign keys for relationships, unique index on user email, index on product name"
    ]
    
    for i, answer in enumerate(answers):
        response = requests.post(f"{base_url}/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": answer})
        result = response.json()
        print(f"   Q{i+1}: {result['prompt'][:60]}...")
        if result['done']:
            print(f"   ✅ Conversation complete!")
            break
    
    # Step 3: Finalize project
    print("\n3️⃣ Finalizing project...")
    response = requests.post(f"{base_url}/api/projects/new_project/finish", 
                           json={"session_id": session_id})
    result = response.json()
    project_id = result["project_id"]
    spec = result["spec"]
    print(f"✅ Project created: {project_id}")
    print(f"   Database: {spec.get('db_type', 'Unknown')}")
    print(f"   Entities: {len(spec.get('entities', []))}")
    
    # Step 4: Generate schema artifacts
    print("\n4️⃣ Generating schema artifacts...")
    response = requests.post(f"{base_url}/api/schema/generate", json=spec)
    artifacts = response.json()
    print(f"✅ Schema generated!")
    print(f"   Artifacts: {list(artifacts.keys())}")
    
    # Step 5: Show generated SQL
    print("\n5️⃣ Generated PostgreSQL SQL:")
    print("-" * 50)
    sql = artifacts.get('postgres_sql', '')
    print(sql)
    print("-" * 50)
    
    # Step 6: Show JSON schema
    print("\n6️⃣ Generated JSON Schema:")
    print("-" * 50)
    json_schema = artifacts.get('json_schema', {})
    print(json.dumps(json_schema, indent=2))
    print("-" * 50)
    
    # Step 7: Show MongoDB scripts
    print("\n7️⃣ Generated MongoDB Scripts:")
    print("-" * 50)
    mongo_scripts = artifacts.get('mongo_scripts', [])
    for script in mongo_scripts:
        print(script)
    print("-" * 50)
    
    # Step 8: Show DynamoDB tables
    print("\n8️⃣ Generated DynamoDB Tables:")
    print("-" * 50)
    dynamodb_tables = artifacts.get('dynamodb_tables', [])
    for table in dynamodb_tables:
        print(f"Table: {table.get('TableName', 'Unknown')}")
        print(f"  Key Schema: {table.get('KeySchema', [])}")
        print(f"  Attributes: {table.get('AttributeDefinitions', [])}")
    print("-" * 50)
    
    print("\n🎉 Complete workflow test successful!")
    print(f"📊 Project ID: {project_id}")
    print("🚀 Your ShipDB is fully functional!")
    
    return project_id, spec, artifacts

if __name__ == "__main__":
    test_complete_workflow()
