#!/usr/bin/env python3
"""
Test Supabase PostgreSQL Driver
Tests connection, table operations, and CRUD functionality
"""

import os
from dotenv import load_dotenv
from claude_supabase_driver import call_supabase_function, SUPABASE_FUNCTION_REGISTRY

load_dotenv()

def test_supabase_connection():
    """Test Supabase credentials and connection"""
    print("Testing Supabase connection...")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', 'Not set')}")
    print(f"SUPABASE_KEY: {'Set' if os.getenv('SUPABASE_KEY') else 'Not set'}")
    
    result = call_supabase_function("validate_credentials")
    print(f"Result: {result}")
    return result.get("success", False)

def test_list_tables():
    """Test listing tables"""
    print("\nTesting list_tables...")
    result = call_supabase_function("list_tables")
    print(f"Result: {result}")
    return result.get("success", False)

def test_crud_operations():
    """Test CRUD operations on a test table"""
    print("\n" + "=" * 60)
    print("Testing CRUD Operations")
    print("=" * 60)
    
    test_table = "test_users"
    
    # Check if table exists by trying to query it
    print(f"\n1. Checking if {test_table} exists...")
    result = call_supabase_function("query_table", table_name=test_table, filters={})
    
    if not result.get("success"):
        print(f"   Table {test_table} doesn't exist yet.")
        print(f"   Create it in Supabase dashboard with SQL:")
        print(f"   CREATE TABLE {test_table} (")
        print(f"       id SERIAL PRIMARY KEY,")
        print(f"       name VARCHAR(100),")
        print(f"       email VARCHAR(100),")
        print(f"       age INTEGER")
        print(f"   );")
        print(f"\n   Then re-run this test.")
        return False
    
    # Test INSERT
    print(f"\n2. Testing INSERT into {test_table}...")
    insert_data = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    }
    result = call_supabase_function("insert_row", table_name=test_table, row_data=insert_data)
    print(f"   Result: {result}")
    
    if not result.get("success"):
        print(f"   INSERT failed")
        return False
    
    # Get the inserted ID
    inserted_id = result.get("data", [{}])[0].get("id") if result.get("data") else None
    print(f"   Inserted ID: {inserted_id}")
    
    # Test QUERY
    print(f"\n3. Testing QUERY from {test_table}...")
    result = call_supabase_function("query_table", table_name=test_table, filters={"id": inserted_id})
    print(f"   Result: {result}")
    
    if not result.get("success"):
        print(f"   QUERY failed")
        return False
    
    # Test UPDATE
    print(f"\n4. Testing UPDATE on {test_table}...")
    update_data = {"age": 26}
    result = call_supabase_function("update_row", table_name=test_table, filters={"id": inserted_id}, update_data=update_data)
    print(f"   Result: {result}")
    
    if not result.get("success"):
        print(f"   UPDATE failed")
        return False
    
    # Test DELETE
    print(f"\n5. Testing DELETE from {test_table}...")
    result = call_supabase_function("delete_row", table_name=test_table, filters={"id": inserted_id})
    print(f"   Result: {result}")
    
    if not result.get("success"):
        print(f"   DELETE failed")
        return False
    
    print(f"\n✅ All CRUD operations completed successfully!")
    return True

def main():
    print("=" * 60)
    print("Supabase Driver Test")
    print("=" * 60)
    
    # Check environment variables
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    # Test 1: Connection
    success = test_supabase_connection()
    if not success:
        print("\nConnection failed. Please check your credentials.")
        return
    
    # Test 2: List tables
    test_list_tables()
    
    # Test 3: CRUD operations
    test_crud_operations()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
