#!/usr/bin/env python3

import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_agent import AIAgentService

def test_json_parsing():
    """Test if AI is returning proper JSON that can be parsed"""
    print("🔍 Testing AI JSON Parsing...")
    
    try:
        agent = AIAgentService()
        
        # Test with a simple scenario
        session_response = agent.start_session('Simple e-commerce store')
        session_id = session_response['session_id']
        print(f"✅ Session started: {session_id}")
        
        # First turn
        print("\n📝 First turn...")
        response1 = agent.next_turn(session_id, 'customers and products')
        print("Response 1:")
        print(json.dumps(response1, indent=2))
        
        # Check if response1 is valid
        if not isinstance(response1, dict):
            print("❌ PROBLEM: Response1 is not a dict!")
            return
        
        if 'prompt' not in response1 or 'done' not in response1:
            print("❌ PROBLEM: Response1 missing required keys!")
            return
        
        # Second turn
        print("\n📝 Second turn...")
        response2 = agent.next_turn(session_id, 'orders with multiple products')
        print("Response 2:")
        print(json.dumps(response2, indent=2))
        
        # Check if response2 is valid
        if not isinstance(response2, dict):
            print("❌ PROBLEM: Response2 is not a dict!")
            return
        
        if 'prompt' not in response2 or 'done' not in response2:
            print("❌ PROBLEM: Response2 missing required keys!")
            return
        
        # Third turn - trigger completion
        print("\n📝 Third turn...")
        response3 = agent.next_turn(session_id, 'that covers everything')
        print("Response 3:")
        print(json.dumps(response3, indent=2))
        
        # Check if response3 is valid
        if not isinstance(response3, dict):
            print("❌ PROBLEM: Response3 is not a dict!")
            return
        
        if 'prompt' not in response3 or 'done' not in response3:
            print("❌ PROBLEM: Response3 missing required keys!")
            return
        
        # Check if we have a complete spec
        if response3.get('done') and response3.get('partial_spec'):
            spec = response3['partial_spec']
            print(f"\n🎯 Complete spec generated!")
            print(f"App type: {spec.get('app_type')}")
            print(f"DB type: {spec.get('db_type')}")
            print(f"Entities: {len(spec.get('entities', []))}")
            
            # Try to validate the spec
            try:
                from app.services.schema_generator import validate_spec
                ok, errors = validate_spec(spec)
                if ok:
                    print("✅ Spec validation passed")
                else:
                    print(f"❌ Spec validation failed: {errors}")
            except Exception as e:
                print(f"❌ Spec validation error: {e}")
        else:
            print("❌ PROBLEM: No complete spec generated!")
            print(f"Done: {response3.get('done')}")
            print(f"Partial spec: {response3.get('partial_spec')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_json_parsing()
