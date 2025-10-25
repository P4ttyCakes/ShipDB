#!/usr/bin/env python3
"""
Real Claude API Integration for DynamoDB Function Calling
Uses the official Anthropic library for proper function calling
"""

import os
import json
import sys
from pathlib import Path
from anthropic import Anthropic  # type: ignore
from typing import Dict, List, Any, Optional

# Add the backend directory to Python path
sys.path.append('backend')

from claude_dynamodb_driver import call_function, FUNCTION_REGISTRY  # type: ignore

class RealClaudeAPIClient:
    """Real Claude API client using official Anthropic library"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.api_key = api_key
    
    def create_function_tools(self) -> List[Dict[str, Any]]:
        """Create function tool definitions for Claude"""
        tools = []
        
        # DynamoDB function definitions
        dynamodb_functions = {
            "create_table_simple": {
                "name": "create_table_simple",
                "description": "Create a simple DynamoDB table with HASH key only",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "primary_key": {"type": "string", "description": "Primary key attribute name"},
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["table_name", "primary_key"]
                }
            },
            "create_table_advanced": {
                "name": "create_table_advanced", 
                "description": "Create DynamoDB table with advanced features (GSI, LSI, composite keys)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_schema": {
                            "type": "object",
                            "description": "Complete DynamoDB table schema with KeySchema, AttributeDefinitions, etc."
                        },
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["table_schema"]
                }
            },
            "execute_transaction": {
                "name": "execute_transaction",
                "description": "Execute DynamoDB transaction (atomic operations) for financial transactions",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "transaction_items": {
                            "type": "array",
                            "description": "List of transaction items (Put, Update, Delete operations)",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["transaction_items"]
                }
            },
            "query_table": {
                "name": "query_table",
                "description": "Query DynamoDB table with complex conditions for analytics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to query"},
                        "key_condition_expression": {"type": "string", "description": "Key condition expression"},
                        "filter_expression": {"type": "string", "description": "Filter expression"},
                        "expression_attribute_values": {"type": "object", "description": "Expression attribute values"},
                        "index_name": {"type": "string", "description": "GSI or LSI name to use"},
                        "limit": {"type": "integer", "description": "Maximum number of items to return"}
                    },
                    "required": ["table_name"]
                }
            },
            "scan_table": {
                "name": "scan_table",
                "description": "Scan DynamoDB table with filters for broad searches",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table to scan"},
                        "filter_expression": {"type": "string", "description": "Filter expression"},
                        "expression_attribute_values": {"type": "object", "description": "Expression attribute values"},
                        "limit": {"type": "integer", "description": "Maximum number of items to return"}
                    },
                    "required": ["table_name"]
                }
            },
            "put_item": {
                "name": "put_item",
                "description": "Put item in DynamoDB table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "item": {"type": "object", "description": "Item to insert"},
                        "condition_expression": {"type": "string", "description": "Condition expression (optional)"}
                    },
                    "required": ["table_name", "item"]
                }
            },
            "batch_write_items": {
                "name": "batch_write_items",
                "description": "Batch write items to DynamoDB table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"},
                        "items": {
                            "type": "array",
                            "description": "List of items to write",
                            "items": {"type": "object"}
                        }
                    },
                    "required": ["table_name", "items"]
                }
            },
            "get_table_info": {
                "name": "get_table_info",
                "description": "Get detailed information about a DynamoDB table",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string", "description": "Name of the table"}
                    },
                    "required": ["table_name"]
                }
            },
            "list_all_tables": {
                "name": "list_all_tables",
                "description": "List all DynamoDB tables",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "validate_credentials": {
                "name": "validate_credentials",
                "description": "Validate AWS credentials",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        # Convert to Claude tool format
        for func_name, func_def in dynamodb_functions.items():
            tools.append(func_def)
        
        return tools
    
    def send_message(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Send message to Claude with function calling enabled"""
        
        tools = self.create_function_tools()
        
        # Enhanced system prompt for deep analysis
        enhanced_system_prompt = """
        You are a senior database architect and domain expert with deep business intelligence. When given ANY request to build a database system, you must:

        🔍 DEEP DOMAIN ANALYSIS PROCESS:
        1. ANALYZE THE BUSINESS MODEL: Understand the core business, revenue streams, user types, and value propositions
        2. IDENTIFY STAKEHOLDERS: Who are the users, admins, partners, regulators, and third-party integrations?
        3. MAP USER JOURNEYS: Trace complete user workflows from onboarding to core operations to offboarding
        4. IDENTIFY BUSINESS PROCESSES: What are the key operations, transactions, and business rules?
        5. CONSIDER REGULATORY REQUIREMENTS: What compliance, audit, and legal requirements exist?
        6. ANALYZE DATA RELATIONSHIPS: How do entities connect? What are the cardinalities and dependencies?
        7. IDENTIFY PERFORMANCE PATTERNS: What are the common queries, search patterns, and analytics needs?

        🏗️ COMPREHENSIVE SCHEMA DESIGN:
        - Design for REAL BUSINESS OPERATIONS, not just basic CRUD
        - Include ALL necessary tables for a production system
        - Consider edge cases, error handling, and data integrity
        - Design for scalability, performance, and maintainability
        - Include proper indexes for common query patterns
        - Consider data archival, backup, and recovery needs

        🎯 DOMAIN-SPECIFIC INTELLIGENCE:
        For ANY domain, think deeply about:
        - User management (roles, permissions, authentication, profiles)
        - Core business entities and their lifecycle
        - Transaction processing and financial flows
        - Communication and notification systems
        - Analytics, reporting, and business intelligence
        - Audit trails and compliance tracking
        - Integration points with external systems
        - Performance optimization and caching needs
        - Security, privacy, and data protection
        - Error handling and system monitoring

        📋 SCHEMA REQUIREMENTS:
        Each table MUST include:
        - TableName (descriptive and clear)
        - KeySchema (HASH and RANGE keys where appropriate)
        - AttributeDefinitions (all attributes used in keys and indexes)
        - GlobalSecondaryIndexes (for performance optimization)
        - BillingMode: "PROVISIONED"
        - ProvisionedThroughput: {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}

        ⚡ EXECUTION INSTRUCTIONS:
        - Use create_table_advanced for EACH table individually
        - Generate complete, production-ready schemas
        - Create multiple tables by calling create_table_advanced multiple times
        - Be thorough - include ALL tables a real business would need
        - Think like you're building a system that will handle millions of users and transactions

        🧠 EXAMPLES OF DEEP THINKING:
        For "peer-to-peer lending marketplace":
        - Borrowers (credit scoring, verification, loan applications)
        - Lenders (investment preferences, risk tolerance, portfolio management)
        - Loans (terms, interest rates, repayment schedules, status tracking)
        - Transactions (payments, fees, escrow, settlements)
        - Credit assessments (scoring models, verification data, risk analysis)
        - Compliance (regulatory reporting, audit trails, KYC/AML)
        - Communication (notifications, messaging, dispute resolution)
        - Analytics (performance metrics, risk analysis, market trends)

        Always think beyond the obvious and create systems that could actually run a real business at scale.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                tools=tools,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            return {
                "success": True,
                "response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_function_call(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return the result"""
        return call_function(function_name, **parameters)
    
    def process_claude_response(self, claude_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process Claude's response and execute any function calls"""
        results = []
        
        if claude_response["success"]:
            response = claude_response["response"]
            
            for content_item in response.content:
                if content_item.type == "tool_use":
                    # Claude wants to call a function
                    function_name = content_item.name
                    parameters = content_item.input
                    
                    # Execute the function
                    result = self.execute_function_call(function_name, parameters)
                    
                    results.append({
                        "function": function_name,
                        "parameters": parameters,
                        "result": result
                    })
        
        return {
            "claude_response": claude_response,
            "function_results": results,
            "success": len(results) > 0
        }

def create_real_claude_session(api_key: str) -> RealClaudeAPIClient:
    """Create a real Claude API client for DynamoDB operations"""
    return RealClaudeAPIClient(api_key)

# Example usage
if __name__ == "__main__":
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create Claude client
    api_key = "your_claude_api_key"
    claude_client = create_real_claude_session(api_key)
    
    # Test message
    test_message = """
    I need you to create a social media platform database in DynamoDB. Please:
    
    1. First validate that AWS credentials are working
    2. List all existing tables to see what's already there
    3. Create a comprehensive social media database with tables for users, posts, follows, likes, comments, and messages
    4. Make sure to include proper GSI indexes for performance
    5. Add some sample data to demonstrate the system
    
    Use the available DynamoDB functions to accomplish this step by step.
    """
    
    system_prompt = """
    You are a senior database architect specializing in social media platforms. You have access to DynamoDB functions that you can call to:
    - Create simple and advanced tables with GSI/LSI
    - Execute transactions for atomic operations
    - Query and scan data for complex operations
    - Manage multiple tables and relationships
    
    Always use the available functions to accomplish DynamoDB tasks. Be thorough and explain what you're doing.
    When creating advanced tables, make sure to include proper AttributeDefinitions for all keys and indexes.
    Design for scalability and performance with appropriate GSI/LSI.
    """
    
    print("🤖 Sending message to Claude...")
    response = claude_client.send_message(test_message, system_prompt)
    
    if not response["success"]:
        print(f"❌ Error: {response['error']}")
    else:
        print("✅ Claude response received")
        
        # Process any function calls
        processed = claude_client.process_claude_response(response)
        
        print(f"\n📊 Function Results ({len(processed['function_results'])} calls):")
        for result in processed["function_results"]:
            print(f"Function: {result['function']}")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
            print("-" * 50)
