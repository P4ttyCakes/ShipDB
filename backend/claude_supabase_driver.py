#!/usr/bin/env python3
"""
Claude-Driven Supabase PostgreSQL Function Service
Functions that Claude can call to manage PostgreSQL operations on Supabase
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

class ClaudeSupabaseDriver:
    """Supabase PostgreSQL functions that Claude can call"""
    
    def __init__(self):
        # Load environment variables from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:
            from supabase import create_client, Client
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except ImportError:
            raise ImportError("supabase-py is not installed. Install it with: pip install supabase")
        
        self.url = supabase_url
    
    def create_table(self, table_schema: str, database_name: str = None) -> Dict[str, Any]:
        """
        Create a PostgreSQL table from SQL schema
        Claude can call this to create tables from CREATE TABLE statements
        """
        try:
            # Execute SQL to create table
            # Note: Supabase uses PostgREST which doesn't support DDL via REST API
            # We'll need to use the Supabase management API or raw SQL execution
            response = self.supabase.rpc('exec_sql', {'query': table_schema}).execute()
            
            return {
                "success": True,
                "message": "Table created successfully",
                "schema": table_schema
            }
            
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create table"
            }
    
    def insert_row(self, table_name: str, row_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a row into a PostgreSQL table
        Claude can call this for data insertion
        """
        try:
            response = self.supabase.table(table_name).insert(row_data).execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Inserted row into {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error inserting row into {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def query_table(self, table_name: str, filters: Dict[str, Any] = None, 
                   columns: str = "*", limit: int = None, offset: int = None) -> Dict[str, Any]:
        """
        Query PostgreSQL table with filters
        Claude can call this for data retrieval and analytics
        """
        try:
            query = self.supabase.table(table_name).select(columns)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            # Apply limit and offset
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            response = query.execute()
            
            return {
                "success": True,
                "table_name": table_name,
                "data": response.data,
                "count": len(response.data) if response.data else 0,
                "message": f"Query returned {len(response.data) if response.data else 0} rows from {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error querying table {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def update_row(self, table_name: str, filters: Dict[str, Any], 
                  update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update rows in PostgreSQL table
        Claude can call this for data updates
        """
        try:
            query = self.supabase.table(table_name).update(update_data)
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Updated rows in {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error updating {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def delete_row(self, table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete rows from PostgreSQL table
        Claude can call this for data deletion
        """
        try:
            query = self.supabase.table(table_name).delete()
            
            # Apply filters
            for key, value in filters.items():
                query = query.eq(key, value)
            
            response = query.execute()
            
            return {
                "success": True,
                "data": response.data,
                "message": f"Deleted rows from {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error deleting from {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def list_tables(self) -> Dict[str, Any]:
        """
        List all tables in the database
        Claude can call this to see what tables exist
        """
        try:
            # Query information_schema to get table list
            response = self.supabase.table('information_schema.tables').select('table_name').eq('table_schema', 'public').execute()
            
            table_names = [row['table_name'] for row in response.data] if response.data else []
            
            return {
                "success": True,
                "tables": table_names,
                "count": len(table_names),
                "message": f"Found {len(table_names)} tables"
            }
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list tables"
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a table
        Claude can call this to understand table structure
        """
        try:
            # Query information_schema to get column information
            response = self.supabase.rpc('get_table_columns', {'table_name': table_name}).execute()
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": response.data if response.data else [],
                "message": f"Retrieved info for {table_name}"
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def validate_credentials(self) -> Dict[str, Any]:
        """
        Validate Supabase credentials
        Claude can call this to check connection
        """
        try:
            # Try to list tables to validate connection
            self.supabase.table('_').select('*').limit(1).execute()
            return {
                "success": True,
                "message": "Supabase credentials are valid",
                "url": self.url
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Supabase credentials are invalid"
            }

# Global instance for Claude to use
claude_supabase = ClaudeSupabaseDriver()

# Function registry for Claude
SUPABASE_FUNCTION_REGISTRY = {
    "create_table": claude_supabase.create_table,
    "insert_row": claude_supabase.insert_row,
    "query_table": claude_supabase.query_table,
    "update_row": claude_supabase.update_row,
    "delete_row": claude_supabase.delete_row,
    "list_tables": claude_supabase.list_tables,
    "get_table_info": claude_supabase.get_table_info,
    "validate_credentials": claude_supabase.validate_credentials
}

def call_supabase_function(function_name: str, **kwargs) -> Dict[str, Any]:
    """
    Main function that Claude can call to execute Supabase operations
    """
    if function_name not in SUPABASE_FUNCTION_REGISTRY:
        return {
            "success": False,
            "error": f"Unknown Supabase function: {function_name}",
            "available_functions": list(SUPABASE_FUNCTION_REGISTRY.keys())
        }
    
    try:
        result = SUPABASE_FUNCTION_REGISTRY[function_name](**kwargs)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Function {function_name} failed"
        }

if __name__ == "__main__":
    # Test the functions
    print("Testing Claude Supabase Driver Functions...")
    
    # Test credentials
    result = call_supabase_function("validate_credentials")
    print(f"Credentials: {result}")
    
    # Test listing tables
    result = call_supabase_function("list_tables")
    print(f"Tables: {result}")
