#!/usr/bin/env python3
"""
Test MongoDB with local connection (if available)
"""

import pymongo
import os

def test_local_mongodb():
    """Test local MongoDB connection"""
    print("🧪 Testing Local MongoDB Connection...")
    
    try:
        # Try local MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Local MongoDB connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📊 Available databases: {databases}")
        
        return True
        
    except Exception as e:
        print(f"❌ Local MongoDB not available: {e}")
        return False

if __name__ == "__main__":
    test_local_mongodb()

