#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test (Existing Cluster)
Tests connection to an existing MongoDB Atlas cluster without creating new resources
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env file
load_dotenv()


async def test_existing_mongodb_connection():
    """Test connection to existing MongoDB Atlas cluster"""
    
    print("🔗 MongoDB Atlas Existing Connection Test")
    print("=" * 45)
    
    # Get connection details from user
    print("This test will connect to an existing MongoDB Atlas cluster.")
    print("You'll need:")
    print("1. MongoDB Atlas connection string")
    print("2. Database name")
    print("3. Collection name (optional)")
    
    # Get connection string
    connection_string = input("\nEnter your MongoDB Atlas connection string: ").strip()
    if not connection_string:
        print("❌ Connection string is required")
        return False
    
    # Get database name
    database_name = input("Enter database name: ").strip()
    if not database_name:
        print("❌ Database name is required")
        return False
    
    # Get collection name (optional)
    collection_name = input("Enter collection name (optional): ").strip()
    
    print(f"\n🔌 Testing connection to MongoDB Atlas...")
    print(f"   Connection String: {connection_string[:50]}...")
    print(f"   Database: {database_name}")
    if collection_name:
        print(f"   Collection: {collection_name}")
    
    try:
        # Test connection
        print("\n1️⃣ Testing MongoDB connection...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        
        # Ping the server
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        print("\n2️⃣ Testing database access...")
        db = client[database_name]
        print(f"✅ Successfully accessed database: {database_name}")
        
        # List collections
        print("\n3️⃣ Listing collections...")
        collections = db.list_collection_names()
        print(f"   Found {len(collections)} collections:")
        for col in collections:
            print(f"     - {col}")
        
        # Test collection access if specified
        if collection_name:
            print(f"\n4️⃣ Testing collection access: {collection_name}")
            collection = db[collection_name]
            
            # Test basic operations
            print("   Testing basic operations...")
            
            # Insert a test document
            test_doc = {
                "test_id": f"connection_test_{int(time.time())}",
                "message": "MongoDB connection test",
                "timestamp": time.time()
            }
            
            result = collection.insert_one(test_doc)
            print(f"✅ Successfully inserted test document")
            
            # Query the document
            found_doc = collection.find_one({"test_id": test_doc["test_id"]})
            if found_doc:
                print(f"✅ Successfully queried document")
            else:
                print(f"❌ Failed to query document")
            
            # Clean up test document
            collection.delete_one({"test_id": test_doc["test_id"]})
            print(f"✅ Cleaned up test document")
            
            # List indexes
            print("   Listing indexes...")
            indexes = list(collection.list_indexes())
            print(f"   Found {len(indexes)} indexes:")
            for index in indexes:
                print(f"     - {index['name']}: {index['key']}")
        
        client.close()
        print("\n🎉 MongoDB connection test completed successfully!")
        
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Check your connection string and network access")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        print("   Check your connection string and network access")
        return False
    except Exception as e:
        print(f"❌ Error during MongoDB connection test: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    success = await test_existing_mongodb_connection()
    
    if success:
        print("\n✅ MongoDB connection test completed successfully!")
        print("🚀 Your MongoDB Atlas cluster is accessible!")
        sys.exit(0)
    else:
        print("\n❌ MongoDB connection test failed.")
        print("Please check your connection details and try again.")
        sys.exit(1)


if __name__ == "__main__":
    import time
    asyncio.run(main())
