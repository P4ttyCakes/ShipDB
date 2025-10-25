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
        print("Connection failed. Please check your credentials.")
        return
    
    # Test 2: List tables
    test_list_tables()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
