#!/usr/bin/env python3
"""
Comprehensive test to verify timeout fix works
"""

import requests
import json
import time

def test_complete_flow():
    print("🔧 Testing Complete Flow - Timeout Fix")
    print("=" * 50)
    
    try:
        # Start project
        print("1. Starting project...")
        start_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/start", 
                               json={"name": "Investment Fund", "description": "Investment fund"},
                               timeout=15)
        start_duration = time.time() - start_time
        print(f"   ✅ Started in {start_duration:.2f}s")
        
        session_id = response.json()["session_id"]
        print(f"   📋 Session: {session_id[:8]}...")
        
        # Answer 1
        print("\n2. Answer 1...")
        answer1_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": "stocks and private equity"},
                               timeout=15)
        answer1_duration = time.time() - answer1_time
        print(f"   ✅ Completed in {answer1_duration:.2f}s")
        
        # Answer 2
        print("\n3. Answer 2...")
        answer2_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": "investor details, total money, distributions"},
                               timeout=15)
        answer2_duration = time.time() - answer2_time
        print(f"   ✅ Completed in {answer2_duration:.2f}s")
        
        # Answer 3 - This should trigger completion
        print("\n4. Answer 3 (should complete)...")
        answer3_time = time.time()
        response = requests.post("http://localhost:8000/api/projects/new_project/next", 
                               json={"session_id": session_id, "answer": "name, email, total investment amount"},
                               timeout=15)
        answer3_duration = time.time() - answer3_time
        print(f"   ✅ Completed in {answer3_duration:.2f}s")
        
        result = response.json()
        print(f"\n📊 RESULT:")
        print(f"   Done: {result.get('done', False)}")
        print(f"   Prompt: {result.get('prompt', 'No prompt')}")
        
        if result.get('done'):
            spec = result.get('partial_spec', {})
            entities = spec.get('entities', [])
            print(f"\n🎉 SUCCESS! Conversation completed!")
            print(f"   App Type: {spec.get('app_type', 'Unknown')}")
            print(f"   Database: {spec.get('db_type', 'Unknown')}")
            print(f"   Entities: {len(entities)}")
            
            for entity in entities:
                fields = entity.get('fields', [])
                print(f"   - {entity.get('name')}: {len(fields)} fields")
                for field in fields[:3]:  # Show first 3 fields
                    print(f"     * {field.get('name')} ({field.get('type')})")
            
            # Test schema generation
            print(f"\n5. Testing schema generation...")
            schema_time = time.time()
            schema_response = requests.post("http://localhost:8000/api/schema/generate", 
                                          json=spec, timeout=15)
            schema_duration = time.time() - schema_time
            
            if schema_response.status_code == 200:
                artifacts = schema_response.json()
                print(f"   ✅ Schema generated in {schema_duration:.2f}s")
                print(f"   📝 PostgreSQL: {len(artifacts.get('postgres_sql', ''))} chars")
                print(f"   🍃 MongoDB: {len(artifacts.get('mongo_scripts', []))} scripts")
                
                # Show a snippet of the SQL
                postgres_sql = artifacts.get('postgres_sql', '')
                if postgres_sql:
                    print(f"\n📝 PostgreSQL Preview:")
                    print(postgres_sql[:200] + "..." if len(postgres_sql) > 200 else postgres_sql)
            else:
                print(f"   ❌ Schema failed: {schema_response.status_code}")
        else:
            print(f"\n❌ FAILED - Conversation did not complete")
            print(f"   This means the timeout fix is not working")
        
        total_time = start_duration + answer1_duration + answer2_duration + answer3_duration
        print(f"\n⏱️  Total time: {total_time:.2f}s")
        
        if total_time < 10:
            print("✅ PERFORMANCE: Excellent (< 10s)")
        elif total_time < 20:
            print("✅ PERFORMANCE: Good (< 20s)")
        else:
            print("⚠️  PERFORMANCE: Slow (> 20s)")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR - The fix is not working")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_complete_flow()
