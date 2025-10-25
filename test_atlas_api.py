#!/usr/bin/env python3
"""
Test MongoDB Atlas API Credentials
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

async def test_atlas_api_credentials():
    """Test MongoDB Atlas API credentials"""
    print("🧪 Testing MongoDB Atlas API Credentials...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Atlas credentials
    public_key = os.getenv('ATLAS_PUBLIC_KEY')
    private_key = os.getenv('ATLAS_PRIVATE_KEY')
    project_id = os.getenv('ATLAS_PROJECT_ID')
    
    if not public_key or not private_key or not project_id:
        print("❌ Missing Atlas credentials in .env file")
        print("Required:")
        print("- MONGODB_ATLAS_PUBLIC_KEY")
        print("- MONGODB_ATLAS_PRIVATE_KEY") 
        print("- MONGODB_ATLAS_PROJECT_ID")
        return False
    
    print(f"🔑 Public Key: {public_key[:10]}...")
    print(f"🔑 Private Key: {private_key[:10]}...")
    print(f"🔑 Project ID: {project_id}")
    
    # Test API connection
    api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
    auth = (public_key, private_key)
    
    try:
        async with httpx.AsyncClient() as client:
            # Test getting project info
            response = await client.get(
                f"{api_base}/groups/{project_id}",
                auth=auth
            )
            
            if response.status_code == 200:
                project_data = response.json()
                print("✅ Atlas API credentials are valid!")
                print(f"📊 Project Name: {project_data.get('name', 'Unknown')}")
                
                # List clusters
                clusters_response = await client.get(
                    f"{api_base}/groups/{project_id}/clusters",
                    auth=auth
                )
                
                if clusters_response.status_code == 200:
                    clusters = clusters_response.json()
                    print(f"📊 Clusters: {len(clusters.get('results', []))}")
                    for cluster in clusters.get('results', []):
                        print(f"   - {cluster['name']} ({cluster['stateName']})")
                
                return True
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Atlas API test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_atlas_api_credentials())
