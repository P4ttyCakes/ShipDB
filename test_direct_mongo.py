#!/usr/bin/env python3
"""
Test Direct MongoDB Connection
"""

import os
import pymongo
from dotenv import load_dotenv

def test_direct_mongodb():
    """Test direct MongoDB connection"""
    print("🧪 Testing Direct MongoDB Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    password = os.getenv('PASSOWRD')  # Note: typo in your .env file
    
    if not password:
        print("❌ No password found in .env file")
        return False
    
    print(f"🔑 Password: {password[:5]}...")
    
    # Try different connection string formats
    connection_strings = [
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/test",
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/",
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/admin",
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n🔗 Trying connection string {i}: {conn_str[:50]}...")
        
        try:
            client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
            
            # Test connection
            client.admin.command('ping')
            print("✅ MongoDB connection successful!")
            
            # List databases
            databases = client.list_database_names()
            print(f"📊 Available databases: {databases}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            continue
    
    print("❌ All connection attempts failed")
    return False

if __name__ == "__main__":
    test_direct_mongodb()

