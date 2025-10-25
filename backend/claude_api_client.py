#!/usr/bin/env python3
"""
Claude API Integration for DynamoDB Function Calling
This allows Claude to call DynamoDB functions using the Anthropic API
"""

import os
import json
import requests  # type: ignore
from typing import Dict, List, Any, Optional
from claude_dynamodb_driver import call_function, FUNCTION_REGISTRY

class ClaudeAPIClient:
    """Client for calling Claude API with function calling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    def create_function_tools(self) -> List[Dict[str, Any]]:
        """Create function tool definitions for Claude"""
        tools = []
        
        # DynamoDB function definitions
        dynamodb_functions = {
            "create_table_simple": {
                "name": "create_table_simple",
                "description": "Create a simple DynamoDB table with HASH key only",
                "parameters": {
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
                "parameters": {
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
            "create_multiple_tables": {
                "name": "create_multiple_tables",
                "description": "Create multiple DynamoDB tables at once",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "schemas": {
                            "type": "array",
                            "description": "List of table schemas",
                            "items": {"type": "object"}
                        },
                        "database_name": {"type": "string", "description": "Database name prefix"}
                    },
                    "required": ["schemas", "database_name"]
                }
            },
            "execute_transaction": {
                "name": "execute_transaction",
                "description": "Execute DynamoDB transaction (atomic operations) for financial transactions",
                "parameters": {
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
                "parameters": {
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
                "parameters": {
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
                "parameters": {
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
                "parameters": {
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
                "parameters": {
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
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            "validate_credentials": {
                "name": "validate_credentials",
                "description": "Validate AWS credentials",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
        
        # Convert to Claude tool format
        for func_name, func_def in dynamodb_functions.items():
            tools.append({
                "type": "function",
                "function": func_def
            })
        
        return tools
    
    def send_message(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Send message to Claude with function calling enabled"""
        
        tools = self.create_function_tools()
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "tools": tools,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def execute_function_call(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call and return the result"""
        return call_function(function_name, **parameters)
    
    def process_claude_response(self, claude_response: Dict[str, Any]) -> Dict[str, Any]:
        """Process Claude's response and execute any function calls"""
        results = []
        
        if "content" in claude_response:
            for content_item in claude_response["content"]:
                if content_item["type"] == "tool_use":
                    # Claude wants to call a function
                    function_name = content_item["name"]
                    parameters = content_item["input"]
                    
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

def create_claude_dynamodb_session(api_key: str) -> ClaudeAPIClient:
    """Create a Claude API client for DynamoDB operations"""
    return ClaudeAPIClient(api_key)

# Example usage
if __name__ == "__main__":
    # Set up environment
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_aws_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_aws_secret_key'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    # Create Claude client
    api_key = "your_claude_api_key"
    claude_client = create_claude_dynamodb_session(api_key)
    
    # Test message
    test_message = """
    I need you to create a financial transaction system with the following requirements:
    
    1. Create a table called 'accounts' with account_id as primary key
    2. Create a table called 'transactions' with composite key (account_id, transaction_id) 
    3. Add a GSI to transactions table for querying by date
    4. Validate that AWS credentials are working
    5. List all existing tables
    
    Please use the available DynamoDB functions to accomplish this.
    """
    
    system_prompt = """
    You are a DynamoDB expert assistant. You have access to DynamoDB functions that you can call to:
    - Create simple and advanced tables
    - Execute transactions
    - Query and scan data
    - Manage multiple tables
    
    Always use the available functions to accomplish DynamoDB tasks. Be thorough and explain what you're doing.
    """
    
    print("🤖 Sending message to Claude...")
    response = claude_client.send_message(test_message, system_prompt)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
    else:
        print("✅ Claude response received")
        
        # Process any function calls
        processed = claude_client.process_claude_response(response)
        
        print("\n📊 Function Results:")
        for result in processed["function_results"]:
            print(f"Function: {result['function']}")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
            print("-" * 50)
