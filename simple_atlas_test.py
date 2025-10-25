#!/usr/bin/env python3
"""
Simple Atlas API Test with Better Error Handling
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

async def test_atlas_simple():
    """Simple Atlas API test"""
    print("🧪 Simple Atlas API Test...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Atlas credentials
    public_key = os.getenv('ATLAS_PUBLIC_KEY')
    private_key = os.getenv('ATLAS_PRIVATE_KEY')
    project_id = os.getenv('ATLAS_PROJECT_ID')
    
    print(f"🔑 Public Key: {public_key}")
    print(f"🔑 Private Key: {private_key}")
    print(f"🔑 Project ID: {project_id}")
    
    # Test API connection
    api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
    auth = (public_key, private_key)
    
    try:
        async with httpx.AsyncClient() as client:
            # Try to get project info
            print(f"🌐 Testing: {api_base}/groups/{project_id}")
            
            response = await client.get(
                f"{api_base}/groups/{project_id}",
                auth=auth,
                timeout=30.0
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Atlas API credentials are valid!")
                return True
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Atlas API test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_atlas_simple())

