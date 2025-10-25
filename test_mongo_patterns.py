#!/usr/bin/env python3
"""
Try different MongoDB connection patterns
"""

import os
import pymongo
from dotenv import load_dotenv

def test_mongodb_patterns():
    """Test different MongoDB connection patterns"""
    print("🧪 Testing MongoDB Connection Patterns...")
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    password = os.getenv('PASSOWRD')  # Note: typo in your .env file
    
    if not password:
        print("❌ No password found in .env file")
        return False
    
    print(f"🔑 Password: {password[:5]}...")
    
    # Try different connection patterns
    connection_patterns = [
        # Common Atlas patterns
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/test",
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/",
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/admin",
        f"mongodb+srv://admin:{password}@cluster0.mongodb.net/shipdb",
        
        # Try with different usernames
        f"mongodb+srv://shipdb:{password}@cluster0.mongodb.net/test",
        f"mongodb+srv://user:{password}@cluster0.mongodb.net/test",
        f"mongodb+srv://root:{password}@cluster0.mongodb.net/test",
        
        # Try with different cluster names
        f"mongodb+srv://admin:{password}@cluster1.mongodb.net/test",
        f"mongodb+srv://admin:{password}@shipdb.mongodb.net/test",
        f"mongodb+srv://admin:{password}@test.mongodb.net/test",
    ]
    
    for i, conn_str in enumerate(connection_patterns, 1):
        print(f"\n🔗 Pattern {i}: {conn_str[:60]}...")
        
        try:
            client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=3000)
            
            # Test connection
            client.admin.command('ping')
            print("✅ MongoDB connection successful!")
            
            # List databases
            databases = client.list_database_names()
            print(f"📊 Available databases: {databases}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed: {str(e)[:80]}...")
            continue
    
    print("❌ All connection patterns failed")
    return False

if __name__ == "__main__":
    test_mongodb_patterns()

