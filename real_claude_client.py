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
from claude_mongodb_driver import call_mongodb_function, MONGODB_FUNCTION_REGISTRY  # type: ignore

class RealClaudeAPIClient:
    """Real Claude API client using official Anthropic library"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.api_key = api_key
    
    def create_function_tools(self) -> List[Dict[str, Any]]:
        """Create function tool definitions for Claude"""
        tools = []

        # MongoDB function definitions - Enhanced with complex operations
        mongodb_functions = {
            "create_collection_simple": {
                "name": "create_collection_simple",
                "description": "Create a simple MongoDB collection with basic indexes",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {"type": "string", "description": "Name of the collection"},
                        "indexes": {"type": "array", "items": {"type": "string"}, "description": "List of index fields"},
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["collection_name", "indexes"]
                }
            },
            "create_collection_advanced": {
                "name": "create_collection_advanced",
                "description": "Create MongoDB collection with advanced features (compound indexes, unique constraints, sparse indexes, TTL, text search, geospatial)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_schema": {
                            "type": "object",
                            "description": "Complete MongoDB collection schema with compound indexes, unique constraints, sparse indexes, text search, TTL indexes"
                        },
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["collection_schema"]
                }
            },
            "create_index": {
                "name": "create_index",
                "description": "Create a specific index on an existing MongoDB collection (compound, unique, sparse, text, geospatial, TTL)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {"type": "string", "description": "Name of the collection"},
                        "index_definition": {
                            "type": "object",
                            "description": "Complex index definition with keys, name, unique, sparse, ttl, text, 2dsphere, etc."
                        },
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["collection_name", "index_definition"]
                }
            },
            "query_collection": {
                "name": "query_collection",
                "description": "Advanced MongoDB query with aggregation pipeline, filters, sorting, projection, pagination, and analytics",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {"type": "string", "description": "Name of the collection to query"},
                        "query": {"type": "object", "description": "MongoDB query filter with advanced operators"},
                        "projection": {"type": "object", "description": "Fields to include/exclude in results"},
                        "sort": {"type": "object", "description": "Sort specification"},
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"},
                        "limit": {"type": "integer", "description": "Maximum number of documents to return"},
                        "skip": {"type": "integer", "description": "Number of documents to skip for pagination"}
                    },
                    "required": ["collection_name", "query"]
                }
            },
            "insert_document": {
                "name": "insert_document",
                "description": "Insert a single document into MongoDB collection",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "collection_name": {"type": "string", "description": "Name of the collection"},
                        "document": {"type": "object", "description": "Document to insert"},
                        "database_name": {"type": "string", "description": "Database name prefix (optional)"}
                    },
                    "required": ["collection_name", "document"]
                }
            },
            "list_collections": {
                "name": "list_collections",
                "description": "List all collections in a MongoDB database with metadata",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "database_name": {"type": "string", "description": "Database name (optional)"}
                    },
                    "required": []
                }
            }
        }
        

        
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
        for func_name, func_def in mongodb_functions.items():
            tools.append(func_def)
        
        for func_name, func_def in dynamodb_functions.items():
            tools.append(func_def)
        
        return tools
    
    def send_message(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """Send message to Claude with function calling enabled"""
        
        tools = self.create_function_tools()
        
        # Enhanced system prompt - Concise, intricate, and complex
        enhanced_system_prompt = """
        You are an elite database architect orchestrating sophisticated, production-grade systems. Execute:

        🔬 ANALYTICAL RIGOR:
        Deconstruct domains into: business model anatomy → stakeholder ecosystems → transactional workflows → regulatory compliance → relationship topologies → query optimization patterns

        🏛️ ARCHITECTURAL EXCELLENCE:
        • Production-ready schemas with: ACID guarantees, referential integrity, audit trails, business logic constraints
        • Scalability: sharding strategies, index optimization, query performance profiling
        • Operational excellence: disaster recovery, data archival, monitoring instrumentation
        • Security: multi-layer authentication, encryption at rest/transit, compliance frameworks

        🎯 MONGODB INTELLIGENCE:
        Collections require:
        - Strategic indexing: compound indexes on query patterns, unique constraints on business keys, sparse indexes for optional fields
        - Text search: full-text indexes with language-specific stemming
        - Geospatial: 2dsphere indexes for location-based queries
        - TTL indexes: automatic document expiration for temporary data
        - Aggregation pipelines: complex joins via $lookup, data transformation, analytics pipelines
        - Transactions: multi-document ACID operations for consistency
        - Change streams: real-time event sourcing for microservices architectures

        🗄️ DYNAMODB MASTERY:
        Tables require:
        - Key design: HASH/RANGE patterns, GSI/LSI for query patterns, projection optimization
        - Access patterns: item access vs. query vs. scan optimization
        - Transactional integrity: conditional writes, optimistic locking
        - Streams: CDC for event-driven architectures
        - Performance: provisioned vs on-demand, autoscaling, DAX caching

        ⚡ EXECUTION MANIFESTO:
        MongoDB: Use create_collection_advanced with complex index definitions (compound, unique, sparse, text, geospatial, TTL).
        DynamoDB: Use create_table_advanced with complete schemas (KeySchema, AttributeDefinitions, GSI/LSI).

        Think architecturally. Build systems that handle millions of users, petabytes of data, sub-millisecond queries, 99.99% uptime.
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
        # Check if it's a MongoDB function
        if function_name in MONGODB_FUNCTION_REGISTRY:
            return call_mongodb_function(function_name, **parameters)
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
