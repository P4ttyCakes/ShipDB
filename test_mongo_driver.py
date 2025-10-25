#!/usr/bin/env python3
"""
Simple MongoDB Driver Test
"""

import os
import pymongo
from dotenv import load_dotenv

def test_mongodb_driver():
    """Test MongoDB driver with connection string"""
    print("🧪 Testing MongoDB Driver...")
    
    # Load environment variables
    load_dotenv()
    
    # Get connection string from environment
    connection_string = os.getenv('MONGODB_CONNECTION_STRING')
    
    if not connection_string:
        print("❌ No MONGODB_CONNECTION_STRING found in .env file")
        print("Please add your MongoDB connection string to .env:")
        print("MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database")
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
        
        # Test creating a simple collection
        db = client['test']
        collection = db['test_collection']
        
        # Insert a test document
        result = collection.insert_one({"test": "Hello MongoDB!", "timestamp": "2024-01-01"})
        print(f"✅ Test document inserted: {result.inserted_id}")
        
        # Query the document
        doc = collection.find_one({"test": "Hello MongoDB!"})
        print(f"✅ Test document retrieved: {doc}")
        
        # Clean up
        collection.drop()
        print("✅ Test collection cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_driver()

