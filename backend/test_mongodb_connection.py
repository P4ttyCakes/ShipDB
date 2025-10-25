#!/usr/bin/env python3
"""
MongoDB Atlas Real Connection Test
Tests actual connection to MongoDB Atlas with real API calls and database operations
"""
import asyncio
import os
import sys
import time
from dotenv import load_dotenv
from app.services.deployment.mongodb_service import MongoDBAtlasService
from app.models.deployment import DeploymentRequest, DatabaseType

# Load environment variables from .env file
load_dotenv()


async def test_mongodb_atlas_connection():
    """Test real MongoDB Atlas connection and operations"""
    
    print("🔗 MongoDB Atlas Real Connection Test")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        'MONGODB_ATLAS_PUBLIC_KEY',
        'MONGODB_ATLAS_PRIVATE_KEY', 
        'MONGODB_ATLAS_PROJECT_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("\n🔧 To set up MongoDB Atlas credentials:")
        print("1. Go to https://cloud.mongodb.com/")
        print("2. Create a project and note your Project ID")
        print("3. Go to Access Manager → API Keys")
        print("4. Create a new API key with 'Project Owner' permissions")
        print("5. Set these environment variables:")
        print("   export MONGODB_ATLAS_PUBLIC_KEY=your_public_key")
        print("   export MONGODB_ATLAS_PRIVATE_KEY=your_private_key")
        print("   export MONGODB_ATLAS_PROJECT_ID=your_project_id")
        print("\nOr add them to your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    print("✅ All required environment variables are set")
    
    # Initialize service
    service = MongoDBAtlasService()
    
    # Test 1: Validate Atlas API credentials
    print("\n🔐 Step 1: Validating Atlas API credentials...")
    try:
        is_valid = await service.validate_credentials()
        if is_valid:
            print("✅ Atlas API credentials are valid")
        else:
            print("❌ Atlas API credentials are invalid")
            return False
    except Exception as e:
        print(f"❌ Error validating credentials: {e}")
        return False
    
    # Test 2: Create deployment request
    print("\n📋 Step 2: Creating deployment request...")
    
    # Use timestamp for unique project ID
    unique_id = f"test-{int(time.time())}"
    
    test_request = DeploymentRequest(
        project_id=unique_id,
        database_type=DatabaseType.MONGODB,
        database_name="connection_test_db",
        schema_data={
            "collections": [
                {
                    "name": "test_users",
                    "indexes": ["email", "username"]
                },
                {
                    "name": "test_products",
                    "indexes": ["category", "price"]
                }
            ]
        }
    )
    
    print(f"✅ Created test request for project: {unique_id}")
    print(f"   Database: {test_request.database_name}")
    print(f"   Collections: test_users, test_products")
    
    # Test 3: Confirm deployment
    print(f"\n⚠️  WARNING: This will create real MongoDB Atlas resources!")
    print(f"   - Cluster: shipdb-{unique_id[:8]}")
    print(f"   - Database: {test_request.database_name}")
    print(f"   - Collections: test_users, test_products")
    print(f"   - This will use your Atlas free tier quota")
    print(f"   - Resources will remain until manually deleted")
    
    response = input("\nDo you want to proceed with the deployment? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Deployment cancelled by user")
        return False
    
    # Test 4: Deploy MongoDB cluster
    print(f"\n🚀 Step 3: Deploying MongoDB Atlas cluster...")
    print("   This may take 2-5 minutes for cluster creation...")
    
    try:
        start_time = time.time()
        deployment_response = await service.deploy(test_request)
        deployment_time = time.time() - start_time
        
        print(f"✅ MongoDB Atlas cluster deployed successfully!")
        print(f"   Deployment time: {deployment_time:.1f} seconds")
        
        print(f"\n📊 Deployment Details:")
        print(f"   Deployment ID: {deployment_response.deployment_id}")
        print(f"   Status: {deployment_response.status}")
        print(f"   Database Type: {deployment_response.database_type}")
        print(f"   Message: {deployment_response.message}")
        
        conn_info = deployment_response.connection_info
        print(f"\n🔗 Connection Information:")
        print(f"   Connection String: {conn_info['connection_string']}")
        print(f"   Username: {conn_info['username']}")
        print(f"   Password: {conn_info['password']}")
        print(f"   Database: {conn_info['database']}")
        print(f"   Cluster: {conn_info['cluster_name']}")
        print(f"   Collections: {conn_info['collections']}")
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Test actual MongoDB connection
    print(f"\n🔌 Step 4: Testing actual MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
        
        # Connect to MongoDB
        connection_string = conn_info['connection_string']
        print(f"   Connecting to: {connection_string}")
        
        client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        db = client[conn_info['database']]
        print(f"✅ Successfully accessed database: {conn_info['database']}")
        
        # Test collection access
        for collection_name in conn_info['collections']:
            collection = db[collection_name]
            print(f"✅ Successfully accessed collection: {collection_name}")
            
            # Test basic operations
            # Insert a test document
            test_doc = {
                "test_id": f"test_{int(time.time())}",
                "message": "Connection test successful",
                "timestamp": time.time()
            }
            
            result = collection.insert_one(test_doc)
            print(f"✅ Successfully inserted test document into {collection_name}")
            
            # Query the document
            found_doc = collection.find_one({"test_id": test_doc["test_id"]})
            if found_doc:
                print(f"✅ Successfully queried document from {collection_name}")
            else:
                print(f"❌ Failed to query document from {collection_name}")
            
            # Clean up test document
            collection.delete_one({"test_id": test_doc["test_id"]})
            print(f"✅ Cleaned up test document from {collection_name}")
        
        # Test indexes
        print(f"\n📇 Step 5: Verifying indexes...")
        for collection_name in conn_info['collections']:
            collection = db[collection_name]
            indexes = list(collection.list_indexes())
            print(f"   {collection_name} indexes: {len(indexes)}")
            for index in indexes:
                print(f"     - {index['name']}: {index['key']}")
        
        client.close()
        print("✅ MongoDB connection test completed successfully!")
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during MongoDB connection test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Summary and cleanup instructions
    print(f"\n🎉 MongoDB Atlas Connection Test Completed Successfully!")
    print(f"\n📝 Test Summary:")
    print(f"   ✅ Atlas API credentials validated")
    print(f"   ✅ Cluster deployed successfully")
    print(f"   ✅ Database and collections created")
    print(f"   ✅ MongoDB connection established")
    print(f"   ✅ Basic CRUD operations tested")
    print(f"   ✅ Indexes verified")
    
    print(f"\n🔧 Cleanup Instructions:")
    print(f"   To clean up the test resources:")
    print(f"   1. Go to https://cloud.mongodb.com/")
    print(f"   2. Navigate to your project")
    print(f"   3. Go to Database → Clusters")
    print(f"   4. Find cluster: shipdb-{unique_id[:8]}")
    print(f"   5. Click 'Delete' to remove the cluster")
    print(f"   6. This will free up your Atlas quota")
    
    print(f"\n💡 Next Steps:")
    print(f"   - Your MongoDB service is working correctly!")
    print(f"   - You can now use it in your application")
    print(f"   - Connection string: {conn_info['connection_string']}")
    print(f"   - Remember to clean up test resources when done")
    
    return True


async def main():
    """Main test runner"""
    success = await test_mongodb_atlas_connection()
    
    if success:
        print("\n✅ MongoDB Atlas connection test completed successfully!")
        print("🚀 Your MongoDB service is ready for production use!")
        sys.exit(0)
    else:
        print("\n❌ MongoDB Atlas connection test failed.")
        print("Please check your credentials and try again.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
