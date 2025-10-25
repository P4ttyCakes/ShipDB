#!/usr/bin/env python3
"""
Simple Claude API Test
Debug the API integration issue
"""

import os
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append('backend')

from claude_api_client import create_claude_dynamodb_session

def test_simple_claude_request():
    """Test a simple Claude request to debug API issues"""
    
    print("🔍 Simple Claude API Test")
    print("=" * 40)
    
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create Claude client
    api_key = "your_claude_api_key"
    claude_client = create_claude_dynamodb_session(api_key)
    
    # Simple test message
    test_message = """
    Please validate AWS credentials and list all tables.
    Use the available DynamoDB functions to do this.
    """
    
    print("📤 Sending simple request to Claude...")
    
    try:
        response = claude_client.send_message(test_message)
        
        print(f"Response status: {response}")
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            
            # Try to get more details
            if hasattr(response, 'text'):
                print(f"Response text: {response.text}")
            
            return False
        
        print("✅ Claude response received")
        
        # Process any function calls
        processed = claude_client.process_claude_response(response)
        
        print(f"\n📊 Function Results ({len(processed['function_results'])} calls):")
        for i, result in enumerate(processed["function_results"], 1):
            print(f"{i}. Function: {result['function']}")
            print(f"   Result: {json.dumps(result['result'], indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_claude_request()
