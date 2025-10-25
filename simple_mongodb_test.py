#!/usr/bin/env python3
"""
Super Simple MongoDB Atlas Connection Test
"""

import os
import pymongo
from dotenv import load_dotenv

def test_mongodb_connection():
    """Test basic MongoDB Atlas connection"""
    print("🧪 Testing MongoDB Atlas Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get connection string from environment
    connection_string = os.getenv('MONGODB_CONNECTION_STRING')
    
    if not connection_string:
        print("❌ No MONGODB_CONNECTION_STRING found in .env file")
        return False
    
    print(f"🔗 Connection String: {connection_string[:50]}...")
    
    try:
        # Test connection
        client = pymongo.MongoClient(connection_string)
        
        # Ping the database
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"📊 Available databases: {databases}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()

