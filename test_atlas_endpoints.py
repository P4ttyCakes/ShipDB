#!/usr/bin/env python3
"""
Test Atlas API with different endpoints
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

async def test_atlas_endpoints():
    """Test different Atlas API endpoints"""
    print("🧪 Testing Atlas API Endpoints...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Atlas credentials
    public_key = os.getenv('ATLAS_PUBLIC_KEY')
    private_key = os.getenv('ATLAS_PRIVATE_KEY')
    project_id = os.getenv('ATLAS_PROJECT_ID')
    
    # Test API connection
    api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
    auth = (public_key, private_key)
    
    # Test different endpoints
    endpoints = [
        f"/groups/{project_id}",
        f"/groups/{project_id}/clusters",
        f"/groups/{project_id}/databaseUsers",
        f"/groups/{project_id}/accessList",
        "/orgs",  # Try organization endpoint
    ]
    
    try:
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                print(f"\n🌐 Testing: {api_base}{endpoint}")
                
                try:
                    response = await client.get(
                        f"{api_base}{endpoint}",
                        auth=auth,
                        timeout=10.0
                    )
                    
                    print(f"📊 Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ This endpoint works!")
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"📊 Keys: {list(data.keys())}")
                        elif isinstance(data, list):
                            print(f"📊 Items: {len(data)}")
                    else:
                        print(f"❌ Failed: {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Overall error: {e}")

if __name__ == "__main__":
    asyncio.run(test_atlas_endpoints())

