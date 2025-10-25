#!/usr/bin/env python3
"""
Test Claude API with different model names
"""

import os
from anthropic import Anthropic

def test_model_names():
    """Test different Claude model names"""
    
    api_key = "your_claude_api_key"
    client = Anthropic(api_key=api_key)
    
    # Try different model names
    model_names = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet",
        "claude-3-sonnet-20240229",
        "claude-3-sonnet",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307"
    ]
    
    for model in model_names:
        try:
            print(f"Testing model: {model}")
            response = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )
            print(f"✅ {model} works!")
            print(f"Response: {response.content[0].text[:100]}...")
            return model
        except Exception as e:
            print(f"❌ {model} failed: {e}")
    
    return None

if __name__ == "__main__":
    working_model = test_model_names()
    if working_model:
        print(f"\n🎉 Working model found: {working_model}")
    else:
        print("\n💥 No working model found")
