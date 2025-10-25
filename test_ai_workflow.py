#!/usr/bin/env python3
"""
Test the full AI workflow for ShipDB
This tests the complete flow from project creation to schema generation
"""

import requests
import json
import time
import sys

def test_ai_workflow():
    base_url = "http://localhost:8000"
    
    print("🤖 Testing ShipDB AI Workflow")
    print("=" * 50)
    
    # Test 1: Start a new project with AI
    print("\n1️⃣ Starting AI-powered project creation...")
    try:
        start_data = {
            "name": "E-commerce Store",
            "description": "A simple e-commerce application for selling products online"
        }
        
        response = requests.post(f"{base_url}/api/projects/new_project/start", json=start_data)
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            first_question = result["prompt"]
            print(f"✅ Project started successfully!")
            print(f"   Session ID: {session_id}")
            print(f"   First question: {first_question}")
        else:
            print(f"❌ Failed to start project: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting project: {e}")
        return False
    
    # Test 2: Answer the first question
    print("\n2️⃣ Answering AI questions...")
    try:
        # Answer the first question
        answer_data = {
            "session_id": session_id,
            "answer": "It's a web application for an online store that sells electronics and books. Users can browse products, add them to cart, and make purchases."
        }
        
        response = requests.post(f"{base_url}/api/projects/new_project/next", json=answer_data)
        if response.status_code == 200:
            result = response.json()
            next_question = result["prompt"]
            done = result["done"]
            partial_spec = result["partial_spec"]
            print(f"✅ Answered first question!")
            print(f"   Next question: {next_question}")
            print(f"   Done: {done}")
            print(f"   Partial spec keys: {list(partial_spec.keys())}")
        else:
            print(f"❌ Failed to answer question: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error answering question: {e}")
        return False
    
    # Test 3: Continue the conversation
    print("\n3️⃣ Continuing AI conversation...")
    try:
        # Answer a few more questions to build up the spec
        answers = [
            "I need to store users, products, orders, and cart items. Users have email and password, products have name, price, and description, orders have user_id and total_amount, and cart items link users to products.",
            "I want to use PostgreSQL for this project because I need ACID transactions for handling orders and payments.",
            "Yes, I need indexes on user email, product name, and order date for better performance."
        ]
        
        for i, answer in enumerate(answers):
            if done:
                break
                
            answer_data = {
                "session_id": session_id,
                "answer": answer
            }
            
            response = requests.post(f"{base_url}/api/projects/new_project/next", json=answer_data)
            if response.status_code == 200:
                result = response.json()
                next_question = result["prompt"]
                done = result["done"]
                partial_spec = result["partial_spec"]
                print(f"✅ Answered question {i+2}!")
                print(f"   Question: {next_question}")
                print(f"   Done: {done}")
                if done:
                    print(f"   Final spec keys: {list(partial_spec.keys())}")
            else:
                print(f"❌ Failed to answer question {i+2}: {response.status_code}")
                break
    except Exception as e:
        print(f"❌ Error in conversation: {e}")
        return False
    
    # Test 4: Finalize the project
    print("\n4️⃣ Finalizing project...")
    try:
        finalize_data = {
            "session_id": session_id
        }
        
        response = requests.post(f"{base_url}/api/projects/new_project/finish", json=finalize_data)
        if response.status_code == 200:
            result = response.json()
            project_id = result["project_id"]
            spec = result["spec"]
            print(f"✅ Project finalized!")
            print(f"   Project ID: {project_id}")
            print(f"   Spec keys: {list(spec.keys())}")
            print(f"   Database type: {spec.get('db_type', 'Not specified')}")
            print(f"   Entities: {len(spec.get('entities', []))}")
        else:
            print(f"❌ Failed to finalize project: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error finalizing project: {e}")
        return False
    
    # Test 5: Generate schema artifacts
    print("\n5️⃣ Generating schema artifacts...")
    try:
        response = requests.post(f"{base_url}/api/schema/generate", json=spec)
        if response.status_code == 200:
            artifacts = response.json()
            print(f"✅ Schema generated successfully!")
            print(f"   Artifacts: {list(artifacts.keys())}")
            
            # Show some sample artifacts
            if "postgres_sql" in artifacts:
                sql_lines = artifacts["postgres_sql"].split('\n')
                print(f"   PostgreSQL SQL ({len(sql_lines)} lines):")
                for line in sql_lines[:5]:  # Show first 5 lines
                    if line.strip():
                        print(f"     {line}")
                if len(sql_lines) > 5:
                    print(f"     ... and {len(sql_lines) - 5} more lines")
        else:
            print(f"❌ Failed to generate schema: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating schema: {e}")
        return False
    
    print("\n🎉 AI Workflow Test Complete!")
    print("=" * 50)
    print("✅ All tests passed! Your ShipDB AI functionality is working correctly.")
    print(f"📊 Project ID: {project_id}")
    print("🚀 You can now test the full frontend workflow!")
    
    return True

if __name__ == "__main__":
    success = test_ai_workflow()
    sys.exit(0 if success else 1)
