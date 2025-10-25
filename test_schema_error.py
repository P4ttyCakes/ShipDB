#!/usr/bin/env python3
"""
Test schema generation with incomplete data to reproduce the 500 error
"""

import requests
import json

def test_schema_generation():
    print("🔍 Testing Schema Generation")
    print("=" * 40)
    
    # Test with incomplete spec (like what AI might generate)
    incomplete_spec = {
        "app_type": "Real Estate Platform",
        "db_type": "postgresql",
        "complexity_level": "moderate",
        "entities": [],  # Empty entities array
        "relationships": [],
        "indexes": [],
        "constraints": [],
        "security": [],
        "monitoring": [],
        "backup": [],
        "scaling": [],
        "integrations": []
    }
    
    print("Testing with incomplete spec:")
    print(f"Entities: {len(incomplete_spec['entities'])}")
    
    try:
        response = requests.post("http://localhost:8000/api/schema/generate", 
                               json=incomplete_spec)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Schema generated successfully")
            print(f"PostgreSQL SQL length: {len(result.get('postgres_sql', ''))}")
            print(f"MongoDB scripts: {len(result.get('mongo_scripts', []))}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test with malformed entities
    print("\n" + "=" * 40)
    print("Testing with malformed entities:")
    
    malformed_spec = {
        "app_type": "Test App",
        "db_type": "postgresql",
        "entities": [
            {
                "name": "users",
                "fields": [
                    {"name": "id", "type": "uuid", "required": True, "primary_key": True},
                    {"name": "email", "type": "string", "required": True}
                    # Missing required fields
                ]
            }
        ]
    }
    
    try:
        response = requests.post("http://localhost:8000/api/schema/generate", 
                               json=malformed_spec)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Schema generated successfully")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_schema_generation()
