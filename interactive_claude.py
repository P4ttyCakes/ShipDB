#!/usr/bin/env python3
"""
Interactive Claude DynamoDB Builder
Just run this and tell Claude what to build!
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('backend')

from real_claude_client import create_real_claude_session

def run_claude_request(prompt):
    """Run a single Claude request"""
    print(f"\n📤 Sending request to Claude: '{prompt}'")
    print("-" * 50)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Debug: Check if credentials are loaded
    print(f"🔑 AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:10]}...")
    print(f"🔑 AWS_SECRET_ACCESS_KEY: {os.getenv('AWS_SECRET_ACCESS_KEY')[:10]}...")
    print(f"🔑 CLAUDE_API_KEY: {os.getenv('CLAUDE_API_KEY')[:10]}...")
    
    # Get credentials from environment
    api_key = os.getenv('CLAUDE_API_KEY')
    claude_client = create_real_claude_session(api_key)
    
    try:
        response = claude_client.send_message(prompt)
        
        if not response["success"]:
            print(f"❌ Error: {response['error']}")
            return False
        
        print("✅ Claude response received!")
        
        # Process function calls
        processed = claude_client.process_claude_response(response)
        
        print(f"\n📊 Claude made {len(processed['function_results'])} function calls:")
        print("=" * 50)
        
        successful_resources = []
        for i, result in enumerate(processed["function_results"], 1):
            print(f"\n{i}. Function: {result['function']}")
            print(f"   Success: {result['result']['success']}")
            
            if result['result']['success']:
                if 'table_name' in result['result']:
                    table_name = result['result']['table_name']
                    successful_resources.append(f"DynamoDB Table: {table_name}")
                    print(f"   Table: {table_name}")
                elif 'collection_name' in result['result']:
                    collection_name = result['result']['collection_name']
                    successful_resources.append(f"MongoDB Collection: {collection_name}")
                    print(f"   Collection: {collection_name}")
                if 'message' in result['result']:
                    print(f"   Message: {result['result']['message']}")
            else:
                print(f"   Error: {result['result'].get('error', 'Unknown error')}")
            print("-" * 30)
        
        if successful_resources:
            print(f"\n🎉 SUCCESS! Created {len(successful_resources)} resources:")
            for resource in successful_resources:
                print(f"   ✅ {resource}")
        
        # Show Claude's text response
        if processed["claude_response"]["success"]:
            response_obj = processed["claude_response"]["response"]
            print("\n🤖 Claude's Analysis:")
            print("=" * 50)
            for content_item in response_obj.content:
                if content_item.type == "text":
                    print(content_item.text)
        
        if len(processed["function_results"]) > 0:
            print(f"\n🎉 SUCCESS! Claude built your system!")
            print(f"✅ {len(processed['function_results'])} operations completed")
            return True
        else:
            print("\n⚠️  Claude responded but didn't call any functions")
            print("   Try being more specific about what you want built")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🤖 Interactive Claude Database Builder")
    print("=" * 50)
    print("Tell Claude what database system you want to build!")
    print("Supports both DynamoDB and MongoDB!")
    print("=" * 50)
    
    # Check if prompt provided as command line argument
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"Using command line prompt: '{prompt}'")
        run_claude_request(prompt)
        return
    
    # Interactive mode
    while True:
        print("\n💡 What do you want Claude to build?")
        print("Examples of simple prompts that Claude will analyze deeply:")
        print("- 'I need a peer-to-peer lending marketplace'")
        print("- 'Build a food delivery platform'")
        print("- 'Create a real estate marketplace'")
        print("- 'Design a fitness tracking app'")
        print("- 'Build a cryptocurrency exchange'")
        print("- 'Create a social media platform'")
        print("- 'Design a healthcare telemedicine system'")
        print("- 'Build a project management tool'")
        print("\nClaude will automatically analyze the domain and create comprehensive schemas!")
        print("Claude can create both DynamoDB tables and MongoDB collections!")
        print("Type 'quit' to exit")
        
        try:
            prompt = input("\n🎯 Your request: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not prompt:
                print("❌ Please enter a request!")
                continue
            
            run_claude_request(prompt)
            
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()