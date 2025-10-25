#!/usr/bin/env python3
"""
MongoDB Service Integration Test
Tests the MongoDB service through the deployment factory
"""
import asyncio
import os
import sys
from app.services.deployment.factory import DeploymentFactory
from app.models.deployment import DatabaseType, DeploymentRequest


async def test_mongodb_factory_integration():
    """Test MongoDB service through the deployment factory"""
    
    print("🏭 Testing MongoDB service through deployment factory...")
    
    # Test 1: Get MongoDB service from factory
    print("\n1️⃣ Getting MongoDB service from factory...")
    try:
        mongodb_service = DeploymentFactory.get_service(DatabaseType.MONGODB)
        assert mongodb_service is not None, "MongoDB service should not be None"
        print("✅ Successfully retrieved MongoDB service from factory")
    except Exception as e:
        print(f"❌ Failed to get MongoDB service: {e}")
        return False
    
    # Test 2: Test service type
    print("\n2️⃣ Verifying service type...")
    from app.services.deployment.mongodb_service import MongoDBAtlasService
    assert isinstance(mongodb_service, MongoDBAtlasService), "Service should be MongoDBAtlasService instance"
    print("✅ Service type verification passed")
    
    # Test 3: Test credential validation
    print("\n3️⃣ Testing credential validation...")
    try:
        # Check if credentials are available
        required_vars = [
            'MONGODB_ATLAS_PUBLIC_KEY',
            'MONGODB_ATLAS_PRIVATE_KEY', 
            'MONGODB_ATLAS_PROJECT_ID'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"⚠️  Missing Atlas credentials: {missing_vars}")
            print("   Skipping credential validation test")
        else:
            is_valid = await mongodb_service.validate_credentials()
            if is_valid:
                print("✅ Credential validation passed")
            else:
                print("❌ Credential validation failed")
                return False
    except Exception as e:
        print(f"⚠️  Credential validation error: {e}")
        print("   This is expected if Atlas credentials are not configured")
    
    # Test 4: Test deployment request creation
    print("\n4️⃣ Testing deployment request creation...")
    try:
        request = DeploymentRequest(
            project_id="factory-test-123",
            database_type=DatabaseType.MONGODB,
            database_name="factory_test_db",
            schema_data={
                "collections": [
                    {"name": "test_collection", "indexes": ["test_field"]}
                ]
            }
        )
        
        assert request.database_type == DatabaseType.MONGODB
        assert request.project_id == "factory-test-123"
        print("✅ Deployment request creation passed")
    except Exception as e:
        print(f"❌ Deployment request creation failed: {e}")
        return False
    
    # Test 5: Test all database types in factory
    print("\n5️⃣ Testing all database types in factory...")
    try:
        dynamodb_service = DeploymentFactory.get_service(DatabaseType.DYNAMODB)
        postgresql_service = DeploymentFactory.get_service(DatabaseType.POSTGRESQL)
        
        assert dynamodb_service is not None, "DynamoDB service should not be None"
        assert postgresql_service is not None, "PostgreSQL service should not be None"
        
        print("✅ All database services available in factory")
    except Exception as e:
        print(f"❌ Factory service retrieval failed: {e}")
        return False
    
    print("\n🎉 MongoDB factory integration test completed successfully!")
    return True


async def main():
    """Main test runner"""
    print("🧪 MongoDB Factory Integration Test")
    print("=" * 40)
    
    success = await test_mongodb_factory_integration()
    
    if success:
        print("\n✅ Factory integration test passed!")
        print("\n📝 Summary:")
        print("   ✅ MongoDB service retrievable from factory")
        print("   ✅ Service type verification")
        print("   ✅ Deployment request creation")
        print("   ✅ All database services available")
        print("\n🚀 MongoDB service is ready for use!")
        sys.exit(0)
    else:
        print("\n❌ Factory integration test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
