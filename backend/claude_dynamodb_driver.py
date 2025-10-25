#!/usr/bin/env python3
"""
Claude-Driven DynamoDB Function Service
Functions that Claude can call to manage DynamoDB operations
"""

import boto3  # type: ignore
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from loguru import logger  # type: ignore

class ClaudeDynamoDBDriver:
    """DynamoDB functions that Claude can call"""
    
    def __init__(self):
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        self.dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    def create_table_simple(self, table_name: str, primary_key: str, database_name: str = None) -> Dict[str, Any]:
        """
        Create a simple DynamoDB table with HASH key only
        Claude can call this for basic table creation
        """
        try:
            full_table_name = f"{database_name}_{table_name}" if database_name else table_name
            
            response = self.dynamodb.create_table(
                TableName=full_table_name,
                KeySchema=[{'AttributeName': primary_key, 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': primary_key, 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'ClaudeDriver'},
                    {'Key': 'CreatedAt', 'Value': datetime.now().isoformat()}
                ]
            )
            
            return {
                "success": True,
                "table_name": full_table_name,
                "status": "CREATING",
                "message": f"Table {full_table_name} created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create table {table_name}"
            }
    
    def create_table_advanced(self, table_schema: Dict[str, Any], database_name: str = None) -> Dict[str, Any]:
        """
        Create DynamoDB table with advanced features (GSI, LSI, composite keys)
        Claude can call this with complex schemas
        """
        try:
            # Add database prefix to table name
            original_name = table_schema['TableName']
            full_table_name = f"{database_name}_{original_name}" if database_name else original_name
            table_schema['TableName'] = full_table_name
            
            # Add tags
            if 'Tags' not in table_schema:
                table_schema['Tags'] = []
            table_schema['Tags'].extend([
                {'Key': 'ManagedBy', 'Value': 'ClaudeDriver'},
                {'Key': 'CreatedAt', 'Value': datetime.now().isoformat()},
                {'Key': 'OriginalName', 'Value': original_name}
            ])
            
            response = self.dynamodb.create_table(**table_schema)
            
            return {
                "success": True,
                "table_name": full_table_name,
                "status": response['TableDescription']['TableStatus'],
                "message": f"Advanced table {full_table_name} created successfully",
                "schema": table_schema
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create advanced table {original_name}"
            }
    
    def create_multiple_tables(self, schemas: List[Dict[str, Any]], database_name: str) -> Dict[str, Any]:
        """
        Create multiple tables at once
        Claude can call this with a list of table schemas
        """
        results = []
        successful_tables = []
        failed_tables = []
        
        for schema in schemas:
            if 'KeySchema' in schema and len(schema.get('GlobalSecondaryIndexes', [])) > 0:
                # Advanced schema
                result = self.create_table_advanced(schema, database_name)
            else:
                # Simple schema - convert to advanced format
                advanced_schema = {
                    'TableName': schema['TableName'],
                    'KeySchema': schema.get('KeySchema', [{'AttributeName': 'id', 'KeyType': 'HASH'}]),
                    'AttributeDefinitions': schema.get('AttributeDefinitions', [{'AttributeName': 'id', 'AttributeType': 'S'}]),
                    'BillingMode': schema.get('BillingMode', 'PAY_PER_REQUEST'),
                    'ProvisionedThroughput': schema.get('ProvisionedThroughput'),
                    'GlobalSecondaryIndexes': schema.get('GlobalSecondaryIndexes', []),
                    'LocalSecondaryIndexes': schema.get('LocalSecondaryIndexes', [])
                }
                result = self.create_table_advanced(advanced_schema, database_name)
            
            results.append(result)
            if result['success']:
                successful_tables.append(result['table_name'])
            else:
                failed_tables.append(result)
        
        return {
            "success": len(failed_tables) == 0,
            "total_tables": len(schemas),
            "successful_tables": successful_tables,
            "failed_tables": failed_tables,
            "results": results,
            "message": f"Created {len(successful_tables)}/{len(schemas)} tables successfully"
        }
    
    def execute_transaction(self, transaction_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute DynamoDB transaction (atomic operations)
        Claude can call this for financial transactions
        """
        try:
            response = self.dynamodb.transact_write_items(
                TransactItems=transaction_items
            )
            
            return {
                "success": True,
                "message": "Transaction executed successfully",
                "transaction_id": response.get('ConsumedCapacity', {}),
                "items_processed": len(transaction_items)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Transaction failed",
                "items_attempted": len(transaction_items)
            }
    
    def query_table(self, table_name: str, key_condition_expression: str = None, 
                   filter_expression: str = None, expression_attribute_values: Dict = None,
                   index_name: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Query DynamoDB table with complex conditions
        Claude can call this for analytics queries
        """
        try:
            query_params = {
                'TableName': table_name
            }
            
            if key_condition_expression:
                query_params['KeyConditionExpression'] = key_condition_expression
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            if expression_attribute_values:
                query_params['ExpressionAttributeValues'] = expression_attribute_values
            if index_name:
                query_params['IndexName'] = index_name
            if limit:
                query_params['Limit'] = limit
            
            response = self.dynamodb.query(**query_params)
            
            return {
                "success": True,
                "items": response['Items'],
                "count": response['Count'],
                "scanned_count": response['ScannedCount'],
                "message": f"Query returned {response['Count']} items"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Query failed on table {table_name}"
            }
    
    def scan_table(self, table_name: str, filter_expression: str = None,
                  expression_attribute_values: Dict = None, limit: int = None) -> Dict[str, Any]:
        """
        Scan DynamoDB table with filters
        Claude can call this for broad searches
        """
        try:
            scan_params = {
                'TableName': table_name
            }
            
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            if expression_attribute_values:
                scan_params['ExpressionAttributeValues'] = expression_attribute_values
            if limit:
                scan_params['Limit'] = limit
            
            response = self.dynamodb.scan(**scan_params)
            
            return {
                "success": True,
                "items": response['Items'],
                "count": response['Count'],
                "scanned_count": response['ScannedCount'],
                "message": f"Scan returned {response['Count']} items"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Scan failed on table {table_name}"
            }
    
    def put_item(self, table_name: str, item: Dict[str, Any], 
                condition_expression: str = None) -> Dict[str, Any]:
        """
        Put item in DynamoDB table
        Claude can call this for data insertion
        """
        try:
            put_params = {
                'TableName': table_name,
                'Item': item
            }
            
            if condition_expression:
                put_params['ConditionExpression'] = condition_expression
            
            response = self.dynamodb.put_item(**put_params)
            
            return {
                "success": True,
                "message": f"Item inserted into {table_name}",
                "attributes": response.get('Attributes', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to insert item into {table_name}"
            }
    
    def batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Batch write items to DynamoDB table
        Claude can call this for bulk operations
        """
        try:
            # DynamoDB batch_write_item can handle up to 25 items
            batch_items = []
            for item in items:
                batch_items.append({
                    'PutRequest': {'Item': item}
                })
            
            response = self.dynamodb.batch_write_item(
                RequestItems={
                    table_name: batch_items
                }
            )
            
            return {
                "success": True,
                "items_processed": len(items),
                "unprocessed_items": response.get('UnprocessedItems', {}),
                "message": f"Batch write completed for {table_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Batch write failed for {table_name}"
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a DynamoDB table
        Claude can call this to understand table structure
        """
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            table_info = response['Table']
            
            return {
                "success": True,
                "table_name": table_info['TableName'],
                "status": table_info['TableStatus'],
                "item_count": table_info.get('ItemCount', 0),
                "key_schema": table_info['KeySchema'],
                "attribute_definitions": table_info['AttributeDefinitions'],
                "global_secondary_indexes": table_info.get('GlobalSecondaryIndexes', []),
                "local_secondary_indexes": table_info.get('LocalSecondaryIndexes', []),
                "billing_mode": table_info.get('BillingModeSummary', {}).get('BillingMode', 'UNKNOWN'),
                "creation_date": table_info['CreationDateTime'].isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get info for table {table_name}"
            }
    
    def list_all_tables(self) -> Dict[str, Any]:
        """
        List all DynamoDB tables
        Claude can call this to see available tables
        """
        try:
            response = self.dynamodb.list_tables()
            
            return {
                "success": True,
                "tables": response['TableNames'],
                "count": len(response['TableNames']),
                "message": f"Found {len(response['TableNames'])} tables"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list tables"
            }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """
        Validate AWS credentials
        Claude can call this to check connection
        """
        try:
            self.dynamodb.list_tables()
            return {
                "success": True,
                "message": "AWS credentials are valid",
                "region": os.getenv('AWS_REGION', 'us-east-1')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "AWS credentials are invalid"
            }

# Global instance for Claude to use
claude_dynamodb = ClaudeDynamoDBDriver()

# Function registry for Claude
FUNCTION_REGISTRY = {
    "create_table_simple": claude_dynamodb.create_table_simple,
    "create_table_advanced": claude_dynamodb.create_table_advanced,
    "create_multiple_tables": claude_dynamodb.create_multiple_tables,
    "execute_transaction": claude_dynamodb.execute_transaction,
    "query_table": claude_dynamodb.query_table,
    "scan_table": claude_dynamodb.scan_table,
    "put_item": claude_dynamodb.put_item,
    "batch_write_items": claude_dynamodb.batch_write_items,
    "get_table_info": claude_dynamodb.get_table_info,
    "list_all_tables": claude_dynamodb.list_all_tables,
    "validate_credentials": claude_dynamodb.validate_credentials
}

def call_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """
    Main function that Claude can call to execute DynamoDB operations
    """
    if function_name not in FUNCTION_REGISTRY:
        return {
            "success": False,
            "error": f"Unknown function: {function_name}",
            "available_functions": list(FUNCTION_REGISTRY.keys())
        }
    
    try:
        result = FUNCTION_REGISTRY[function_name](**kwargs)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Function {function_name} failed"
        }

if __name__ == "__main__":
    # Test the functions
    print("🧪 Testing Claude DynamoDB Driver Functions...")
    
    # Test credentials
    result = call_function("validate_credentials")
    print(f"Credentials: {result}")
    
    # Test listing tables
    result = call_function("list_all_tables")
    print(f"Tables: {result}")
