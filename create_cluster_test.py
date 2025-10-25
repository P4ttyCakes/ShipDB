#!/usr/bin/env python3
"""
Try to create a simple MongoDB cluster
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

async def try_create_cluster():
    """Try to create a simple cluster"""
    print("🧪 Trying to create MongoDB cluster...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Atlas credentials
    public_key = os.getenv('ATLAS_PUBLIC_KEY')
    private_key = os.getenv('ATLAS_PRIVATE_KEY')
    project_id = os.getenv('ATLAS_PROJECT_ID')
    
    # Test API connection
    api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
    auth = (public_key, private_key)
    
    # Simple cluster configuration
    cluster_config = {
        "name": "test-cluster",
        "clusterType": "REPLICASET",
        "providerSettings": {
            "providerName": "AWS",
            "regionName": "US_EAST_1",
            "instanceSizeName": "M0"  # Free tier
        },
        "mongoDBMajorVersion": "7.0"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"🌐 Creating cluster in project: {project_id}")
            
            response = await client.post(
                f"{api_base}/groups/{project_id}/clusters",
                auth=auth,
                json=cluster_config,
                timeout=30.0
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
            if response.status_code == 201:
                print("✅ Cluster creation initiated!")
                return True
            else:
                print(f"❌ Cluster creation failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Cluster creation failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(try_create_cluster())

