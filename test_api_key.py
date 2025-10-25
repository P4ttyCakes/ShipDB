#!/usr/bin/env python3
"""
Quick test script to verify Anthropic API key is working
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.config import settings
    from app.services.ai_agent import AIAgent
    
    print("🚢 Testing ShipDB API Configuration")
    print("=" * 40)
    
    # Check if API key is configured
    api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not configured!")
        print("   Please run: ./setup_api_key.sh")
        sys.exit(1)
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    print(f"✅ Model: {getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-haiku-20240307')}")
    
    # Test AI agent initialization
    try:
        agent = AIAgent()
        print("✅ AI Agent initialized successfully")
        
        # Test a simple session
        print("\n🧪 Testing AI conversation...")
        result = agent.start_session("Test Rental Property", "Rental property management system")
        print(f"✅ AI Response: {result.get('prompt', 'No response')[:100]}...")
        
        print("\n🎉 All tests passed! ShipDB is ready to use.")
        
    except Exception as e:
        print(f"❌ AI Agent test failed: {e}")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the ShipDB root directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)
