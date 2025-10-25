#!/usr/bin/env python3
"""
Claude Social Media Platform Test
Tests Claude's ability to build a comprehensive social media database
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('backend')

from claude_api_client import create_claude_dynamodb_session

def test_claude_social_media_platform():
    """Test Claude building a complete social media platform database"""
    
    print("🤖 Claude Social Media Platform Test")
    print("=" * 60)
    print("Testing Claude's ability to build a comprehensive social media database")
    print("=" * 60)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create Claude client
    api_key = "your_claude_api_key"
    claude_client = create_claude_dynamodb_session(api_key)
    
    # Test message for Claude
    test_message = """
    Build a social media platform database in DynamoDB that handles all the in-depth tables you would need.
    
    Requirements:
    - Users and profiles
    - Posts and content
    - Social relationships (follows, friends)
    - Interactions (likes, comments, shares)
    - Messaging system
    - Notifications
    - Groups and communities
    - Media and file storage
    - Analytics and engagement tracking
    
    Please:
    1. First validate AWS credentials
    2. Design comprehensive table schemas with proper GSI/LSI for performance
    3. Create all necessary tables
    4. Add sample data to demonstrate the system
    5. Show how to query for common social media operations (feed generation, user relationships, etc.)
    
    Make sure to include proper indexing for:
    - User feeds (posts by followed users)
    - Trending content
    - User relationships
    - Time-based queries
    - Analytics and reporting
    
    Use the available DynamoDB functions to accomplish this step by step.
    """
    
    system_prompt = """
    You are a senior database architect specializing in social media platforms. You have access to DynamoDB functions that you can call to:
    - Create simple and advanced tables with GSI/LSI
    - Execute transactions for atomic operations
    - Query and scan data for complex operations
    - Manage multiple tables and relationships
    
    For a social media platform, you need to design:
    1. User management (profiles, authentication)
    2. Content system (posts, media, stories)
    3. Social graph (follows, friends, blocks)
    4. Interactions (likes, comments, shares, reactions)
    5. Messaging (direct messages, group chats)
    6. Notifications (real-time updates)
    7. Communities (groups, pages, events)
    8. Analytics (engagement, reach, insights)
    
    Always use the available functions to accomplish DynamoDB tasks. Be thorough and explain what you're doing.
    When creating advanced tables, make sure to include proper AttributeDefinitions for all keys and indexes.
    Design for scalability and performance with appropriate GSI/LSI.
    """
    
    print("📤 Sending comprehensive request to Claude...")
    print("Request: Build a complete social media platform database")
    print("-" * 60)
    
    try:
        response = claude_client.send_message(test_message, system_prompt)
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            return False
        
        print("✅ Claude response received")
        
        # Process any function calls
        processed = claude_client.process_claude_response(response)
        
        print(f"\n📊 Function Results ({len(processed['function_results'])} calls):")
        print("=" * 60)
        
        for i, result in enumerate(processed["function_results"], 1):
            print(f"\n{i}. Function: {result['function']}")
            print(f"   Parameters: {json.dumps(result['parameters'], indent=2)}")
            print(f"   Result: {json.dumps(result['result'], indent=2)}")
            print("-" * 50)
        
        # Show Claude's text response
        if "content" in response:
            print("\n🤖 Claude's Analysis and Design:")
            print("=" * 60)
            for content_item in response["content"]:
                if content_item["type"] == "text":
                    print(content_item["text"])
        
        print("\n" + "=" * 60)
        print("🎉 Claude Social Media Platform Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_function_calls():
    """Test some direct function calls to verify system works"""
    print("\n🧪 Testing Direct Function Calls")
    print("-" * 40)
    
    try:
        from claude_dynamodb_driver import call_function
        
        # Test credentials
        result = call_function("validate_credentials")
        print(f"✅ Credentials: {result['success']}")
        
        # Test listing tables
        result = call_function("list_all_tables")
        print(f"✅ Tables found: {result['count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct function test failed: {e}")
        return False

def main():
    """Run the complete test"""
    print("🚀 Starting Claude Social Media Platform Test")
    print("=" * 80)
    
    # Test 1: Direct function calls
    if not test_direct_function_calls():
        print("❌ Direct function test failed - stopping")
        return
    
    # Test 2: Claude API integration
    print("\n🤖 Testing Claude API Integration...")
    success = test_claude_social_media_platform()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("Claude successfully built a social media platform database!")
        print("Check the function results above to see what Claude created.")
    else:
        print("\n💥 FAILED!")
        print("Claude test failed - check the error messages above.")

if __name__ == "__main__":
    main()
