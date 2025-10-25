#!/usr/bin/env python3
"""
Basic Claude API Test (No Function Calling)
Test basic API connectivity first
"""

import os
import json
import sys
import requests

def test_basic_claude_api():
    """Test basic Claude API without function calling"""
    
    print("🔍 Basic Claude API Test (No Function Calling)")
    print("=" * 50)
    
    api_key = "your_claude_api_key"
    
    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Can you help me design a DynamoDB schema for a social media platform?"
            }
        ]
    }
    
    print("📤 Sending basic request to Claude...")
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Claude response received!")
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_claude_api()
