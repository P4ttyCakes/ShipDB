#!/usr/bin/env python3
"""
Comprehensive test suite for the improved conversation completion functionality.
Tests various scenarios to ensure the AI agent properly detects conversation completion.
"""

import os
import sys
import json
import time
from pathlib import Path

# Change to backend directory to ensure .env is loaded correctly
backend_path = Path(__file__).parent / "backend"
os.chdir(backend_path)
sys.path.insert(0, str(backend_path))

from app.services.ai_agent import AIAgentService

class ConversationTester:
    def __init__(self):
        self.agent = AIAgentService()
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results."""
        print(f"\n🧪 Running: {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.test_results.append({"test": test_name, "status": "PASSED"})
            else:
                print(f"❌ FAILED: {test_name}")
                self.test_results.append({"test": test_name, "status": "FAILED"})
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})
    
    def test_completion_phrase_detection(self):
        """Test that completion phrases are properly detected."""
        completion_phrases = [
            "Perfect! I have enough information to create your database design.",
            "Great! I now have everything I need to design your database.",
            "Excellent! Based on what you've told me, I can create your database schema.",
            "I have enough information to create a complete database design.",
            "I can create your database schema now.",
            "Ready to design your database with the information provided.",
            "I have everything I need to design your database."
        ]
        
        non_completion_phrases = [
            "What type of users will be using this system?",
            "Can you tell me more about your business requirements?",
            "I need to understand your data better before proceeding.",
            "Let me ask a few more questions about your project."
        ]
        
        # Test completion phrases
        for phrase in completion_phrases:
            if not self.agent._detect_completion_phrases(phrase):
                print(f"❌ Failed to detect completion phrase: {phrase[:50]}...")
                return False
        
        # Test non-completion phrases
        for phrase in non_completion_phrases:
            if self.agent._detect_completion_phrases(phrase):
                print(f"❌ False positive for non-completion phrase: {phrase[:50]}...")
                return False
        
        print("✅ All completion phrase detection tests passed")
        return True
    
    def test_entity_generation(self):
        """Test that entities are generated correctly for different business types."""
        test_cases = [
            {
                "name": "Real Estate",
                "history": [
                    {"role": "user", "content": "I want to build a real estate platform"},
                    {"role": "assistant", "content": "What type of properties will you list?"},
                    {"role": "user", "content": "Residential properties with bedrooms, bathrooms, and price"}
                ],
                "answer": "We need to track property details",
                "expected_entities": ["properties", "users"]
            },
            {
                "name": "E-commerce",
                "history": [
                    {"role": "user", "content": "I want to build an online store"},
                    {"role": "assistant", "content": "What products will you sell?"},
                    {"role": "user", "content": "Electronics and accessories"}
                ],
                "answer": "We need inventory management",
                "expected_entities": ["products", "users"]
            }
        ]
        
        for test_case in test_cases:
            entities = self.agent._generate_basic_entities_from_context(
                test_case["history"], 
                test_case["answer"]
            )
            
            entity_names = [entity['name'] for entity in entities]
            if not all(name in entity_names for name in test_case["expected_entities"]):
                print(f"❌ {test_case['name']}: Expected {test_case['expected_entities']}, got {entity_names}")
                return False
            
            print(f"✅ {test_case['name']}: Generated {len(entities)} entities correctly")
        
        return True
    
    def test_conversation_flow_real_estate(self):
        """Test a complete conversation flow for a real estate platform."""
        print("Testing Real Estate Platform conversation...")
        
        # Start session
        result = self.agent.start_session("Real Estate Platform", "A platform for buying and selling properties")
        session_id = result["session_id"]
        print(f"Session started: {session_id}")
        print(f"Initial prompt: {result['prompt']}")
        
        # First turn
        result = self.agent.next_turn(session_id, "We need to track properties with bedrooms, bathrooms, price, and location. Users can be buyers or sellers.")
        print(f"Turn 1 - Done: {result['done']}, Prompt: {result['prompt'][:100]}...")
        
        # Second turn
        result = self.agent.next_turn(session_id, "We also need to track user favorites and property views for analytics.")
        print(f"Turn 2 - Done: {result['done']}, Prompt: {result['prompt'][:100]}...")
        
        # Third turn (should trigger completion)
        result = self.agent.next_turn(session_id, "That covers all our main requirements. We want to use PostgreSQL for reliability.")
        print(f"Turn 3 - Done: {result['done']}, Prompt: {result['prompt'][:100]}...")
        
        # Check if conversation completed
        if result['done']:
            print("✅ Conversation completed naturally")
            
            # Test finalization
            final_result = self.agent.finalize(session_id)
            spec = final_result['spec']
            
            # Validate spec
            if (spec.get('app_type') and 
                spec.get('db_type') in ['postgresql', 'mongodb', 'dynamodb'] and
                len(spec.get('entities', [])) > 0):
                print("✅ Valid database specification generated")
                print(f"   App type: {spec.get('app_type')}")
                print(f"   DB type: {spec.get('db_type')}")
                print(f"   Entities: {len(spec.get('entities', []))}")
                return True
            else:
                print("❌ Invalid database specification")
                return False
        else:
            print("❌ Conversation did not complete naturally")
            return False
    
    def test_conversation_flow_ecommerce(self):
        """Test a complete conversation flow for an e-commerce platform."""
        print("Testing E-commerce Platform conversation...")
        
        # Start session
        result = self.agent.start_session("E-commerce Store", "An online store for selling products")
        session_id = result["session_id"]
        print(f"Session started: {session_id}")
        
        # First turn
        result = self.agent.next_turn(session_id, "We sell electronics and accessories. Need inventory tracking and order management.")
        print(f"Turn 1 - Done: {result['done']}")
        
        # Second turn
        result = self.agent.next_turn(session_id, "We also need customer accounts, payment processing, and shipping tracking.")
        print(f"Turn 2 - Done: {result['done']}")
        
        # Third turn
        result = self.agent.next_turn(session_id, "That's everything we need. We prefer MongoDB for flexibility.")
        print(f"Turn 3 - Done: {result['done']}")
        
        if result['done']:
            print("✅ E-commerce conversation completed naturally")
            return True
        else:
            print("❌ E-commerce conversation did not complete")
            return False
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("Testing edge cases...")
        
        # Test empty session
        try:
            result = self.agent.start_session("", "")
            if result.get('session_id'):
                print("❌ Should not allow empty session name")
                return False
        except ValueError:
            print("✅ Correctly rejected empty session name")
        
        # Test invalid session ID
        try:
            result = self.agent.next_turn("invalid-session-id", "test answer")
            print("❌ Should not allow invalid session ID")
            return False
        except ValueError:
            print("✅ Correctly rejected invalid session ID")
        
        # Test empty answer
        try:
            result = self.agent.start_session("Test Project", "Test description")
            session_id = result["session_id"]
            result = self.agent.next_turn(session_id, "")
            print("❌ Should not allow empty answer")
            return False
        except ValueError:
            print("✅ Correctly rejected empty answer")
        
        return True
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("🧪 TEST SUMMARY")
        print("="*60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        
        if failed > 0 or errors > 0:
            print("\nFailed/Error Details:")
            for result in self.test_results:
                if result["status"] != "PASSED":
                    print(f"  - {result['test']}: {result['status']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! The conversation completion improvements are working correctly.")
        else:
            print(f"\n⚠️  {failed + errors} test(s) need attention.")

def main():
    """Run all tests."""
    print("🚢 ShipDB Conversation Completion Test Suite")
    print("="*60)
    
    tester = ConversationTester()
    
    # Run all tests
    tester.run_test("Completion Phrase Detection", tester.test_completion_phrase_detection)
    tester.run_test("Entity Generation", tester.test_entity_generation)
    tester.run_test("Real Estate Conversation Flow", tester.test_conversation_flow_real_estate)
    tester.run_test("E-commerce Conversation Flow", tester.test_conversation_flow_ecommerce)
    tester.run_test("Edge Cases", tester.test_edge_cases)
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    main()
