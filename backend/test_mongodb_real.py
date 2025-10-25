#!/usr/bin/env python3
"""
Real MongoDB Atlas Service Testing Script
Tests the MongoDB service with actual Atlas API calls (requires valid credentials)
"""
import asyncio
import os
import sys
from app.services.deployment.mongodb_service import MongoDBAtlasService
from app.models.deployment import DeploymentRequest, DatabaseType


async def test_real_mongodb_deployment():
    """Test MongoDB service with real Atlas API calls"""
    
    # Check environment variables
    required_vars = [
        'MONGODB_ATLAS_PUBLIC_KEY',
        'MONGODB_ATLAS_PRIVATE_KEY', 
        'MONGODB_ATLAS_PROJECT_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("\nTo set up MongoDB Atlas credentials:")
        print("1. Go to https://cloud.mongodb.com/")
        print("2. Create a project and get your Project ID")
        print("3. Go to Access Manager > API Keys")
        print("4. Create a new API key with 'Project Owner' permissions")
        print("5. Set these environment variables:")
        for var in missing_vars:
            print(f"   export {var}=your_value_here")
        print("\nOr add them to your .env file:")
        for var in missing_vars:
            print(f"   {var}=your_value_here")
        return False
    
    print("✅ All required environment variables are set")
    
    # Initialize service
    service = MongoDBAtlasService()
    
    # Test 1: Credential validation
    print("\n🔐 Testing credential validation...")
    try:
        is_valid = await service.validate_credentials()
        if is_valid:
            print("✅ MongoDB Atlas credentials are valid")
        else:
            print("❌ MongoDB Atlas credentials are invalid")
            return False
    except Exception as e:
        print(f"❌ Error validating credentials: {e}")
        return False
    
    # Test 2: Create a test deployment request
    print("\n📋 Creating test deployment request...")
    
    # Use a unique project ID to avoid conflicts
    import time
    unique_id = f"test-{int(time.time())}"
    
    test_request = DeploymentRequest(
        project_id=unique_id,
        database_type=DatabaseType.MONGODB,
        database_name="test_database",
        schema_data={
            "collections": [
                {
                    "name": "users",
                    "indexes": ["email", "username"]
                },
                {
                    "name": "products",
                    "indexes": ["category", "price"]
                }
            ]
        }
    )
    
    print(f"✅ Created test request for project: {unique_id}")
    
    # Test 3: Ask user if they want to proceed with actual deployment
    print(f"\n⚠️  WARNING: This will create real MongoDB Atlas resources!")
    print(f"   - Cluster name: shipdb-{unique_id[:8]}")
    print(f"   - Database: test_database")
    print(f"   - Collections: users, products")
    print(f"   - This will use your Atlas free tier quota")
    
    response = input("\nDo you want to proceed with the actual deployment? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Deployment cancelled by user")
        return False
    
    # Test 4: Deploy MongoDB cluster
    print(f"\n🚀 Deploying MongoDB Atlas cluster...")
    try:
        deployment_response = await service.deploy(test_request)
        
        print("✅ MongoDB Atlas cluster deployed successfully!")
        print(f"\n📊 Deployment Details:")
        print(f"   Deployment ID: {deployment_response.deployment_id}")
        print(f"   Status: {deployment_response.status}")
        print(f"   Database Type: {deployment_response.database_type}")
        print(f"   Message: {deployment_response.message}")
        
        print(f"\n🔗 Connection Information:")
        conn_info = deployment_response.connection_info
        print(f"   Connection String: {conn_info['connection_string']}")
        print(f"   Username: {conn_info['username']}")
        print(f"   Password: {conn_info['password']}")
        print(f"   Database: {conn_info['database']}")
        print(f"   Cluster: {conn_info['cluster_name']}")
        print(f"   Collections: {conn_info['collections']}")
        
        print(f"\n🎉 MongoDB Atlas deployment test completed successfully!")
        print(f"\n💡 Next steps:")
        print(f"   1. Connect to your cluster using the connection string")
        print(f"   2. Verify collections and indexes were created")
        print(f"   3. Test your application with the new database")
        print(f"   4. Clean up resources when done testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test runner"""
    print("🧪 MongoDB Atlas Real Deployment Test")
    print("=" * 50)
    
    success = await test_real_mongodb_deployment()
    
    if success:
        print("\n✅ Real MongoDB Atlas test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Real MongoDB Atlas test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
